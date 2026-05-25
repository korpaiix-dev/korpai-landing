"""
per-client-namespace-guard.py — PDPA cross-client leak guard for accounting RAG.
Enforces namespace separation + TIN-in-chunk check before sending context to LLM.
KORP AI · 2026 · MIT
"""
import re
from typing import Iterable

TIN_IN_TEXT = re.compile(r"\b(\d{13})\b")

class CrossClientLeak(Exception):
    pass

def filter_chunks(current_tin: str, chunks: Iterable[dict]) -> list[dict]:
    """
    Drop any chunk whose embedded TINs don't match current_tin.
    Each chunk: {"id": str, "text": str, "namespace": str}
    """
    safe = []
    for c in chunks:
        # Hard rule 1: namespace must match
        if c.get("namespace") != f"client_{current_tin}":
            raise CrossClientLeak(
                f"namespace mismatch: chunk {c['id']} from {c.get('namespace')}, "
                f"current=client_{current_tin}"
            )
        # Hard rule 2: any TIN embedded inside chunk text must equal current_tin
        tins = set(TIN_IN_TEXT.findall(c.get("text", "")))
        rogue = tins - {current_tin}
        if rogue:
            # log to audit + drop
            audit_log_drop(c, current_tin, rogue)
            continue
        safe.append(c)
    return safe

def audit_log_drop(chunk: dict, current_tin: str, rogue: set[str]) -> None:
    # In production: write to immutable audit_log table (see audit-log-schema.sql)
    print(f"AUDIT: dropped chunk {chunk['id']} — current={current_tin}, rogue={rogue}")

if __name__ == "__main__":
    # Demo
    chunks = [
        {"id":"a1","text":"VAT input 2026-Q1 TIN 0105560123456 …","namespace":"client_0105560123456"},
        {"id":"a2","text":"yoy revenue TIN 0105561999999 …","namespace":"client_0105560123456"},
    ]
    print(filter_chunks("0105560123456", chunks))
