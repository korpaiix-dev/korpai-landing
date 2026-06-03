#!/usr/bin/env python3
"""kpi-rollup.py — KORP AI (https://korpai.co)
รวม KPI รายเดือนของ AI chatbot จาก log ดิบ เป็นรายงานสรุปบรรทัดเดียว
อ่านไฟล์ JSONL (1 บทสนทนา/บรรทัด) หรือใช้ roll_up() กับ list ตรงๆ
fields ที่ใช้: resolved_by, reopened(bool), csat(1-5|None),
              first_response_ms(int), token_cost_thb(float), lead_captured(bool)
"""
import json, sys
from statistics import mean

def roll_up(rows):
    rows = list(rows)
    n = len(rows)
    if not n:
        return {"conversations": 0}
    bot = sum(1 for r in rows if r.get("resolved_by") == "bot")
    human = sum(1 for r in rows if r.get("resolved_by") == "human")
    csats = [r["csat"] for r in rows if r.get("csat")]
    frts = [r["first_response_ms"] for r in rows if r.get("first_response_ms")]
    leads = sum(1 for r in rows if r.get("lead_captured"))
    tok = sum(r.get("token_cost_thb", 0) for r in rows)
    pct = lambda x: round(100 * x / n, 1)
    return {
        "conversations": n,
        "containment_pct": pct(bot),
        "escalation_pct": pct(human),
        "csat_pct": round(100 * sum(1 for c in csats if c >= 4) / len(csats), 1) if csats else None,
        "avg_first_response_ms": round(mean(frts)) if frts else None,
        "lead_capture_pct": pct(leads),
        "token_cost_thb_total": round(tok, 2),
        "token_cost_thb_per_conv": round(tok / n, 3),
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:                       # อ่านจากไฟล์ JSONL
        rows = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
    else:                                       # demo data
        rows = (
            [{"resolved_by":"bot","csat":5,"first_response_ms":1200,"token_cost_thb":1.1,"lead_captured":True} for _ in range(40)] +
            [{"resolved_by":"bot","csat":4,"first_response_ms":1500,"token_cost_thb":0.9} for _ in range(25)] +
            [{"resolved_by":"human","csat":3,"first_response_ms":1800,"token_cost_thb":1.3} for _ in range(28)] +
            [{"resolved_by":"abandoned","token_cost_thb":0.4} for _ in range(7)]
        )
    print(json.dumps(roll_up(rows), ensure_ascii=False, indent=2))
