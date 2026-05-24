"""
order-export-pdpa-mask.py
Export orders to CSV with PII automatically masked for non-admin roles.
Prevents accidental data leaks when CS/ops download daily reports.

PDPA: customer phone + name + address = personal data (sec.6/sec.26).
Mask by default; admins with explicit purpose can request unmasked export
which gets audit-logged.

Companion to: https://korpai.co/blog/ai-chatbot-ขนส่ง-โลจิสติกส์-logistics-sme-2026
MIT — KORP AI Automation.
"""
import csv
import re
from datetime import datetime, timedelta


PII_COLUMNS = {"recipient", "phone", "address1", "id_card", "email"}


def mask_phone(p: str) -> str:
    if not p:
        return ""
    digits = re.sub(r"\D", "", p)
    if len(digits) < 4:
        return "***"
    return "*" * (len(digits) - 4) + digits[-4:]


def mask_name(n: str) -> str:
    if not n:
        return ""
    parts = n.split()
    if len(parts) == 1:
        return parts[0][0] + "***"
    return parts[0] + " ***"


def mask_address(a: str) -> str:
    # Keep province + postal — useful for ops; mask street/house number
    if not a:
        return ""
    last = a.split()[-1]
    return f"*** {last}"


def mask_email(e: str) -> str:
    if not e or "@" not in e:
        return "***"
    user, dom = e.split("@", 1)
    return user[0] + "***@" + dom


MASKERS = {
    "phone": mask_phone,
    "recipient": mask_name,
    "address1": mask_address,
    "email": mask_email,
}


def export_orders(orders, output_path, role="cs", purpose=None, audit_log=None):
    """
    role: 'cs' | 'ops' | 'admin'
    purpose: required when role == 'admin' and you want unmasked output.
    audit_log: callable(role, purpose, count, masked) for compliance trail.
    """
    unmasked = role == "admin" and bool(purpose)
    masked_count = 0

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        if not orders:
            return
        fieldnames = list(orders[0].keys())
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for o in orders:
            row = dict(o)
            if not unmasked:
                for col in PII_COLUMNS:
                    if col in row:
                        masker = MASKERS.get(col, lambda v: "***" if v else "")
                        row[col] = masker(row[col])
                        masked_count += 1
            w.writerow(row)

    if audit_log:
        audit_log(role=role, purpose=purpose, count=len(orders),
                  masked=(not unmasked), at=datetime.utcnow())


if __name__ == "__main__":
    sample = [{"id": "X1", "recipient": "สมชาย ใจดี", "phone": "0812345678",
               "address1": "39/12 รามคำแหง", "amount": 450}]
    export_orders(sample, "/tmp/orders-masked.csv", role="cs")
    print("Wrote /tmp/orders-masked.csv")
