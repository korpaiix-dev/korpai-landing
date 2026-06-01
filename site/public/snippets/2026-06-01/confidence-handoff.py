"""confidence-handoff.py — KORP AI (Layer 4)
Make "I'm not sure" a first-class, allowed answer. When retrieval support is
weak or the question is out of scope, hand off to a human instead of guessing.
MIT licensed.
"""
from dataclasses import dataclass

@dataclass
class Retrieval:
    top_score: float        # cosine similarity of best knowledge-base chunk (0..1)
    n_supporting: int       # how many chunks cleared the relevance floor
    in_scope: bool          # did an intent classifier place this in a known domain?

# Tuned on real traffic; start conservative and relax as the KB matures.
SCORE_FLOOR = 0.62
MIN_SUPPORT = 1

def should_answer(r: Retrieval) -> tuple[bool, str]:
    if not r.in_scope:
        return False, "out_of_scope"
    if r.top_score < SCORE_FLOOR:
        return False, f"low_similarity({r.top_score:.2f}<{SCORE_FLOOR})"
    if r.n_supporting < MIN_SUPPORT:
        return False, "no_supporting_chunk"
    return True, "ok"

def respond(r: Retrieval, draft_answer: str) -> dict:
    ok, reason = should_answer(r)
    if ok:
        return {"action": "reply", "text": draft_answer, "reason": reason}
    return {
        "action": "handoff",
        "text": "ขอส่งต่อให้ทีมงานช่วยยืนยันให้แน่ใจนะคะ เดี๋ยวรีบตอบกลับค่ะ 🙏",
        "reason": reason,
    }

if __name__ == "__main__":
    print(respond(Retrieval(0.81, 3, True), "เปิด 10:00-21:00 ค่ะ"))
    print(respond(Retrieval(0.41, 0, True), "น่าจะราคาประมาณ..."))
    print(respond(Retrieval(0.90, 5, False), "เรื่องคดีความ..."))
