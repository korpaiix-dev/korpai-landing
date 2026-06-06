#!/usr/bin/env python3
"""
PDPA data-residency gate.
Before sending a prompt to a CLOUD API, scan it for sensitive personal data.
If found, block the cloud call and force the request onto a self-hosted/on-prem
model so the data never leaves your infrastructure. This is the concrete mechanism
behind "when PDPA forces self-host."

Heuristic detectors (extend for your domain). Not legal advice.
"""
import re
from dataclasses import dataclass

PATTERNS = {
    "thai_national_id": re.compile(r"\b\d{1}[- ]?\d{4}[- ]?\d{5}[- ]?\d{2}[- ]?\d{1}\b"),
    "thai_phone":       re.compile(r"\b0\d{1,2}[- ]?\d{3}[- ]?\d{3,4}\b"),
    "email":            re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "credit_card":      re.compile(r"\b(?:\d[ -]?){13,16}\b"),
    "thai_passport":    re.compile(r"\b[A-Z]{1,2}\d{6,7}\b"),
}
# Sensitive-category keywords (health/finance) — Thai + English
SENSITIVE_KW = ["โรค", "ผลตรวจ", "วินิจฉัย", "เงินเดือน", "บัญชีธนาคาร",
                "เลขบัตร", "diagnosis", "salary", "bank account"]


@dataclass
class Decision:
    allow_cloud: bool
    route: str          # "cloud" or "local"
    reasons: list


def classify(text: str) -> Decision:
    hits = [name for name, rx in PATTERNS.items() if rx.search(text)]
    kw = [k for k in SENSITIVE_KW if k.lower() in text.lower()]
    reasons = hits + [f"kw:{k}" for k in kw]
    if reasons:
        return Decision(False, "local", reasons)
    return Decision(True, "cloud", [])


def gate(text: str):
    d = classify(text)
    if not d.allow_cloud:
        # route to self-hosted model; data stays on-prem
        return {"route": "local", "blocked_cloud": True, "reasons": d.reasons}
    return {"route": "cloud", "blocked_cloud": False, "reasons": []}


if __name__ == "__main__":
    for t in ["ราคาคอร์สนวดเท่าไหร่คะ",
              "ผลตรวจของคุณสมชาย เลขบัตร 1-2345-67890-12-3 ครับ"]:
        print(repr(t[:40]), "->", gate(t))
