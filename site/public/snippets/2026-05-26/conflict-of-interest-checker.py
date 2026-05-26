"""
conflict-of-interest-checker.py — 3-layer conflict-of-interest check for
Thai law firm intake bots. Triggered on every new matter intake BEFORE the
lawyer accepts the case. Violating ม.16 ข้อบังคับสภาทนายความ = license
revocation.

Layers:
  1. Exact ID match (national ID / juristic ID).
  2. Fuzzy name match (Levenshtein + Thai-to-roman fold).
  3. Counterparty cross-check (was the opposing party ever our client?).

Author: KORP AI — https://korpai.co
License: MIT
"""
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Callable, Iterable

# A very small, dependency-free Thai romanization fold. For production use
# pyicu or thai-segmenter; this is here to keep the snippet copy-pasteable.
_FOLD = str.maketrans({
    "ก": "k", "ข": "kh", "ค": "kh", "ง": "ng", "จ": "j", "ช": "ch",
    "ซ": "s", "ด": "d", "ต": "t", "ท": "th", "น": "n", "บ": "b",
    "ป": "p", "ผ": "ph", "ฝ": "f", "พ": "ph", "ฟ": "f", "ม": "m",
    "ย": "y", "ร": "r", "ล": "l", "ว": "w", "ส": "s", "ห": "h",
    "อ": "a", "ะ": "a", "า": "a", "ิ": "i", "ี": "i", "ึ": "ue",
    "ื": "ue", "ุ": "u", "ู": "u", "เ": "e", "แ": "ae", "โ": "o",
    "ใ": "ai", "ไ": "ai", " ": "", "่": "", "้": "",
    "๊": "", "๋": "",
})


def _fold(s: str) -> str:
    return s.lower().translate(_FOLD)


def fuzzy_ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, _fold(a), _fold(b)).ratio()


@dataclass(frozen=True)
class Party:
    name: str
    national_id: str | None = None
    juristic_id: str | None = None


@dataclass(frozen=True)
class Matter:
    matter_id: str
    client: Party
    counterparty: Party | None


@dataclass
class ConflictReport:
    has_conflict: bool
    reasons: list[str]


def check(
    new_client: Party,
    new_counterparty: Party | None,
    open_matters: Iterable[Matter],
    fuzzy_threshold: float = 0.92,
) -> ConflictReport:
    reasons: list[str] = []

    for m in open_matters:
        # Layer 1: exact ID match — strongest signal.
        if new_client.national_id and new_client.national_id == m.client.national_id:
            reasons.append(f"exact-id-client: matter={m.matter_id}")
        if (
            new_client.juristic_id
            and new_client.juristic_id == m.client.juristic_id
        ):
            reasons.append(f"exact-juristic-client: matter={m.matter_id}")

        # Layer 2: fuzzy name match.
        if fuzzy_ratio(new_client.name, m.client.name) >= fuzzy_threshold:
            reasons.append(f"fuzzy-name-client: matter={m.matter_id}")

        # Layer 3: counterparty cross-check — opposing the firm's existing client.
        if new_counterparty:
            if (
                new_counterparty.national_id
                and new_counterparty.national_id == m.client.national_id
            ):
                reasons.append(f"counterparty-was-client: matter={m.matter_id}")
            if fuzzy_ratio(new_counterparty.name, m.client.name) >= fuzzy_threshold:
                reasons.append(f"counterparty-fuzzy-client: matter={m.matter_id}")

    return ConflictReport(has_conflict=bool(reasons), reasons=reasons)
