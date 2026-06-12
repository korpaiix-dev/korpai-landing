#!/usr/bin/env python3
"""faq_sheet_to_jsonl.py — convert an SME FAQ sheet (CSV) into clean JSONL chunks for RAG ingest.

Expected CSV columns: category, question, answer, synonyms (optional), updated_at (YYYY-MM-DD), expires_at (optional)
Validates the "1-1-1 rule" basics while converting:
  - skips empty Q or A
  - drops rows whose expires_at is in the past (stale promos)
  - warns on answers > 1200 chars (likely multi-topic row)
  - warns on dangling references ("ดูด้านบน", "ตามตาราง", "ข้อ 3")
  - dedupes identical normalized questions

Usage: python3 faq_sheet_to_jsonl.py faq.csv > kb.jsonl
Companion to: https://korpai.co/blog/knowledge-base-ai-chatbot-เตรียมข้อมูล-sme-ไทย-2026
MIT license — KORP AI (korpai.co)
"""
import csv, json, re, sys, unicodedata
from datetime import date

DANGLING = ["ดูด้านบน", "ตามตารางด้านบน", "ดังกล่าวข้างต้น", "ดูข้อ ", "see above", "as mentioned above"]

def norm(s: str) -> str:
    s = unicodedata.normalize("NFC", s or "").strip()
    return re.sub(r"[\s​﻿]+", " ", s)

def main(path: str) -> None:
    seen, out_n, warn_n = set(), 0, 0
    today = date.today().isoformat()
    with open(path, newline="", encoding="utf-8-sig") as f:
        for i, row in enumerate(csv.DictReader(f), start=2):
            q, a = norm(row.get("question", "")), norm(row.get("answer", ""))
            if not q or not a:
                print(f"[skip] row {i}: empty question/answer", file=sys.stderr); continue
            exp = norm(row.get("expires_at", ""))
            if exp and exp < today:
                print(f"[skip] row {i}: expired {exp} — {q[:40]}", file=sys.stderr); continue
            key = re.sub(r"[^\wก-๙]", "", q.lower())
            if key in seen:
                print(f"[skip] row {i}: duplicate question — {q[:40]}", file=sys.stderr); continue
            seen.add(key)
            if len(a) > 1200:
                warn_n += 1; print(f"[warn] row {i}: answer {len(a)} chars — split into multiple rows?", file=sys.stderr)
            for d in DANGLING:
                if d in a:
                    warn_n += 1; print(f"[warn] row {i}: dangling reference '{d}' — answer must be self-contained", file=sys.stderr)
            doc = {
                "id": f"faq-{i}",
                "text": f"Q: {q}\nA: {a}",
                "metadata": {
                    "category": norm(row.get("category", "")) or "uncategorized",
                    "synonyms": [s.strip() for s in norm(row.get("synonyms", "")).split("|") if s.strip()],
                    "updated_at": norm(row.get("updated_at", "")) or today,
                    **({"expires_at": exp} if exp else {}),
                },
            }
            print(json.dumps(doc, ensure_ascii=False)); out_n += 1
    print(f"[done] {out_n} chunks written, {warn_n} warnings", file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: faq_sheet_to_jsonl.py faq.csv > kb.jsonl")
    main(sys.argv[1])
