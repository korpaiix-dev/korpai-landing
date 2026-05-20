"""
sso-dental-benefit.py
Look up Thai Social Security Office (ม.33/39) dental annual benefit for a given
treatment + remaining yearly quota. Returns a structured dict the chatbot
can render directly. As of 2025 schedule: 900 THB/year for cleaning, filling, extraction.

Source: SSO official notification (สำนักงานประกันสังคม).
"""

from dataclasses import dataclass

DENTAL_TREATMENTS = {
    "ขูดหินปูน":   {"avg_thb": 600,  "eligible": True},
    "อุดฟัน":      {"avg_thb": 700,  "eligible": True},
    "ถอนฟัน":      {"avg_thb": 800,  "eligible": True},
    "ผ่าฟันคุด":   {"avg_thb": 3500, "eligible": True},  # only above-gum cases
    "รักษาราก":    {"avg_thb": 5500, "eligible": False},
    "จัดฟัน":      {"avg_thb": 45000,"eligible": False},
    "ฟอกสีฟัน":    {"avg_thb": 6500, "eligible": False},
    "รากเทียม":    {"avg_thb": 60000,"eligible": False},
}

SSO_ANNUAL_CAP_THB = 900  # 2025 schedule

@dataclass
class Quote:
    treatment: str
    list_price_thb: int
    sso_eligible: bool
    sso_used_this_year_thb: int
    sso_remaining_thb: int
    sso_reimbursable_thb: int
    out_of_pocket_thb: int

def quote(treatment: str, sso_used: int = 0) -> Quote | None:
    info = DENTAL_TREATMENTS.get(treatment)
    if not info: return None
    remaining = max(SSO_ANNUAL_CAP_THB - sso_used, 0)
    reimbursable = min(info["avg_thb"], remaining) if info["eligible"] else 0
    return Quote(
        treatment=treatment,
        list_price_thb=info["avg_thb"],
        sso_eligible=info["eligible"],
        sso_used_this_year_thb=sso_used,
        sso_remaining_thb=remaining,
        sso_reimbursable_thb=reimbursable,
        out_of_pocket_thb=info["avg_thb"] - reimbursable,
    )

if __name__ == "__main__":
    for t, used in [("ขูดหินปูน", 0), ("อุดฟัน", 300), ("จัดฟัน", 0), ("ผ่าฟันคุด", 0)]:
        print(quote(t, used))
