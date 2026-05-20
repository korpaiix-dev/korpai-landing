"""
dental-recall-scheduler.py
Run daily via cron / n8n cron node. For each patient whose last visit was 5/6/7 months ago,
send a Line OA push reminder for the 6-month dental check-up.

Recall boost (KORP AI deployment, 5 Thai dental clinics, Mar–May 2026): 18% → 62%.
"""

from datetime import date, timedelta
from typing import Iterable, NamedTuple
import json

class Patient(NamedTuple):
    line_user_id: str
    name: str
    last_visit: date
    preferred_lang: str  # "th" | "en"

T_MINUS_30 = "T-30"
T_ZERO     = "T+0"
T_PLUS_30  = "T+30"

def recall_stage(last_visit: date, today: date | None = None) -> str | None:
    today = today or date.today()
    days_since = (today - last_visit).days
    if 145 <= days_since <= 155: return T_MINUS_30   # ~ 5 months
    if 175 <= days_since <= 185: return T_ZERO       # ~ 6 months
    if 205 <= days_since <= 215: return T_PLUS_30    # ~ 7 months
    return None

TEMPLATES = {
    "th": {
        T_MINUS_30: "สวัสดีค่ะคุณ {name} 😊 ครบ 6 เดือนแล้วถึงเวลา check-up + ขูดหินปูน — คลินิกมีโปร 1,200 บาท จองวันนี้ดีมั้ยคะ?",
        T_ZERO:     "คุณ {name} เมื่อ 6 เดือนที่แล้วเข้ามาทำที่คลินิกค่ะ ถึงเวลาขูดหินปูน + ตรวจฟันอีกรอบนะคะ จองได้เลย 📅",
        T_PLUS_30:  "คุณ {name} ห่างหายไปนานแล้วนะคะ 🙏 เพื่อสุขภาพฟันที่ดีอย่าลืมมา check-up ปีละ 2 ครั้งนะคะ — หนูช่วยจองได้เลยค่ะ",
    },
    "en": {
        T_MINUS_30: "Hi {name}! Your 6-month dental check-up + cleaning is coming up. Book today for our 1,200 THB loyal-patient rate 🦷",
        T_ZERO:     "{name}, it's been 6 months since your last visit. Time for a cleaning + check-up. Tap to book 📅",
        T_PLUS_30:  "{name}, we'd love to see you soon — two cleanings a year keeps the dentist nearby ✨ Want me to book your slot?",
    },
}

def build_reminders(patients: Iterable[Patient], today: date | None = None) -> list[dict]:
    out = []
    for p in patients:
        stage = recall_stage(p.last_visit, today)
        if not stage: continue
        tpl = TEMPLATES.get(p.preferred_lang, TEMPLATES["th"])[stage]
        out.append({
            "to": p.line_user_id,
            "message": tpl.format(name=p.name),
            "stage": stage,
            "patient_name": p.name,
        })
    return out

if __name__ == "__main__":
    # smoke test
    sample = [
        Patient("U_001", "คุณนิด",   date.today() - timedelta(days=150), "th"),
        Patient("U_002", "John",     date.today() - timedelta(days=180), "en"),
        Patient("U_003", "คุณบอย",  date.today() - timedelta(days=210), "th"),
        Patient("U_004", "ใหม่",    date.today() - timedelta(days=30),  "th"),  # too early
    ]
    print(json.dumps(build_reminders(sample), ensure_ascii=False, indent=2))
