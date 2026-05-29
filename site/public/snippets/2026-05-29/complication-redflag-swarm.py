"""
KORP AI — Aesthetic-clinic complication red-flag swarm (Thai + EN)
2026-05-29 — MIT
Used in: filler/botox/HIFU/laser chatbot. Detect post-procedure danger keywords
and escalate to MD within 4 minutes. Bot MUST NOT generate medical advice for
these messages — only acknowledge + escalate + log.

Reference cases that informed swarm design:
- Filler-induced vascular occlusion (window 4-6h for hyaluronidase reversal)
- Botox-induced ptosis (assess within 24h)
- HIFU/laser thermal burn (cool + assess within 1h)
- Anaphylaxis to lidocaine/other (1669 immediately)
"""
import re
from dataclasses import dataclass
from typing import Optional

@dataclass
class RedFlagHit:
    category: str
    matched: str
    severity: str           # "critical" | "urgent" | "monitor"
    escalate_minutes: int   # SLA for MD callback
    recommend_er: bool      # tell patient to go ER if MD not answer
    instructions: str       # immediate "do/don't" template (no medical diagnosis)

# Each entry: (regex, category, severity, escalate_minutes, recommend_er, instructions)
RULES = [
    # === Critical: vascular ===
    (r"บวมข้างเดียว|บวมเฉพาะข้าง|swelling\s+only\s+one\s+side", "vascular", "critical", 4, True,
     "ห้ามนวด ห้ามประคบร้อน ห้ามทาครีมอะไรเพิ่ม. ทีมแพทย์กำลังติดต่อกลับใน 4 นาที."),
    (r"ผิวเขียว|สีผิวเปลี่ยน|ผิวซีดผิดปกติ|blanching|skin\s+color\s+change", "vascular", "critical", 4, True,
     "ห้ามนวด ห้ามประคบร้อน. เก็บภาพไว้. ทีมแพทย์จะติดต่อกลับใน 4 นาที."),
    (r"ปวดรุนแรง.{0,10}(2|3|4)\s*วัน|severe\s+pain\s+(2|3|4)\s+days?", "vascular", "critical", 4, True,
     "ทีมแพทย์จะติดต่อกลับใน 4 นาที. ห้ามนวด/ทาครีมเพิ่ม. ถ้าปวดแรงขึ้น โทร 1669."),

    # === Critical: vision/eye ===
    (r"มองไม่ชัด|มอง.{0,5}เบลอ|เห็นเหลื่อม|double\s+vision|blurred\s+vision", "vision", "critical", 4, True,
     "หยุดทำกิจกรรมทุกอย่าง. ทีมแพทย์จะติดต่อกลับใน 4 นาที. ถ้า MD ไม่ตอบใน 10 นาที ไป ER ทันที."),
    (r"ปวดลูกตา|ดวงตาห้อย|มองไม่เห็น|eye\s+pain|cannot\s+see", "vision", "critical", 4, True,
     "ไป ER ทันที. ทีมแพทย์จะ call กลับใน 4 นาที."),

    # === Critical: anaphylaxis ===
    (r"หายใจไม่ออก|หายใจลำบาก|cannot\s+breathe|difficulty\s+breathing", "anaphylaxis", "critical", 0, True,
     "โทร 1669 ทันที. เก็บภาพไว้. ทีมแพทย์จะติดต่อกลับเพื่อ coordinate ใน 4 นาที."),
    (r"ปากบวม|ลิ้นบวม|คอบวม|tongue\s+swell|throat\s+swell", "anaphylaxis", "critical", 0, True,
     "โทร 1669 ทันที. ทีมแพทย์จะติดต่อกลับใน 4 นาที."),
    (r"ผื่นทั้งตัว|ลมพิษ.{0,20}ทั้งตัว|hives\s+all\s+over", "anaphylaxis", "critical", 4, True,
     "ทีมแพทย์จะติดต่อกลับใน 4 นาที. เตรียม antihistamine ถ้ามี. ถ้าหายใจไม่ออก โทร 1669."),

    # === Urgent: infection ===
    (r"ไข้สูง.{0,20}(2|3)\s*วัน|fever\s+(2|3)\s+days?", "infection", "urgent", 30, False,
     "ทีมแพทย์ติดต่อกลับใน 30 นาที. เตรียม temperature record."),
    (r"หนอง|abscess|ผิวร้อน.{0,15}แดง|pus", "infection", "urgent", 30, False,
     "ทีมแพทย์จะติดต่อกลับใน 30 นาที. ห้ามบีบ/แกะ. ถ่ายภาพไว้ทุก 4 ชั่วโมง."),

    # === Monitor: botox effects ===
    (r"เปลือกตาตก|ยิ้มเบี้ยว|ปากเบี้ยว|eyelid\s+drooping|ptosis", "botox-effect", "urgent", 60, False,
     "ทีมแพทย์จะติดต่อกลับใน 1 ชั่วโมง. นี่อาจเป็น migration ปกติ — ห้ามนวด."),

    # === Monitor: HIFU/laser ===
    (r"ผิวไหม้|รู้สึกแสบ.{0,15}หลังเลเซอร์|burn\s+after\s+laser", "thermal", "urgent", 60, False,
     "ประคบเย็น 15 นาที. ทีมแพทย์จะติดต่อกลับใน 1 ชั่วโมง."),
]

def scan(message: str) -> Optional[RedFlagHit]:
    """Return RedFlagHit if any pattern matches, else None (bot may answer normally)."""
    for pattern, category, severity, mins, er, instructions in RULES:
        m = re.search(pattern, message, re.IGNORECASE)
        if m:
            return RedFlagHit(
                category=category,
                matched=m.group(0),
                severity=severity,
                escalate_minutes=mins,
                recommend_er=er,
                instructions=instructions,
            )
    return None

if __name__ == "__main__":
    tests = [
        "ทำ filler ใต้ตา 2 วันแล้วบวมข้างเดียว ปวดมาก",
        "หายใจไม่ออก เหมือนแพ้ยา",
        "ปกติเลยค่ะ แค่บวมเล็กน้อย",
        "ทำ HIFU มา รู้สึกแสบหลังเลเซอร์",
    ]
    for t in tests:
        h = scan(t)
        print("---")
        print("MSG:", t)
        if h:
            print(f"  HIT: {h.category}/{h.severity}, escalate in {h.escalate_minutes}min, ER={h.recommend_er}")
        else:
            print("  CLEAN — bot may answer")
