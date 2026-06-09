#!/usr/bin/env python3
"""
golden_set_runner.py — run your AI chatbot against a "golden set" (ชุดข้อสอบทอง)
and produce a scored results file you can diff between releases (regression testing).

The golden set is a CSV with columns:
    id, question, expected_points, must_not, category
  - expected_points : ; -separated points a good answer MUST cover
  - must_not        : ; -separated things the answer must NEVER contain (e.g. invented prices)
  - category        : free text, e.g. faq / trap / safety   ("trap" = bot SHOULD say "I don't know")

Plug your real chatbot into `bot_reply()`. Scoring here is a transparent
keyword/coverage heuristic so it runs with zero dependencies; swap in llm_judge.py
for open-ended grading. MIT licensed — adapt freely. (c) KORP AI 2026
"""
import csv, sys, json, time

def bot_reply(question: str) -> str:
    """REPLACE ME with a call to your chatbot (LINE webhook handler, API, etc.)."""
    raise NotImplementedError("Wire bot_reply() to your chatbot endpoint")

def score_row(answer: str, expected_points: str, must_not: str):
    ans = (answer or "").lower()
    pts = [p.strip().lower() for p in expected_points.split(";") if p.strip()]
    bad = [b.strip().lower() for b in must_not.split(";") if b.strip()]
    covered = [p for p in pts if p in ans]
    violations = [b for b in bad if b in ans]
    coverage = (len(covered) / len(pts)) if pts else 1.0
    # any must-not violation hard-fails the row to 0 (e.g. invented price)
    score = 0.0 if violations else round(coverage, 3)
    return score, covered, violations

def run(golden_csv: str, out_path: str = "golden_results.json"):
    rows, scores = [], []
    with open(golden_csv, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            t0 = time.time()
            ans = bot_reply(r["question"])
            latency = round(time.time() - t0, 3)
            s, covered, viol = score_row(ans, r.get("expected_points", ""), r.get("must_not", ""))
            scores.append(s)
            rows.append({"id": r["id"], "category": r.get("category", ""),
                         "score": s, "latency_s": latency,
                         "covered": covered, "violations": viol, "answer": ans})
    overall = round(sum(scores) / len(scores), 3) if scores else 0.0
    hard_fails = [x["id"] for x in rows if x["violations"]]
    report = {"overall_score": overall, "n": len(rows),
              "hard_fail_ids": hard_fails, "rows": rows}
    json.dump(report, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"overall={overall}  n={len(rows)}  hard_fails={len(hard_fails)} -> {out_path}")
    return report

if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "golden_set.csv")
