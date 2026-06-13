# booking-confirm-state.py
# state machine สถานะนัด: ยืนยัน active แทน default-มาแน่ → flag นัดที่ต้องโทรเช็ก
# Pure stdlib. MIT — KORP AI Automation (https://korpai.co)
from enum import Enum
from datetime import datetime, timedelta

class State(str, Enum):
    BOOKED = "booked"          # จองแล้ว ยังไม่ยืนยัน
    CONFIRMED = "confirmed"    # ลูกค้ากดยืนยัน
    NEEDS_CALL = "needs_call"  # ไม่ยืนยันในเวลาที่กำหนด → ทีมโทรเช็ก
    RESCHEDULED = "rescheduled"
    CANCELLED = "cancelled"

def evaluate(state: str, *, appointment_at: datetime, now: datetime,
             confirm_deadline_hours: int = 12) -> str:
    """เลื่อนสถานะอัตโนมัติ: ถ้ายังไม่ยืนยันและใกล้ถึง deadline → needs_call"""
    if state in (State.CONFIRMED, State.CANCELLED, State.RESCHEDULED):
        return state
    deadline = appointment_at - timedelta(hours=confirm_deadline_hours)
    if state == State.BOOKED and now >= deadline:
        return State.NEEDS_CALL
    return state

if __name__ == "__main__":
    appt = datetime(2026, 6, 15, 10, 0)
    print(evaluate("booked", appointment_at=appt, now=datetime(2026, 6, 14, 23, 0)))  # needs_call
    print(evaluate("booked", appointment_at=appt, now=datetime(2026, 6, 13, 9, 0)))   # booked
