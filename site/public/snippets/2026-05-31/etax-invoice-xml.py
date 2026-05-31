"""Build a minimal e-Tax Invoice payload (ETDA-style fields) + sanity checks.

NOTE: This is a *reference skeleton* of the fields a wholesale bot must collect
and validate before handing off to a certified e-Tax service provider, which
submits the signed XML to the Revenue Department by the 15th of the following
tax month. It is NOT a full ETDA RDXML document and is not digitally signed.
MIT licensed.
"""
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP

VAT_RATE = Decimal("0.07")
q2 = lambda x: Decimal(x).quantize(Decimal("0.01"), ROUND_HALF_UP)

@dataclass
class Line:
    desc: str
    qty: Decimal
    unit_price: Decimal
    @property
    def amount(self): return q2(self.qty * self.unit_price)

@dataclass
class Buyer:
    name: str
    tax_id: str            # 13 digits, validate with thai-tax-id-validator.py
    branch: str = "00000"
    address: str = ""

def build_invoice(buyer: Buyer, lines: list[Line], doc_no: str, issue_date: str) -> dict:
    sub = q2(sum((l.amount for l in lines), Decimal("0")))
    vat = q2(sub * VAT_RATE)
    total = q2(sub + vat)
    problems = []
    if len(buyer.tax_id) != 13 or not buyer.tax_id.isdigit():
        problems.append("tax_id ต้องเป็นเลข 13 หลัก")
    if sub <= 0:
        problems.append("ยอดก่อน VAT ต้อง > 0")
    return {
        "valid": not problems, "problems": problems,
        "docType": "T03",  # T03 = ใบกำกับภาษีเต็มรูป
        "docNo": doc_no, "issueDate": issue_date,
        "buyer": buyer.__dict__,
        "lines": [{"desc": l.desc, "qty": str(l.qty), "unit": str(l.unit_price),
                   "amount": str(l.amount)} for l in lines],
        "subTotal": str(sub), "vatRate": "7", "vat": str(vat), "grandTotal": str(total),
    }

if __name__ == "__main__":
    inv = build_invoice(
        Buyer("บจก. ตัวอย่างค้าส่ง", "0105556000001", "00000", "กรุงเทพฯ"),
        [Line("กระดาษ A4 80g (ลัง)", Decimal("10"), Decimal("520")),
         Line("ปากกาลูกลื่น (โหล)", Decimal("24"), Decimal("96"))],
        "INV-2026-000128", "2026-05-31")
    import json; print(json.dumps(inv, ensure_ascii=False, indent=2))
