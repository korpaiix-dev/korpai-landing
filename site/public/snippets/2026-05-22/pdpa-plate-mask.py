"""
pdpa-plate-mask.py
KORP AI — utility for masking license plates + VIN in customer-facing UI / logs.
Under PDPA 2562 + สคส. guidance 2024+, Thai license plates ARE personal data.

Use cases:
1. Mask plate in chatbot UI when echoing back to customer
2. Mask plate before logging conversation for analytics
3. Blur plate in damage photos before reuse in marketing
"""

import re

# Thai plate formats: 1ABC2345, ABC2345, กข1234, 1กข2345 (BMA + provincial)
THAI_PLATE_RE = re.compile(r'\b\d{0,2}[A-Zก-๏]{1,3}\s?\d{1,4}\b')
VIN_RE = re.compile(r'\b[A-HJ-NPR-Z0-9]{17}\b')  # standard VIN excludes I/O/Q
ID_CARD_RE = re.compile(r'\b\d{1}[- ]?\d{4}[- ]?\d{5}[- ]?\d{2}[- ]?\d{1}\b')

def mask_plate(text: str) -> str:
    """Show only last 2 chars, e.g. กข1234 → xxxx34"""
    def _m(m):
        s = m.group(0)
        keep = s[-2:] if len(s) >= 2 else s
        return 'x' * (len(s) - len(keep)) + keep
    return THAI_PLATE_RE.sub(_m, text)

def mask_vin(text: str) -> str:
    return VIN_RE.sub(lambda m: m.group(0)[:3] + 'x' * 11 + m.group(0)[-3:], text)

def mask_id_card(text: str) -> str:
    return ID_CARD_RE.sub(lambda m: 'x-xxxx-xxxxx-xx-x', text)

def mask_all_pii(text: str) -> str:
    return mask_id_card(mask_vin(mask_plate(text)))

# Demo
if __name__ == '__main__':
    sample = (
        "ลูกค้า: รถผม 1กข 2345 VIN MR2BL3FZ100001234 "
        "บัตรประจำตัว 1-2345-67890-12-3 ต้องการเคลมประกัน"
    )
    print('INPUT :', sample)
    print('MASKED:', mask_all_pii(sample))
