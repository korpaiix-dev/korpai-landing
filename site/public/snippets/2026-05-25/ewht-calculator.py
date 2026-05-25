"""
ewht-calculator.py — e-Withholding Tax calculator for Thai SMEs.
Returns the correct PND form, withholding %, and amount based on
payer/payee type and nature of payment (RD Sec.50 + ministerial regulations).
KORP AI · 2026 · MIT
"""
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class WHTResult:
    form: str          # "PND.3" or "PND.53" or "PND.54"
    percent: Decimal
    amount: Decimal
    rationale: str

# (payer_type, payee_type, nature) -> (form, percent, rationale)
RULES = {
    # Service / wages of services
    ("company","company","service"):     ("PND.53", "3", "ค่าจ้างทำของ/บริการ นิติ→นิติ"),
    ("company","individual","service"):  ("PND.3",  "3", "ค่าวิชาชีพอิสระ/บริการ → บุคคล"),
    # Rent
    ("company","company","rent"):        ("PND.53", "5", "ค่าเช่าทรัพย์สิน"),
    ("company","individual","rent"):     ("PND.3",  "5", "ค่าเช่าทรัพย์สิน"),
    # Advertising
    ("company","company","advertising"): ("PND.53", "2", "ค่าโฆษณา"),
    # Transport (non-postal)
    ("company","company","transport"):   ("PND.53", "1", "ค่าขนส่งไม่รวมไปรษณีย์"),
    # Interest
    ("company","company","interest"):    ("PND.53", "1", "ดอกเบี้ย"),
    # Royalty
    ("company","company","royalty"):     ("PND.53", "3", "ค่าลิขสิทธิ์"),
    # Cross-border service
    ("company","foreign","service"):     ("PND.54", "15", "บริการต่างประเทศ"),
    ("company","foreign","interest"):    ("PND.54", "10", "ดอกเบี้ยต่างประเทศ"),
    # Prize / promotion
    ("company","individual","prize"):    ("PND.3",  "5", "รางวัล/ส่วนลด/สิทธิประโยชน์"),
}

# minimum thresholds (THB) under which WHT not required
THRESHOLDS = {"service": Decimal("1000"), "interest": Decimal("1000")}

def calc(payer: str, payee: str, nature: str, gross: Decimal) -> WHTResult | None:
    rule = RULES.get((payer, payee, nature))
    if rule is None:
        return None
    form, pct, rationale = rule
    threshold = THRESHOLDS.get(nature, Decimal("0"))
    if gross < threshold:
        return WHTResult(form, Decimal("0"), Decimal("0"),
                         f"ต่ำกว่าเกณฑ์ {threshold} THB ไม่ต้องหัก ({rationale})")
    pct_d = Decimal(pct)
    amt = (gross * pct_d / Decimal("100")).quantize(Decimal("0.01"))
    return WHTResult(form, pct_d, amt, rationale)

if __name__ == "__main__":
    r = calc("company", "individual", "service", Decimal("50000"))
    print(f"Form: {r.form}, {r.percent}%, หัก {r.amount} บาท ({r.rationale})")
