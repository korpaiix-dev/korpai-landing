"""
symptom-intake-guardrail.py
KORP AI — symptom collection without diagnosis.
Hard rule: AI MUST NOT diagnose vehicle problems. Only collect + book diagnostic appointment.

Why: legal liability — if AI tells customer "looks like alternator, drive home"
and engine dies on highway, garage is liable. Always escalate to mechanic.
"""

from dataclasses import dataclass, field

# These phrases would diagnose — never emit them
FORBIDDEN_OUTPUTS = [
    'น่าจะเป็น', 'น่าจะเสีย', 'น่าจะมีปัญหาที่', 'น่าจะคือ',
    'น่าจะ alternator', 'น่าจะ battery', 'น่าจะ injector',
    'sounds like', 'probably the', 'most likely the',
    'ขับต่อได้', 'ไม่เป็นไรครับ ลองขับดูก่อน', 'safe to drive',
]

@dataclass
class SymptomIntake:
    customer_id: str
    vehicle_brand: str
    vehicle_model: str
    raw_symptoms: list[str] = field(default_factory=list)
    safety_critical: bool = False

    # Safety-critical keywords trigger IMMEDIATE escalation to mechanic + tow recommendation
    SAFETY_RED_FLAGS = [
        'เบรกไม่กิน', 'พวงมาลัยล็อก', 'ควันใต้คาปอ', 'ไฟไหม้', 'พ่นน้ำมัน',
        'no brake', 'steering locked', 'smoke from hood', 'fire', 'fuel leak',
    ]

    def add_symptom(self, text: str):
        self.raw_symptoms.append(text)
        if any(flag in text.lower() for flag in self.SAFETY_RED_FLAGS):
            self.safety_critical = True

    def response(self) -> str:
        if self.safety_critical:
            return (
                "🚨 อาการที่คุณบอกมา **อันตราย ห้ามขับต่อ** ครับ\n"
                "กรุณาจอดในที่ปลอดภัย โทรหารถยก\n"
                "หรือกด → https://korpai.co/emergency-tow ทีมรับจัดให้ภายใน 30 นาที"
            )
        if len(self.raw_symptoms) < 3:
            return (
                "เข้าใจครับ ขอข้อมูลเพิ่มอีก 2 ข้อเพื่อให้ช่างเตรียมเครื่องมือ:\n"
                "1) อาการเกิดตอนสตาร์ทเย็น/ร้อน/ระหว่างขับ?\n"
                "2) มีไฟเตือนขึ้น dashboard ไหม?"
            )
        # Final: hand off to booking — never diagnose
        return (
            f"ขอบคุณข้อมูลครับ จดอาการให้ช่างแล้ว ({len(self.raw_symptoms)} ข้อ)\n"
            f"แนะนำให้นำรถเข้าตรวจหน้างาน เพื่อความปลอดภัย\n"
            f"จองคิวด่วน → https://korpai.co/book/{self.customer_id}"
        )

def validate_output(text: str) -> bool:
    """Returns False if AI accidentally tried to diagnose."""
    lower = text.lower()
    return not any(phrase in lower for phrase in FORBIDDEN_OUTPUTS)

if __name__ == '__main__':
    s = SymptomIntake(customer_id='c01', vehicle_brand='Toyota', vehicle_model='Vios')
    s.add_symptom('เครื่องสะดุดตอนสตาร์ท')
    print(s.response())
