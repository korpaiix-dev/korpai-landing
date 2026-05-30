"""
Shift Muay Thai training-time suggestions to post-iftar hours during Ramadan.

For an Arabic-speaking inbound customer, the chatbot consults the Islamic
calendar and, if today is within Ramadan, rewrites any time block in the
07:00–18:00 window to a 21:00–00:00 alternative (and never offers food/drink
during fasting hours).

Uses hijri-converter (pip install hijri-converter --break-system-packages).
KORP AI Automation, 2026-05-30. MIT.
"""

from __future__ import annotations
from datetime import date, time
from hijri_converter import Hijri, Gregorian


def is_ramadan(d: date | None = None) -> bool:
    d = d or date.today()
    h = Gregorian(d.year, d.month, d.day).to_hijri()
    return h.month == 9  # Ramadan = 9th month of the Hijri year


def shift_block(slot: tuple[time, time]) -> tuple[time, time]:
    """If slot is fully inside fasting hours, shift to post-iftar (21:00 start)."""
    start, end = slot
    fast_start, fast_end = time(7, 0), time(18, 0)
    if start >= fast_start and end <= fast_end:
        return (time(21, 0), time(min(23, start.hour + 14 - 21), 0))
    return slot


def chatbot_suggest(slots: list[tuple[time, time]], today: date | None = None) -> dict:
    today = today or date.today()
    if is_ramadan(today):
        shifted = [shift_block(s) for s in slots]
        return {
            'ramadan': True,
            'note_th': 'ปรับเวลาเทรนเป็นหลังละศีลอด (post-iftar) — ไม่เสนออาหาร/น้ำในช่วงถือศีลอด',
            'note_ar': 'تم تعديل أوقات التدريب إلى ما بعد الإفطار. لن نقترح طعاماً أو ماءً خلال ساعات الصيام.',
            'slots': [(s.strftime('%H:%M'), e.strftime('%H:%M')) for s, e in shifted],
        }
    return {
        'ramadan': False,
        'slots': [(s.strftime('%H:%M'), e.strftime('%H:%M')) for s, e in slots],
    }


if __name__ == '__main__':
    # Ramadan 2026 = approx Feb 17 – Mar 19
    test_day = date(2026, 3, 1)
    out = chatbot_suggest(
        [(time(7, 0), time(10, 0)), (time(16, 0), time(18, 0))],
        today=test_day,
    )
    import json
    print(json.dumps(out, ensure_ascii=False, indent=2))
