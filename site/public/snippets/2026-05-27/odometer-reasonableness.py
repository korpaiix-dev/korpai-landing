"""
Odometer reasonableness check — flags potential mileage rollback
on used cars before trade-in valuation. Used inside KORP AI's
car-dealer chatbot trade-in flow.

Rule of thumb (Thailand market, 2026):
  - Normal annual driving: 15,000 - 22,000 km
  - Taxi/grab/delivery: 40,000 - 80,000 km/year
  - Owner-driven city car: 8,000 - 14,000 km/year (work-from-home era)

Returns a verdict + suggested next step (no LLM hallucination — pure rules).
"""
from dataclasses import dataclass
from datetime import date


@dataclass
class OdometerVerdict:
    verdict: str        # "ok" | "low_suspect" | "high_normal" | "very_high_inspect"
    yearly_km: float
    flag: bool
    next_step: str


def check_odometer(
    current_km: int,
    first_reg_year: int,
    usage_hint: str = "personal",
    today: date | None = None,
) -> OdometerVerdict:
    today = today or date.today()
    age_years = max(today.year - first_reg_year, 1)
    yearly = current_km / age_years

    if usage_hint in ("taxi", "grab", "delivery"):
        lo, hi = 30_000, 90_000
    else:  # personal / unknown
        lo, hi = 6_000, 25_000

    if yearly < lo * 0.5:
        return OdometerVerdict(
            verdict="low_suspect",
            yearly_km=yearly,
            flag=True,
            next_step=(
                "เลขไมล์ต่ำผิดปกติ — เสี่ยง mileage rollback. "
                "ขอ service book + เลขไมล์รอบล่าสุดที่ศูนย์ก่อนรับเข้า stock."
            ),
        )
    if yearly > hi * 1.6:
        return OdometerVerdict(
            verdict="very_high_inspect",
            yearly_km=yearly,
            flag=True,
            next_step=(
                "เลขไมล์สูงผิดปกติ — ต้อง physical inspection: ช่วงล่าง, เครื่อง, เกียร์, "
                "compression test ก่อน quote trade-in."
            ),
        )
    if yearly > hi:
        return OdometerVerdict("high_normal", yearly, False, "ปกติสำหรับการใช้งานหนัก. ปรับราคา trade-in -8%.")
    return OdometerVerdict("ok", yearly, False, "เลขไมล์อยู่ในเกณฑ์ปกติ. ใช้ตาราง market comp ตามรุ่น/ปีได้.")


if __name__ == "__main__":
    # Demo
    cases = [
        # (km, first_reg_year, hint)
        (38_000, 2020, "personal"),   # low suspect
        (96_000, 2020, "personal"),   # normal-ish (16k/yr)
        (210_000, 2020, "personal"),  # very high
        (290_000, 2020, "taxi"),      # normal for taxi
    ]
    for km, yr, hint in cases:
        v = check_odometer(km, yr, hint)
        print(f"{km:>7} km, {yr}, {hint:>9} -> {v.verdict:<20} {v.yearly_km:>8.0f} km/y :: {v.next_step}")
