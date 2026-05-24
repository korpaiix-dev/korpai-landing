#!/usr/bin/env bash
# sla-breach-report.sh
# Daily SLA breach report for logistics SME — emits CSV summary by carrier.
# Reads JSON lines like: {"id":"X1","carrier":"flash","status":"delivered","promised":"...","delivered_at":"..."}
#
# Usage:
#   cat orders-today.jsonl | bash sla-breach-report.sh > breach.csv
#
# Companion to: https://korpai.co/blog/ai-chatbot-ขนส่ง-โลจิสติกส์-logistics-sme-2026
# MIT — KORP AI Automation.

set -euo pipefail

python3 - "$@" << 'PY'
import json
import sys
from collections import defaultdict
from datetime import datetime

ISO = "%Y-%m-%dT%H:%M:%S"

stats = defaultdict(lambda: {"total": 0, "ontime": 0, "breach": 0})

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        o = json.loads(line)
    except json.JSONDecodeError:
        continue
    if o.get("status") != "delivered":
        continue
    promised = o.get("promised")
    delivered = o.get("delivered_at")
    carrier = o.get("carrier", "unknown")
    if not promised or not delivered:
        continue
    p = datetime.fromisoformat(promised.replace("Z", ""))
    d = datetime.fromisoformat(delivered.replace("Z", ""))
    stats[carrier]["total"] += 1
    if d <= p:
        stats[carrier]["ontime"] += 1
    else:
        stats[carrier]["breach"] += 1

print("carrier,total,ontime,breach,ontime_pct")
for c, v in sorted(stats.items()):
    pct = (100.0 * v["ontime"] / v["total"]) if v["total"] else 0
    print(f"{c},{v['total']},{v['ontime']},{v['breach']},{pct:.1f}")
PY
