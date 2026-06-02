"""rag-topk-limiter.py — cap RAG context to a token budget, keep the most relevant.

Companion to: /blog/ai-chatbot-ต้นทุน-token-ต่อข้อความ-sme-2026
MIT licensed.

Stuffing whole documents into every prompt is the most common way SME bots overspend
on input tokens. Retrieve many candidates, then pack only the highest-scoring chunks
that fit your budget (greedy knapsack by score density).
"""
from dataclasses import dataclass
from typing import List

@dataclass
class Chunk:
    id: str
    text: str
    score: float          # similarity score from your vector DB (higher = better)

def est_tokens(text: str) -> int:
    thai = sum(1 for c in text if "฀" <= c <= "๿")
    other = len(text) - thai
    return max(1, round(thai / 1.6 + other / 4))

def pack_context(chunks: List[Chunk], max_tokens: int = 1200, min_score: float = 0.0) -> List[Chunk]:
    """Greedy pack: drop low-similarity chunks, then add best-scoring until budget hit."""
    eligible = sorted((c for c in chunks if c.score >= min_score),
                      key=lambda c: c.score, reverse=True)
    picked, used = [], 0
    for c in eligible:
        t = est_tokens(c.text)
        if used + t > max_tokens:
            continue            # skip; a later smaller high-score chunk may still fit
        picked.append(c)
        used += t
    return picked

if __name__ == "__main__":
    demo = [
        Chunk("faq#1", "ราคาติดตั้งเริ่มต้นและแพ็กเกจรายเดือนของ AI chatbot", 0.91),
        Chunk("faq#2", "นโยบายการคืนเงินภายใน 7 วันหลังเริ่มใช้งาน", 0.74),
        Chunk("faq#3", "ประวัติความเป็นมาและรางวัลที่บริษัทเคยได้รับ", 0.38),  # low score -> dropped
        Chunk("faq#4", "เวลาทำการและช่องทางติดต่อทีมงาน", 0.66),
    ]
    chosen = pack_context(demo, max_tokens=60, min_score=0.5)
    print("kept:", [c.id for c in chosen],
          "| dropped low-score: faq#3",
          "| total tok:", sum(est_tokens(c.text) for c in chosen))
