"""
service-reminder-scheduler.py
KORP AI — automated service reminder for car service customers.
Tracks last odometer reading + last service date → predicts next due date.
Sends Line Push 500km / 14 days before due.

PDPA: requires customer opt-in consent for direct marketing.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class Vehicle:
    customer_id: str
    plate: str
    brand: str
    model: str
    year: int
    odometer_km: int
    last_oil_change_at: datetime
    last_oil_change_km: int
    consent_marketing: bool  # MUST be True before push

SERVICE_INTERVALS = {
    # service: (km, days)
    'oil_change':       ( 5_000, 180),
    'transmission_oil': (40_000, 730),
    'brake_pads':       (40_000, 365),  # mid-range; track wear in production
    'tires':            (60_000, 1825),
    'air_filter':       (15_000, 365),
}

def days_to_next_oil_change(v: Vehicle, daily_km_estimate: int = 60) -> int:
    """Estimate days until next oil change (km-based OR time-based, whichever sooner)."""
    if not v.consent_marketing:
        return -1  # cannot remind without opt-in

    km_interval, day_interval = SERVICE_INTERVALS['oil_change']

    # km-based
    km_since = v.odometer_km - v.last_oil_change_km
    km_remaining = max(km_interval - km_since, 0)
    days_by_km = km_remaining / max(daily_km_estimate, 1)

    # time-based
    days_since = (datetime.now() - v.last_oil_change_at).days
    days_by_time = max(day_interval - days_since, 0)

    return int(min(days_by_km, days_by_time))

def should_remind_now(days_left: int) -> bool:
    """Reminder windows: 14 days before, then 7 days, then 1 day."""
    return days_left in (14, 7, 1)

def render_reminder_message(v: Vehicle, days_left: int) -> str:
    """Thai-language Line push template — short, friendly, with magic-link CTA."""
    return (
        f"สวัสดีค่ะ คุณ {v.customer_id[:6]} 🚗\n"
        f"รถ {v.brand} {v.model} ({v.year}) ทะเบียน {v.plate[-4:]}xx "
        f"ใกล้ถึงรอบเปลี่ยนน้ำมันเครื่องในอีก {days_left} วัน\n"
        f"จองคิวด่วน (คลิกเดียว): https://korpai.co/book/{v.customer_id}\n\n"
        f"ไม่อยากรับ reminder กดตอบ \"หยุด\""
    )

if __name__ == '__main__':
    v = Vehicle(
        customer_id='cust_a1b2c3d4',
        plate='REDACTED',
        brand='Honda', model='Civic FC', year=2018,
        odometer_km=24_400,
        last_oil_change_at=datetime(2025, 12, 1),
        last_oil_change_km=20_000,
        consent_marketing=True,
    )
    d = days_to_next_oil_change(v)
    print(f'days until next oil change: {d}')
    if should_remind_now(d):
        print(render_reminder_message(v, d))
