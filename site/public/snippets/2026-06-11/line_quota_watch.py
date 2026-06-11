#!/usr/bin/env python3
"""LINE OA free-tier quota watcher — alert before you hit the broadcast cap.

Calls LINE Messaging API quota endpoints, prints usage %, estimates THB
overage if you stay on a paid plan, exits 1 when usage >= threshold
(so you can wire it to cron + LINE Notify/email).

Usage:
  LINE_CHANNEL_TOKEN=xxxx python3 line_quota_watch.py [--threshold 0.8]

Companion to: https://korpai.co/blog/ai-chatbot-ฟรี-2026-ต้นทุนแฝง-sme
MIT — KORP AI (korpai.co)
"""
import json, os, sys, urllib.request

API = "https://api.line.me/v2/bot/message"
OVERAGE_THB = 0.08          # ~0.06-0.10 THB/msg on TH paid plans (Jun 2026, verify)

def get(path: str, token: str) -> dict:
    req = urllib.request.Request(API + path, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.load(r)

def main() -> int:
    token = os.environ.get("LINE_CHANNEL_TOKEN")
    if not token:
        print("set LINE_CHANNEL_TOKEN first", file=sys.stderr); return 2
    threshold = 0.8
    if "--threshold" in sys.argv:
        threshold = float(sys.argv[sys.argv.index("--threshold") + 1])

    quota = get("/quota", token)                    # {"type":"limited","value":300} or {"type":"none"}
    used = get("/quota/consumption", token)["totalUsage"]

    if quota.get("type") != "limited":
        print(f"plan has no broadcast cap. used this month: {used}"); return 0

    cap = quota["value"]
    pct = used / cap if cap else 0
    print(f"used {used}/{cap} broadcast msgs ({pct:.0%})")
    remain = cap - used
    print(f"remaining: {remain} | projected overage cost if exceeded: ~{OVERAGE_THB:.2f} THB/msg")
    if pct >= threshold:
        print(f"WARNING: >= {threshold:.0%} of free quota — plan upgrade (~1,200 THB/mo) or trim push campaigns")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
