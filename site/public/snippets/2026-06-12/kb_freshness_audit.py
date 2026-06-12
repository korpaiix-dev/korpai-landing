#!/usr/bin/env python3
"""kb_freshness_audit.py — find knowledge-base entries nobody touched in N days.

Stale KB = bot quoting March promos in June. Run monthly (or in cron) against the
JSONL from faq_sheet_to_jsonl.py. Exit code 1 if stale entries found → easy CI/cron alert.

Usage: python3 kb_freshness_audit.py kb.jsonl --days 60
Cron:  0 9 1 * * python3 kb_freshness_audit.py /srv/kb/kb.jsonl --days 60 || notify-send "KB stale"
Companion to: https://korpai.co/blog/knowledge-base-ai-chatbot-เตรียมข้อมูล-sme-ไทย-2026
MIT license — KORP AI (korpai.co)
"""
import json, sys
from datetime import date, datetime, timedelta

def main(path: str, days: int) -> int:
    cutoff = date.today() - timedelta(days=days)
    stale, expired, total = [], [], 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            total += 1
            doc = json.loads(line)
            meta = doc.get("metadata", {})
            upd = meta.get("updated_at", "")
            exp = meta.get("expires_at", "")
            try:
                if upd and datetime.strptime(upd, "%Y-%m-%d").date() < cutoff:
                    stale.append((doc.get("id"), upd, doc.get("text", "")[:50]))
            except ValueError:
                stale.append((doc.get("id"), f"bad date '{upd}'", doc.get("text", "")[:50]))
            if exp and exp < date.today().isoformat():
                expired.append((doc.get("id"), exp, doc.get("text", "")[:50]))
    print(f"KB freshness audit — {total} entries, cutoff {cutoff} ({days} days)")
    for label, rows in (("STALE (review or re-confirm)", stale), ("EXPIRED (delete now)", expired)):
        print(f"\n{label}: {len(rows)}")
        for id_, d, t in rows[:30]:
            print(f"  {id_:<10} {d:<12} {t}")
    pct = (len(stale) / total * 100) if total else 0
    print(f"\nstale ratio: {pct:.0f}% — target < 20% (fresh KB ≈ answers people & AI engines both trust)")
    return 1 if (stale or expired) else 0

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args: sys.exit("usage: kb_freshness_audit.py kb.jsonl [--days 60]")
    days = int(args[args.index("--days") + 1]) if "--days" in args else 60
    sys.exit(main(args[0], days))
