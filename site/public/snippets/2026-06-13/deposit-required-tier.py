# deposit-required-tier.py
# จัดลูกค้าเข้า tier "ต้องมัดจำ" จากประวัติ no-show — ลด no-show ซ้ำซาก
# Pure stdlib. MIT — KORP AI Automation (https://korpai.co)
from dataclasses import dataclass

@dataclass
class CustomerHistory:
    total_bookings: int
    no_shows: int
    last_no_show_days_ago: int | None = None  # None = ไม่เคย no-show

def requires_deposit(h: CustomerHistory, *, high_value: bool = False) -> dict:
    """คืน decision ว่าต้องเก็บมัดจำไหม + เหตุผล (อธิบายได้ = ลดดราม่า)"""
    rate = (h.no_shows / h.total_bookings) if h.total_bookings else 0.0
    reasons = []

    if h.no_shows >= 2 and rate >= 0.3:
        reasons.append(f"no-show {h.no_shows}/{h.total_bookings} ครั้ง (rate {rate:.0%})")
    if h.last_no_show_days_ago is not None and h.last_no_show_days_ago <= 30:
        reasons.append("no-show ภายใน 30 วันล่าสุด")
    if high_value:
        reasons.append("บริการมูลค่าสูง")

    # บริการมูลค่าสูง: เก็บมัดจำเสมอ; ลูกค้าทั่วไป: เก็บเมื่อมีสัญญาณ no-show
    required = high_value or (h.no_shows >= 2 and rate >= 0.3) or \
               (h.last_no_show_days_ago is not None and h.last_no_show_days_ago <= 30)
    suggested = 300 if high_value else 100
    return {"required": required, "suggested_deposit_thb": suggested if required else 0,
            "reasons": reasons}

if __name__ == "__main__":
    print(requires_deposit(CustomerHistory(8, 3, 12)))
    print(requires_deposit(CustomerHistory(5, 0), high_value=True))
    print(requires_deposit(CustomerHistory(10, 1, 200)))
