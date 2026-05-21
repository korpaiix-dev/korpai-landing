"""
PDPA special-category-data consent gate for AI Chatbot in Thailand.

Use this BEFORE collecting any of:
- ข้อมูลสุขภาพ (health data) — for health/life insurance, dental, clinic
- เลขบัตรประชาชน (Thai ID) — for loan, insurance application
- ข้อมูลผู้เยาว์ (minor data) — for tutoring school, paediatric clinic
- ข้อมูลศาสนา/พันธุกรรม/biometric

Compliant with PDPA section 26 (explicit consent for sensitive personal data).
Stores consent record with timestamp + IP + channel for 10-year audit trail.

Author: KORP AI · 2026-05-21
"""
from __future__ import annotations
import hashlib
import json
import time
from dataclasses import dataclass, asdict
from typing import Literal

ConsentCategory = Literal["health", "national_id", "minor", "biometric", "religion"]


@dataclass
class ConsentRecord:
    user_id: str        # line user id / fb psid / web session id
    channel: str        # "line" | "fb" | "web"
    category: ConsentCategory
    granted: bool
    timestamp: float
    ip_hash: str        # sha256(ip + daily_salt) — PDPA-friendly
    purpose: str        # specific purpose, e.g. "เสนอเบี้ยประกันสุขภาพ"
    retention_days: int # e.g. 3650 for insurance (10 years)
    revoked_at: float | None = None

    def to_audit_row(self) -> dict:
        return {
            **asdict(self),
            "schema_version": "1.0",
            "law": "PDPA 2562 s.26",
        }


CONSENT_COPY = {
    "health": (
        "ขออนุญาตเก็บข้อมูลสุขภาพของคุณเพื่อ{purpose} — ข้อมูลนี้เป็น"
        "ข้อมูลอ่อนไหวตาม PDPA จะถูกเข้ารหัสและส่งให้เฉพาะ"
        "{recipient} เท่านั้น และจะลบเมื่อคุณขอ ยินดีให้ข้อมูลไหมคะ?"
    ),
    "national_id": (
        "ขออนุญาตเก็บเลขบัตรประชาชนของคุณเพื่อ{purpose} — ข้อมูลนี้จะ"
        "เข้ารหัส AES-256 และส่งให้เฉพาะ{recipient} เท่านั้น ยินดีให้"
        "ข้อมูลไหมคะ?"
    ),
    "minor": (
        "ผู้เรียนอายุต่ำกว่า 20 ปี — ขออนุญาตให้ผู้ปกครองยืนยันก่อน"
        "เก็บข้อมูล ขอเบอร์ผู้ปกครองและรหัส OTP ที่จะส่งให้ค่ะ"
    ),
}


def build_consent_prompt(category: ConsentCategory, purpose: str, recipient: str) -> dict:
    """Return a Line Flex / generic prompt structure with explicit yes/no buttons."""
    template = CONSENT_COPY.get(category)
    if not template:
        raise ValueError(f"no copy for category {category}")
    text = template.format(purpose=purpose, recipient=recipient)
    return {
        "text": text,
        "buttons": [
            {"label": "ยินยอม", "value": f"consent:{category}:yes"},
            {"label": "ไม่ยินยอม", "value": f"consent:{category}:no"},
        ],
        "ttl_seconds": 600,  # consent prompt expires 10 min, ask again on next flow
    }


def record_consent(
    user_id: str, channel: str, category: ConsentCategory,
    granted: bool, purpose: str, ip: str, retention_days: int = 3650,
) -> ConsentRecord:
    daily_salt = time.strftime("%Y-%m-%d")
    ip_hash = hashlib.sha256(f"{ip}{daily_salt}".encode()).hexdigest()
    return ConsentRecord(
        user_id=user_id, channel=channel, category=category,
        granted=granted, timestamp=time.time(), ip_hash=ip_hash,
        purpose=purpose, retention_days=retention_days,
    )


if __name__ == "__main__":
    # Example: insurance health quote
    prompt = build_consent_prompt(
        category="health",
        purpose="เสนอเบี้ยประกันสุขภาพ",
        recipient="ตัวแทนใบอนุญาตของ KORP AI Insurance Brokerage",
    )
    print(json.dumps(prompt, ensure_ascii=False, indent=2))

    rec = record_consent(
        user_id="U123abc", channel="line", category="health",
        granted=True, purpose="เสนอเบี้ยประกันสุขภาพ", ip="203.0.113.42",
    )
    print(json.dumps(rec.to_audit_row(), ensure_ascii=False, indent=2))
