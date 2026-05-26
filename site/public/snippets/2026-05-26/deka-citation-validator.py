"""
deka-citation-validator.py — Thai Supreme Court (คำพิพากษาศาลฎีกา) citation validator.

Why this exists:
LLMs hallucinate Thai Deka citations ~31% of the time on specific queries
(KORP AI internal eval, Feb 2026, n=420). When a lawyer cites a non-existent
ฎีกา in court, it's contempt + permanent credibility loss.

Pattern: retrieve-then-cite-then-verify.

Author: KORP AI — Thai AI agency for SME law firms.
URL: https://korpai.co/blog/ai-chatbot-สำนักงานกฎหมาย-ทนายความ-law-firm-sme-2026
License: MIT
"""
import re
from dataclasses import dataclass
from typing import Iterable

# Thai Supreme Court citation patterns commonly seen in pleadings:
#   "ฎีกาที่ 1234/2567"        -> case 1234, year 2567 (B.E.)
#   "คำพิพากษาศาลฎีกาที่ 1234/2567"
#   "ฎ.1234/2567"
DEKA_RE = re.compile(
    r"(?:ฎีกาที่|คำพิพากษาศาลฎีกาที่|ฎ\.)\s*([0-9]{1,6})\s*/\s*(2[345][0-9]{2})"
)


@dataclass(frozen=True)
class DekaCite:
    case_no: int
    year_be: int  # Buddhist Era

    @property
    def year_ce(self) -> int:
        return self.year_be - 543

    def key(self) -> str:
        return f"{self.case_no}/{self.year_be}"


def extract_citations(text: str) -> list[DekaCite]:
    """Extract every Deka citation from free Thai text."""
    out: list[DekaCite] = []
    for m in DEKA_RE.finditer(text):
        out.append(DekaCite(case_no=int(m.group(1)), year_be=int(m.group(2))))
    return out


def validate(
    citations: Iterable[DekaCite],
    corpus_lookup,  # callable(key:str) -> bool
) -> tuple[list[DekaCite], list[DekaCite]]:
    """
    Returns (valid, invalid). `corpus_lookup` is your DB/index check — e.g.
    a sqlite/Postgres query against the ingested ฎีกา corpus.
    """
    valid, invalid = [], []
    for c in citations:
        if corpus_lookup(c.key()):
            valid.append(c)
        else:
            invalid.append(c)
    return valid, invalid


def must_be_safe(llm_answer: str, corpus_lookup) -> str:
    """
    Drop-in guardrail. Replace any Deka citation that is not in the corpus
    with [UNVERIFIED] so the lawyer never accidentally files a hallucinated
    citation. Designed to be called between LLM output and any storage/UI.
    """
    found = extract_citations(llm_answer)
    if not found:
        return llm_answer
    _, invalid = validate(found, corpus_lookup)
    if not invalid:
        return llm_answer
    redacted = llm_answer
    for c in invalid:
        # Strip any of the three citation forms for this case
        redacted = re.sub(
            r"(?:ฎีกาที่|คำพิพากษาศาลฎีกาที่|ฎ\.)\s*"
            + re.escape(str(c.case_no))
            + r"\s*/\s*"
            + re.escape(str(c.year_be)),
            f"[UNVERIFIED ฎีกา {c.case_no}/{c.year_be}]",
            redacted,
        )
    return redacted


if __name__ == "__main__":
    # Smoke test — pretend corpus has only one citation.
    known = {"1234/2567"}
    text = (
        "ตามคำพิพากษาศาลฎีกาที่ 1234/2567 และ ฎีกาที่ 9999/2567 "
        "ศาลวินิจฉัยว่า..."
    )
    print("Extracted:", [c.key() for c in extract_citations(text)])
    print("Guarded :", must_be_safe(text, known.__contains__))
