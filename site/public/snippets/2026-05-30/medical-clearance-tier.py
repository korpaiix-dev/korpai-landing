"""
Muay Thai gym medical clearance 3-tier risk classifier.
Returns 'GREEN' (auto-pass), 'YELLOW' (head trainer approval), 'RED' (specialist clearance required).

Reviewed by sport-medicine physicians, codified for chatbot intake.
Use at intake (before trial class) to gate sparring/clinch/fight participation.

KORP AI Automation — production reference, 2026-05-30.
License: MIT. Use at your own risk. Not medical advice.
"""

from typing import TypedDict, Literal, Optional

Tier = Literal['GREEN', 'YELLOW', 'RED']


class Intake(TypedDict, total=False):
    age: int
    bmi: float
    sbp: int                       # systolic blood pressure (mmHg)
    concussion_days: Optional[int] # days since last concussion (None if never)
    heart_class_iii_iv: bool       # NYHA III-IV
    epilepsy_uncontrolled: bool
    pregnancy: bool
    surgery_lt_6mo_major: bool
    blood_thinner_unstoppable: bool
    diabetes_oral: bool            # controlled by oral meds


RED_FLAGS = (
    'heart_class_iii_iv',
    'epilepsy_uncontrolled',
    'pregnancy',
    'surgery_lt_6mo_major',
    'blood_thinner_unstoppable',
)


def classify(answers: Intake) -> Tier:
    """Classify intake into a participation tier. Order: RED > YELLOW > GREEN."""
    # Red: hard contraindications
    for k in RED_FLAGS:
        if answers.get(k):
            return 'RED'
    cd = answers.get('concussion_days')
    if cd is not None and cd < 90:
        return 'RED'

    # Yellow: caution-warranted conditions
    age = answers.get('age', 0)
    bmi = answers.get('bmi', 0.0)
    sbp = answers.get('sbp', 0)
    if (
        55 <= age <= 65
        or answers.get('diabetes_oral')
        or 150 <= sbp <= 170
        or 32 <= bmi <= 38
        or (cd is not None and 90 <= cd <= 365)
    ):
        return 'YELLOW'

    return 'GREEN'


def policy_message(tier: Tier, lang: str = 'th') -> str:
    msgs = {
        'GREEN': {
            'th': 'พร้อมเทรนได้ — เซ็น e-waiver แล้วรับ QR wrist band',
            'en': 'Cleared for training — please sign the e-waiver and collect your wrist QR band.',
        },
        'YELLOW': {
            'th': 'กรุณาแนบใบรับรองแพทย์ทั่วไป (general fitness) — หัวหน้าเทรนเนอร์อนุมัติภายใน 4 ชม. และห้าม sparring 14 วันแรก',
            'en': 'Please upload a general-fitness medical certificate. Head trainer approves within 4 hrs. No sparring in the first 14 days.',
        },
        'RED': {
            'th': 'ต้องมีใบรับรองแพทย์เฉพาะทาง — เราแนะนำ pad work no-contact เท่านั้น โปรดติดต่อแพทย์ก่อน',
            'en': 'Specialist medical clearance required. We can offer no-contact pad work only. Please consult your physician first.',
        },
    }
    return msgs[tier][lang]


if __name__ == '__main__':
    cases = [
        {'age': 28, 'bmi': 24, 'sbp': 120, 'concussion_days': None},
        {'age': 60, 'bmi': 30, 'sbp': 158, 'concussion_days': 200},
        {'age': 24, 'bmi': 22, 'sbp': 118, 'concussion_days': 45},
        {'age': 30, 'bmi': 25, 'sbp': 110, 'pregnancy': True},
    ]
    for c in cases:
        t = classify(c)
        print(f'{c} -> {t} -> {policy_message(t)}')
