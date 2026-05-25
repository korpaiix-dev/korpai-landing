"""
tax-deadline-swarm.py — Schedule 5-tier reminders (D-14/D-7/D-3/D-1/D-0)
for every recurring Thai tax filing per client, push to Line OA.
KORP AI · 2026 · MIT
"""
from datetime import date, timedelta
from dataclasses import dataclass
from typing import Iterable

# Recurrence definitions for monthly-cycle forms
MONTHLY_FORMS = {
    "PND.1":  {"day": 7,  "label": "ภงด.1 หัก ณ ที่จ่ายเงินเดือน"},
    "PND.3":  {"day": 7,  "label": "ภงด.3 หัก ณ ที่จ่ายบุคคล"},
    "PND.53": {"day": 7,  "label": "ภงด.53 หัก ณ ที่จ่ายนิติบุคคล"},
    "PND.54": {"day": 7,  "label": "ภงด.54 จ่ายไปต่างประเทศ"},
    "PP.30":  {"day": 15, "label": "ภพ.30 VAT"},
    "PP.36":  {"day": 15, "label": "ภพ.36 VAT จ่ายแทน"},
    "SSO":    {"day": 15, "label": "ประกันสังคม สปส.1-10"},
}
REMINDER_OFFSETS = [14, 7, 3, 1, 0]

@dataclass
class Reminder:
    client_tin: str
    form: str
    label: str
    due: date
    days_left: int

def upcoming_reminders(client_tin: str, today: date) -> Iterable[Reminder]:
    """Yield reminders that should fire today for this client."""
    # Generate next 2 monthly cycles
    candidates: list[tuple[str, dict, date]] = []
    for offset in (0, 1):
        m = today.month + offset
        y = today.year + (m - 1) // 12
        m = ((m - 1) % 12) + 1
        for code, info in MONTHLY_FORMS.items():
            try:
                due = date(y, m, info["day"])
            except ValueError:
                continue
            candidates.append((code, info, due))
    for code, info, due in candidates:
        delta = (due - today).days
        if delta in REMINDER_OFFSETS:
            yield Reminder(client_tin, code, info["label"], due, delta)

def format_line_message(r: Reminder) -> str:
    urgency = {14:"แจ้งล่วงหน้า",7:"อีก 1 สัปดาห์",3:"3 วัน",1:"พรุ่งนี้!",0:"วันนี้!"}[r.days_left]
    return (
        f"🔔 {urgency}: {r.label}\n"
        f"กำหนดยื่น: {r.due.strftime('%d/%m/%Y')}\n"
        f"เลขผู้เสียภาษี: {r.client_tin}\n"
        f"ส่งเอกสารผ่าน Line นี้ภายในวันนี้เพื่อให้สำนักงานเตรียมยื่นทันรอบ"
    )

if __name__ == "__main__":
    today = date.today()
    for r in upcoming_reminders("0105560123456", today):
        print(format_line_message(r))
        print("---")
