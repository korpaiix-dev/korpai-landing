"""
KORP AI — Preliminary BOQ Quote Calculator (Thai contractor / renovation SME)
For: AI Chatbot on Line OA / FB that needs to give a 38-min preliminary quote.
NOTE: This is for early estimate only (±15%). Final BOQ must be reviewed by a PE
      (professional engineer) before contract signing — see พรบ. วิศวกร 2542 ม.45.
Output JSON contains: total, breakdown (14 categories), confidence, ttl_days,
material_price_ref (so revise check can trigger when prices move > 7%).
"""
from __future__ import annotations
import json, hashlib, time
from typing import Literal, TypedDict

Tier = Literal["economy", "standard", "premium"]
Status = Literal["empty", "partial_demo", "full_demo", "greenfield"]

# Baseline cost per sqm (THB) — refreshed weekly from supplier RAG
# (sample numbers — replace with live RAG lookup in production)
RATE_PER_SQM: dict[Tier, dict[str, int]] = {
    "economy":  {"livingroom":  9800, "bedroom":  8200, "kitchen": 14500, "bathroom": 18000, "general":  7400},
    "standard": {"livingroom": 14000, "bedroom": 11500, "kitchen": 21000, "bathroom": 26500, "general": 10500},
    "premium":  {"livingroom": 22500, "bedroom": 18800, "kitchen": 34000, "bathroom": 44000, "general": 17000},
}

DEMO_COST_PER_SQM = {"empty": 0, "partial_demo": 350, "full_demo": 720, "greenfield": 0}
TIMELINE_MULT = {"rush_under_45d": 1.12, "normal_60_90d": 1.00, "slow_90plus": 0.97}

class Room(TypedDict):
    type: str   # livingroom / bedroom / kitchen / bathroom / general
    sqm: float

def calc_preliminary_boq(
    rooms: list[Room],
    tier: Tier,
    status: Status,
    timeline: str,
    permit_fee: int = 18000,        # อ.1/อ.2 mid range
    waste_haul: int = 95000,        # mid range
    materials_price_ref_hash: str = "",  # RAG snapshot id
) -> dict:
    """Return preliminary BOQ. Confidence ±15%."""
    subtotal = 0
    breakdown = {}
    total_sqm = 0
    for r in rooms:
        rate = RATE_PER_SQM[tier].get(r["type"], RATE_PER_SQM[tier]["general"])
        cost = round(rate * r["sqm"])
        breakdown[r["type"]] = breakdown.get(r["type"], 0) + cost
        subtotal += cost
        total_sqm += r["sqm"]

    demo = round(DEMO_COST_PER_SQM[status] * total_sqm)
    fixed_overhead = demo + waste_haul + permit_fee
    rough = (subtotal + fixed_overhead) * TIMELINE_MULT.get(timeline, 1.0)

    return {
        "total_baht_estimate": round(rough),
        "range_low_baht":  round(rough * 0.85),
        "range_high_baht": round(rough * 1.15),
        "confidence": "±15% — preliminary only, final BOQ requires site visit + PE review",
        "ttl_days": 30,
        "breakdown": {
            "rooms": breakdown,
            "demolition": demo,
            "waste_haul": waste_haul,
            "permit_fee": permit_fee,
            "timeline_multiplier": TIMELINE_MULT.get(timeline, 1.0),
        },
        "material_price_ref": materials_price_ref_hash or hashlib.md5(str(time.time()).encode()).hexdigest()[:12],
        "disclaimer_th": "ราคาประเมิน เพื่อใช้เป็น early budget เท่านั้น — Final BOQ ที่ใช้เซ็น contract ต้องผ่าน site visit + PE review ก่อน (พรบ. วิศวกร 2542 ม.45)",
    }


if __name__ == "__main__":
    # Demo: รีโนเวทคอนโด 45 ตร.ม. tier standard, full demolition, timeline ปกติ
    quote = calc_preliminary_boq(
        rooms=[
            {"type": "livingroom", "sqm": 18},
            {"type": "bedroom",    "sqm": 12},
            {"type": "kitchen",    "sqm":  7},
            {"type": "bathroom",   "sqm":  4},
            {"type": "general",    "sqm":  4},
        ],
        tier="standard",
        status="full_demo",
        timeline="normal_60_90d",
        permit_fee=22000,
        waste_haul=110000,
    )
    print(json.dumps(quote, indent=2, ensure_ascii=False))
