"""Validate a Thai 13-digit Tax ID (เลขประจำตัวผู้เสียภาษี) + branch code.

Used by a B2B wholesale chatbot BEFORE issuing a full e-Tax Invoice, so a
corporate buyer can actually claim input VAT. A wrong/typo'd tax ID is the
#1 reason a wholesale customer's accountant rejects an invoice.

Checksum: d13 is the check digit. With d1..d12,
    s = sum(d[i] * (13 - i) for i in 0..11)   # weights 13,12,...,2
    check = (11 - (s % 11)) % 10
MIT licensed — adapt freely.
"""
import re

def validate_tax_id(tax_id: str) -> dict:
    digits = re.sub(r"\D", "", tax_id or "")
    if len(digits) != 13:
        return {"valid": False, "reason": "ต้องเป็นเลข 13 หลัก", "normalized": digits}
    nums = [int(c) for c in digits]
    s = sum(nums[i] * (13 - i) for i in range(12))
    check = (11 - (s % 11)) % 10
    if check != nums[12]:
        return {"valid": False, "reason": "checksum ไม่ผ่าน (เลขผิด/พิมพ์ตก)", "normalized": digits}
    return {"valid": True, "reason": "ok", "normalized": digits}


def normalize_branch(branch: str | None) -> str:
    """'สำนักงานใหญ่'/'HQ'/'' -> '00000'; otherwise zero-pad to 5 digits."""
    if not branch or str(branch).strip().lower() in {"hq", "สำนักงานใหญ่", "head office", "0"}:
        return "00000"
    d = re.sub(r"\D", "", str(branch))
    return d.zfill(5)[:5] if d else "00000"


if __name__ == "__main__":
    for t in ["0105556000009", "0105556000001", "12345"]:  # valid, bad-checksum, too-short
        print(t, validate_tax_id(t))
    print("branch:", normalize_branch("สำนักงานใหญ่"), normalize_branch("12"))
