"""
thai-statute-of-limitations.py — calculate Thai statute of limitations
(อายุความ) for common civil, criminal, labor, tax, and administrative claims.

This is NOT legal advice. It is a deadline calendar, mirroring the deadline
swarm KORP AI runs for SME law firms. A lawyer must still review.

Sources:
  - ประมวลกฎหมายอาญา ม.95
  - ประมวลกฎหมายแพ่งและพาณิชย์ ม.193/30, ม.193/34
  - พ.ร.บ.คุ้มครองแรงงาน
  - ประมวลรัษฎากร
  - พ.ร.บ.จัดตั้งศาลปกครองและวิธีพิจารณาคดีปกครอง ม.49

Author: KORP AI — https://korpai.co
License: MIT
"""
from datetime import date, timedelta
from dataclasses import dataclass

REMINDER_OFFSETS_DAYS = (60, 30, 14, 7, 3, 1)  # send reminders T-N days


@dataclass
class Limitation:
    matter_type: str
    years: float
    note: str


# A small but realistic subset of the 38-case swarm.
TABLE: dict[str, Limitation] = {
    # ----- อาญา (criminal) — ม.95 -----
    "อาญา-ประหาร/ตลอดชีวิต": Limitation("อาญา", 20, "ม.95(1)"),
    "อาญา-เกิน7ปี": Limitation("อาญา", 15, "ม.95(2)"),
    "อาญา-เกิน1ปี": Limitation("อาญา", 10, "ม.95(3)"),
    "อาญา-ไม่เกิน1ปี/ปรับ": Limitation("อาญา", 5, "ม.95(4)"),
    "อาญา-ลหุโทษ": Limitation("อาญา", 1, "ม.95(5)"),
    # ----- แพ่ง -----
    "แพ่ง-ผิดสัญญาทั่วไป": Limitation("แพ่ง", 10, "ม.193/30"),
    "แพ่ง-ละเมิด-รู้ตัวผู้กระทำ": Limitation("แพ่ง", 1, "ม.448 (อีก lid 10 ปี)"),
    "แพ่ง-ค่าจ้าง/บำเหน็จ": Limitation("แพ่ง", 2, "ม.193/34"),
    # ----- แรงงาน -----
    "แรงงาน-ค่าจ้าง/OT": Limitation("แรงงาน", 2, "ม.193/30 + พ.ร.บ.คุ้มครองแรงงาน"),
    # ----- ภาษี -----
    "ภาษี-ประมวลรัษฎากร": Limitation("ภาษี", 10, "ป.รัษฎากร"),
    # ----- ปกครอง -----
    "ปกครอง-เพิกถอนคำสั่ง": Limitation("ปกครอง", 90 / 365, "ม.49 (90 วันนับจากรู้)"),
}


def deadline(matter_key: str, trigger_date: date) -> date:
    lim = TABLE[matter_key]
    # 365.25 to handle leap years over multi-year limitations.
    return trigger_date + timedelta(days=round(lim.years * 365.25))


def reminders(matter_key: str, trigger_date: date) -> list[date]:
    d = deadline(matter_key, trigger_date)
    return [d - timedelta(days=offset) for offset in REMINDER_OFFSETS_DAYS]


if __name__ == "__main__":
    # Example: ละเมิดเกิดวันที่ 1 ม.ค. 2024, ผู้เสียหายรู้ตัวผู้กระทำวันเดียวกัน.
    t = date(2024, 1, 1)
    k = "แพ่ง-ละเมิด-รู้ตัวผู้กระทำ"
    print(f"Matter: {k}")
    print(f"Deadline: {deadline(k, t)}")
    print(f"Reminders: {reminders(k, t)}")
