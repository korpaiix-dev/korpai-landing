"""
Test drive scheduler — books a test-drive slot on the sales rep's
Google Calendar with conflict avoidance and a 30-min buffer.

Used inside KORP AI dealer chatbot. Always picks the next-available
slot in business hours (10:00–18:00 local) for the requested sales rep.

Requirements:
  pip install google-api-python-client google-auth
"""
from __future__ import annotations
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Bangkok")
SLOT_MINUTES = 45  # 30-min test drive + 15-min handoff
BUFFER_MINUTES = 15
OPEN = time(10, 0)
CLOSE = time(18, 0)


def next_available_slot(
    calendar_service,
    sales_email: str,
    desired_start: datetime | None = None,
    days_ahead: int = 7,
) -> datetime:
    start = (desired_start or datetime.now(TZ)).astimezone(TZ)
    if start.time() < OPEN:
        start = start.replace(hour=OPEN.hour, minute=0, second=0, microsecond=0)

    for d in range(days_ahead):
        day = start + timedelta(days=d)
        # Skip Sunday (dealer closed)
        if day.weekday() == 6:
            continue
        day_open = day.replace(hour=OPEN.hour, minute=0, second=0, microsecond=0)
        day_close = day.replace(hour=CLOSE.hour, minute=0, second=0, microsecond=0)
        cursor = max(day_open, start) if d == 0 else day_open

        busy = _busy_blocks(calendar_service, sales_email, day_open, day_close)
        while cursor + timedelta(minutes=SLOT_MINUTES) <= day_close:
            slot_end = cursor + timedelta(minutes=SLOT_MINUTES + BUFFER_MINUTES)
            if not any(_overlap(cursor, slot_end, b[0], b[1]) for b in busy):
                return cursor
            cursor += timedelta(minutes=15)

    raise RuntimeError("No slot available in the next 7 days — escalate to sales manager")


def book_test_drive(calendar_service, sales_email: str, customer_name: str, car_label: str, start: datetime):
    event = {
        "summary": f"[Test Drive] {customer_name} — {car_label}",
        "description": (
            f"Auto-booked by KORP AI chatbot.\n"
            f"Customer: {customer_name}\n"
            f"Car: {car_label}\n"
            f"Buffer: {BUFFER_MINUTES} min after."
        ),
        "start": {"dateTime": start.isoformat(), "timeZone": "Asia/Bangkok"},
        "end": {"dateTime": (start + timedelta(minutes=SLOT_MINUTES)).isoformat(), "timeZone": "Asia/Bangkok"},
        "reminders": {"useDefault": False, "overrides": [
            {"method": "popup", "minutes": 24 * 60},
            {"method": "popup", "minutes": 120},
        ]},
    }
    return calendar_service.events().insert(calendarId=sales_email, body=event).execute()


def _busy_blocks(calendar_service, email: str, t_min: datetime, t_max: datetime):
    body = {
        "timeMin": t_min.isoformat(),
        "timeMax": t_max.isoformat(),
        "timeZone": "Asia/Bangkok",
        "items": [{"id": email}],
    }
    resp = calendar_service.freebusy().query(body=body).execute()
    return [
        (datetime.fromisoformat(b["start"]), datetime.fromisoformat(b["end"]))
        for b in resp["calendars"][email]["busy"]
    ]


def _overlap(a_s, a_e, b_s, b_e):
    return a_s < b_e and b_s < a_e
