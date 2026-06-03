#!/usr/bin/env python3
"""containment-rate-tracker.py — KORP AI (https://korpai.co)
คำนวณ containment / deflection / escalation rate จาก log บทสนทนา
ใช้ได้ทันที: ส่ง list ของ dict ที่มี key 'resolved_by' = 'bot' | 'human' | 'abandoned'
ไม่ต้องลง dependency อะไร (stdlib ล้วน)
"""
from collections import Counter

def kpi_from_log(conversations):
    """
    conversations: iterable ของ dict เช่น
      {"id": "c1", "resolved_by": "bot", "reopened": False}
    resolved_by: 'bot' (จบในบอต), 'human' (ส่งต่อคน), 'abandoned' (ลูกค้าหายไป)
    reopened: True ถ้าลูกค้าทักกลับมาเรื่องเดิม (กระทบ FCR)
    """
    convs = list(conversations)
    total = len(convs)
    if total == 0:
        return {"total": 0}
    by = Counter(c.get("resolved_by", "unknown") for c in convs)
    bot = by.get("bot", 0)
    human = by.get("human", 0)
    reopened = sum(1 for c in convs if c.get("reopened"))
    pct = lambda n: round(100 * n / total, 1)
    fcr_base = bot  # เฉพาะที่บอตปิดงาน
    return {
        "total": total,
        "containment_rate_pct": pct(bot),          # บอตจบเอง
        "escalation_rate_pct": pct(human),         # ส่งต่อคน
        "abandon_rate_pct": pct(by.get("abandoned", 0)),
        "fcr_pct": round(100 * (fcr_base - reopened) / fcr_base, 1) if fcr_base else 0.0,
        "verdict": _verdict(pct(bot)),
    }

def _verdict(containment):
    if containment >= 70: return "ดีมาก — ROI มักเป็นบวกชัด"
    if containment >= 45: return "ใช้ได้ — มีพื้นที่ปรับจูนเพิ่ม"
    if containment >= 30: return "เริ่มต้น — เร่งเติมฐานความรู้"
    return "ต่ำ — ทบทวนการออกแบบ/ฐานความรู้"

if __name__ == "__main__":
    sample = (
        [{"resolved_by": "bot"} for _ in range(63)] +
        [{"resolved_by": "bot", "reopened": True} for _ in range(2)] +
        [{"resolved_by": "human"} for _ in range(28)] +
        [{"resolved_by": "abandoned"} for _ in range(7)]
    )
    import json
    print(json.dumps(kpi_from_log(sample), ensure_ascii=False, indent=2))
