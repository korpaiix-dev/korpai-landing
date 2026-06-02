"""thai-token-estimator.py — rough token estimate for mixed Thai/English text.

Companion to: /blog/ai-chatbot-ต้นทุน-token-ต่อข้อความ-sme-2026
MIT licensed.

Why this exists: Thai is tokenized far less efficiently than English by GPT/Claude/Gemini
BPE/SentencePiece tokenizers (often ~2-3x more tokens per character). For accurate
billing use the vendor's real tokenizer (tiktoken / Anthropic count_tokens / Gemini
count_tokens). This heuristic is for quick budgeting when you only have plain strings.
"""
import re

# Heuristic ratios (chars per token). English ~4 chars/token; Thai script far denser.
EN_CHARS_PER_TOKEN = 4.0
TH_CHARS_PER_TOKEN = 1.6   # Thai chars frequently become ~1 token each -> expensive

_THAI = re.compile(r"[฀-๿]")

def estimate_tokens(text: str) -> int:
    thai_chars = len(_THAI.findall(text))
    other_chars = len(text) - thai_chars
    tokens = thai_chars / TH_CHARS_PER_TOKEN + other_chars / EN_CHARS_PER_TOKEN
    return max(1, round(tokens))

def thai_premium(text: str) -> float:
    """How many x more tokens this text costs vs the same length all-English."""
    est = estimate_tokens(text)
    english_equiv = max(1, len(text) / EN_CHARS_PER_TOKEN)
    return est / english_equiv

if __name__ == "__main__":
    samples = [
        "สวัสดีค่ะ ร้านเปิดกี่โมง แล้วมีที่จอดรถไหมคะ",
        "Hi, what time do you open and is there parking?",
        "ขอใบเสนอราคาติดตั้ง AI chatbot บน Line OA สำหรับร้านอาหาร 2 สาขา",
    ]
    for s in samples:
        print(f"{estimate_tokens(s):4d} tok | {thai_premium(s):.2f}x vs EN | {s}")
