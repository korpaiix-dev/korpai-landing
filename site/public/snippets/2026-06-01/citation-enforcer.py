"""citation-enforcer.py — KORP AI (Layer 3: retrieve-cite-verify)
Every factual claim must point back to a retrieved source id like [src:faq#7].
Claims that assert a fact without a citation are suppressed, so the bot cannot
smuggle an un-grounded line past the user.

NOTE on Thai: Thai has no inter-word spaces and rarely uses .!? terminators, so
naive sentence splitting fails. In production, segment with a Thai tokenizer
(e.g. PyThaiNLP `sent_tokenize`). Here we split on newlines/clause spaces, and
the design contract is: **emit one claim per line** from your LLM (ask for it in
the system prompt). MIT licensed.
"""
import re

CITE = re.compile(r"\[src:[a-z0-9_\-]+#\d+\]", re.I)
FACT_HINT = re.compile(
    r"(ราคา|บาท|เปิด|ปิด|รับประกัน|คืนเงิน|ส่วนลด|มีของ|สต็อก|ส่งฟรี|วันที่|เวลา|"
    r"\bprice\b|\bopen\b|\brefund\b|\bwarranty\b|\d)", re.I)

def split_claims(text: str):
    # One claim per line is the contract; fall back to .!? and Thai space-clauses.
    parts = re.split(r"\n+|(?<=[.!?。])\s+", text.strip())
    out = []
    for p in parts:
        out.extend(s for s in re.split(r"\s{2,}", p) if s.strip())
    return [s.strip() for s in out if s.strip()]

def enforce(answer: str, valid_ids: set[str] | None = None):
    kept, dropped = [], []
    for claim in split_claims(answer):
        cites = CITE.findall(claim)
        asserts_fact = bool(FACT_HINT.search(claim))
        cited_ok = bool(cites) and (
            valid_ids is None
            or all(c.lower() in valid_ids for c in (x.lower() for x in cites))
        )
        if asserts_fact and not cited_ok:
            dropped.append(claim)                       # un-grounded fact -> remove
        else:
            kept.append(CITE.sub("", claim).strip())    # strip cite tags from output
    return {"text": "\n".join(k for k in kept if k),
            "dropped": dropped, "grounded": not dropped}

if __name__ == "__main__":
    import json
    answer = (
        "ชาเขียวมะลิ 35 บาทค่ะ [src:menu#12]\n"
        "ส่งฟรีทั่วประเทศไม่มีขั้นต่ำเลยค่ะ\n"      # no citation -> dropped
        "ขอบคุณที่สนใจนะคะ"
    )
    print(json.dumps(enforce(answer, {"[src:menu#12]"}), ensure_ascii=False, indent=2))
