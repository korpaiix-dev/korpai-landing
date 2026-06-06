#!/usr/bin/env python3
"""
Thai vs English token-efficiency estimator.
Thai text is tokenized less efficiently than English by most Western tokenizers,
so the same meaning costs ~2-3x more tokens (the 'Thai token tax'). Thai-specialized
open models (e.g. Typhoon) often tokenize Thai more efficiently — one reason to
consider self-hosting Typhoon when Thai volume is high.

This gives a quick *estimate* without pulling a specific tokenizer. For production,
measure with your real provider's tokenizer.
"""
from dataclasses import dataclass


@dataclass
class Estimate:
    chars: int
    est_tokens_generic: int   # generic western tokenizer (Thai tax applied)
    est_tokens_thai_opt: int  # Thai-optimized tokenizer (e.g. Typhoon)
    thai_tax_x: float


def is_thai(ch: str) -> bool:
    return "฀" <= ch <= "๿"


def estimate(text: str,
             eng_chars_per_token: float = 4.0,
             thai_chars_per_token_generic: float = 1.6,
             thai_chars_per_token_optimized: float = 3.2) -> Estimate:
    thai_chars = sum(1 for c in text if is_thai(c))
    other_chars = len(text) - thai_chars

    eng_tokens = other_chars / eng_chars_per_token
    thai_tokens_generic = thai_chars / thai_chars_per_token_generic
    thai_tokens_opt = thai_chars / thai_chars_per_token_optimized

    generic = round(eng_tokens + thai_tokens_generic)
    optimized = round(eng_tokens + thai_tokens_opt)
    tax = (thai_tokens_generic / thai_tokens_opt) if thai_tokens_opt else 1.0
    return Estimate(len(text), generic, optimized, round(tax, 2))


if __name__ == "__main__":
    sample = ("สวัสดีค่ะ ร้านเปิดกี่โมง มีที่จอดรถไหม แล้วราคาคอร์สนวดเท่าไหร่คะ "
              "Do you have parking and what time do you open?")
    e = estimate(sample)
    print(f"chars                       : {e.chars}")
    print(f"est tokens (generic/western): {e.est_tokens_generic}")
    print(f"est tokens (Thai-optimized) : {e.est_tokens_thai_opt}")
    print(f"Thai token tax (x)          : {e.thai_tax_x}")
    print("\nHigh Thai volume + this tax is a real argument for a Thai-optimized "
          "model like Typhoon. Always confirm with the real tokenizer.")
