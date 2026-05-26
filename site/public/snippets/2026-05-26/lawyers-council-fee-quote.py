"""
lawyers-council-fee-quote.py — quote a base lawyer fee aligned with
the Lawyers Council of Thailand's minimum-fee guidance, parameterised by
matter type, ทุนทรัพย์ (claim amount), and complexity multiplier.

This is a starting estimate. Final quote = partner judgement + market.
DO NOT publish to clients without partner approval.

Author: KORP AI — https://korpai.co
License: MIT
"""
from dataclasses import dataclass

# Indicative base fees, THB. Tune to the firm's actual rate card.
BASE = {
    "civil":            {"setup": 15000, "pct_of_claim": 0.05},   # แพ่ง
    "criminal":         {"setup": 25000, "pct_of_claim": 0.00},   # อาญา
    "labor":            {"setup": 10000, "pct_of_claim": 0.10},   # แรงงาน
    "administrative":   {"setup": 20000, "pct_of_claim": 0.00},   # ปกครอง
    "family":           {"setup": 18000, "pct_of_claim": 0.00},   # ครอบครัว
    "tax":              {"setup": 22000, "pct_of_claim": 0.03},   # ภาษี
}

COMPLEXITY = {"low": 1.0, "medium": 1.4, "high": 2.0, "very_high": 2.8}


@dataclass
class Quote:
    matter_type: str
    base_thb: float
    pct_component_thb: float
    complexity_multiplier: float
    total_thb: float
    notes: list[str]


def quote(
    matter_type: str,
    claim_amount_thb: float = 0,
    complexity: str = "medium",
) -> Quote:
    if matter_type not in BASE:
        raise ValueError(f"unknown matter_type {matter_type!r}")
    if complexity not in COMPLEXITY:
        raise ValueError(f"unknown complexity {complexity!r}")

    cfg = BASE[matter_type]
    base = cfg["setup"]
    pct = cfg["pct_of_claim"] * max(claim_amount_thb, 0)
    mult = COMPLEXITY[complexity]
    total = (base + pct) * mult

    notes = []
    if matter_type == "civil" and claim_amount_thb > 5_000_000:
        notes.append("ทุนทรัพย์สูง — ต่อรอง pct ลงได้")
    if complexity == "very_high":
        notes.append("ตรวจสอบ partner ก่อนยืนยัน")

    return Quote(matter_type, base, pct, mult, round(total, 2), notes)


if __name__ == "__main__":
    q = quote("civil", claim_amount_thb=800_000, complexity="medium")
    print(q)
