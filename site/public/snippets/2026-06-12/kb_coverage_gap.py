#!/usr/bin/env python3
"""kb_coverage_gap.py — find real customer questions your knowledge base does NOT cover yet.

Input 1: chat log CSV with a 'question' column (export from LINE OA / FB, one first-question per row)
Input 2: kb.jsonl from faq_sheet_to_jsonl.py
Output: clusters of unmatched questions ranked by frequency → your next 5-10 FAQ rows.

No embeddings needed — difflib similarity is enough to triage Thai SME chat logs.
Usage: python3 kb_coverage_gap.py chats.csv kb.jsonl [--threshold 0.62]
Companion to: https://korpai.co/blog/knowledge-base-ai-chatbot-เตรียมข้อมูล-sme-ไทย-2026
MIT license — KORP AI (korpai.co)
"""
import csv, json, re, sys, unicodedata
from difflib import SequenceMatcher

def norm(s: str) -> str:
    s = unicodedata.normalize("NFC", (s or "").lower().strip())
    return re.sub(r"[^\wก-๙]+", "", s)

def sim(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def main(chats_csv: str, kb_jsonl: str, threshold: float) -> None:
    kb = []
    with open(kb_jsonl, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                doc = json.loads(line)
                kb.append(norm(doc.get("text", "").split("\n")[0]))  # the Q: line
                kb += [norm(s) for s in doc.get("metadata", {}).get("synonyms", [])]
    unmatched = []
    with open(chats_csv, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            q = (row.get("question") or "").strip()
            nq = norm(q)
            if not nq or len(nq) < 4: continue
            if max((sim(nq, k) for k in kb), default=0.0) < threshold:
                unmatched.append((nq, q))
    # cluster unmatched questions among themselves
    clusters: list[list[str]] = []
    for nq, q in unmatched:
        for c in clusters:
            if sim(nq, norm(c[0])) >= threshold:
                c.append(q); break
        else:
            clusters.append([q])
    clusters.sort(key=len, reverse=True)
    print(f"unmatched questions: {len(unmatched)} → {len(clusters)} clusters (threshold {threshold})\n")
    print("TOP GAPS — write these FAQ rows first:")
    for i, c in enumerate(clusters[:15], 1):
        print(f"{i:>2}. ({len(c)}x) {c[0]}" + (f"   e.g. also: {c[1][:40]}" if len(c) > 1 else ""))

if __name__ == "__main__":
    if len(sys.argv) < 3: sys.exit("usage: kb_coverage_gap.py chats.csv kb.jsonl [--threshold 0.62]")
    th = float(sys.argv[sys.argv.index("--threshold") + 1]) if "--threshold" in sys.argv else 0.62
    main(sys.argv[1], sys.argv[2], th)
