"""
insurance-claim-intake.py
KORP AI — 4-step insurance claim intake for Thai car service chatbots
Compresses 47-min phone intake into 8-min Line/Messenger flow.

Supports: วิริยะ, ไทยศรี, เมืองไทย, สินมั่นคง, ทิพยประกันภัย, AXA, MSIG
"""

from dataclasses import dataclass, field
from typing import Literal
from datetime import datetime

Insurer = Literal['viriya', 'thaisri', 'muangthai', 'sinmunkong', 'thip', 'axa', 'msig']

@dataclass
class ClaimIntake:
    customer_id: str
    plate: str  # PDPA: encrypt at rest
    vin: str    # PDPA: encrypt at rest
    insurer: Insurer | None = None
    policy_no: str | None = None
    damage_photos: list[str] = field(default_factory=list)  # storage URLs
    incident_at: datetime | None = None
    counterparty: dict | None = None
    consent_given: bool = False
    step: int = 1

    def required_photos(self) -> list[str]:
        captured = len(self.damage_photos)
        # 4 angles: front, rear, driver-side, passenger-side
        return ['front', 'rear', 'driver_side', 'passenger_side'][captured:]

    def can_submit(self) -> bool:
        return all([
            self.consent_given,
            self.insurer,
            self.policy_no,
            len(self.damage_photos) >= 4,
            self.incident_at,
        ])

    def next_question(self) -> str | None:
        if not self.consent_given:
            return ('ขออนุญาตเก็บข้อมูลกรมธรรม์เพื่อทำเคลมตาม PDPA นะคะ '
                    'ข้อมูลจะใช้เฉพาะส่งบริษัทประกันเท่านั้น (ตอบ "ยินยอม")')
        missing_photos = self.required_photos()
        if missing_photos:
            return f"ขอรูปด้าน {missing_photos[0]} ของรถครับ (เห็นความเสียหายชัด ๆ)"
        if not self.insurer:
            return 'รถคันนี้ทำประกันกับบริษัทไหนครับ (วิริยะ / ไทยศรี / เมืองไทย / สินมั่นคง / ทิพย / AXA / MSIG)'
        if not self.policy_no:
            return 'ขอเลขกรมธรรม์ครับ (อยู่บนหน้าแรกของหนังสือกรมธรรม์)'
        if not self.incident_at:
            return 'เหตุการณ์เกิดเมื่อไหร่ครับ (วันที่ + เวลาคร่าว ๆ)'
        return None

    def render_claim_form(self) -> dict:
        """Render insurer-specific claim form payload."""
        assert self.can_submit(), 'incomplete intake'
        # Each insurer has slightly different field names — abstract here
        templates = {
            'viriya':       {'policy_field': 'หมายเลขกรมธรรม์',  'submit_via': 'email'},
            'thaisri':      {'policy_field': 'เลขที่กรมธรรม์',   'submit_via': 'api'},
            'muangthai':    {'policy_field': 'Policy No.',         'submit_via': 'email'},
            'sinmunkong':   {'policy_field': 'หมายเลขกรมธรรม์',  'submit_via': 'email'},
            'thip':         {'policy_field': 'Policy Number',      'submit_via': 'api'},
            'axa':          {'policy_field': 'Policy Number',      'submit_via': 'api'},
            'msig':         {'policy_field': 'Policy No.',         'submit_via': 'email'},
        }
        tmpl = templates[self.insurer]
        return {
            tmpl['policy_field']: self.policy_no,
            'plate': self.plate,  # NOTE: encrypted at rest
            'damage_photos': self.damage_photos,
            'incident_at': self.incident_at.isoformat(),
            'counterparty': self.counterparty,
            'submit_via': tmpl['submit_via'],
        }

if __name__ == '__main__':
    # quick demo
    c = ClaimIntake(customer_id='cust_001', plate='REDACTED', vin='REDACTED')
    while q := c.next_question():
        print(q)
        # in real chatbot: await user reply, then update state
        break
