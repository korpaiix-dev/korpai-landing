"""
KORP AI — Warranty / Post-Handover follow-up bot for Thai contractor SME.
Schedules 3 touchpoints per delivered project: 6 mo, 12 mo, 24 mo (legal warranty
runs 2 years; structural 5 years). Sends a Thai 8-item home-check survey on
each anchor, captures issues into the CRM, and offers an upsell at 24mo
("ครบ warranty + รีโนเวทเพิ่ม").

Run as cron daily 09:00 ICT.
"""
from __future__ import annotations
import datetime as dt
from dataclasses import dataclass

CHECKLIST_TH = [
    "กระเบื้องร่อน / แตก",
    "สีลอก / สีเป็นรา",
    "ก๊อกน้ำหยด / ระบบประปารั่ว",
    "แอร์มีน้ำหยด หรือ ทำงานปกติ",
    "ปลั๊กไฟ / สวิตช์ ใช้งานได้ทุกจุด",
    "ประตู / หน้าต่าง ปิดสนิท / ล็อกได้",
    "ฝ้าเพดาน บวม / ร้อน / รั่วซึม",
    "พื้นมีรอยแยก / เสียงดังเมื่อเดิน"
]

@dataclass
class HandoverRecord:
    project_id: str
    customer_line_userid: str
    customer_name: str
    handed_over_at: dt.date

def due_touchpoints(today: dt.date, h: HandoverRecord) -> list[str]:
    age_days = (today - h.handed_over_at).days
    due = []
    if 180 <= age_days <= 185:  due.append("6mo")
    if 365 <= age_days <= 370:  due.append("12mo")
    if 730 <= age_days <= 735:  due.append("24mo")
    return due

def compose_message(kind: str, customer_name: str) -> str:
    if kind == "6mo":
        return (f"สวัสดีค่ะคุณ{customer_name} ครบ 6 เดือนตั้งแต่ส่งมอบบ้าน — "
                f"รบกวนเช็ค 8 จุดนี้ค่ะ แล้วตอบกลับว่าจุดไหนต้องให้ทีมเข้าซ่อม "
                f"(ภายใต้ warranty ฟรี):\n• " + "\n• ".join(CHECKLIST_TH))
    if kind == "12mo":
        return (f"สวัสดีค่ะคุณ{customer_name} ครบ 1 ปี — "
                f"ขอเชิญรับ service ตรวจสภาพประจำปีฟรี + ขอ feedback "
                f"ให้คะแนน 1-10 + บอกสิ่งที่ดีและสิ่งที่ควรปรับ")
    if kind == "24mo":
        return (f"สวัสดีค่ะคุณ{customer_name} ครบ warranty 2 ปี — "
                f"เรามีโปรพิเศษสำหรับลูกค้าเก่า: รีโนเวทเพิ่มเติม / ขยายห้อง / "
                f"upgrade ครัว ลด 8% รวม free 3D mockup — สนใจส่ง 'สนใจ' ตอบกลับค่ะ")
    raise ValueError(kind)

def run_daily(today: dt.date, all_handovers: list[HandoverRecord], line_push):
    sent = []
    for h in all_handovers:
        for kind in due_touchpoints(today, h):
            line_push(h.customer_line_userid, compose_message(kind, h.customer_name))
            sent.append({"project": h.project_id, "kind": kind})
    return sent
