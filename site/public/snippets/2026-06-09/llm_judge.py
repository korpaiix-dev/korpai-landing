#!/usr/bin/env python3
"""
llm_judge.py — LLM-as-a-judge scorer (0..1) for open-ended chatbot answers.

2026 best practice: an LLM judge agrees with humans ~80-90% at a fraction of
the cost — but you MUST calibrate it against humans first (see judge_calibration.py).
This builds a strict rubric prompt and parses a numeric score; wire `call_llm()`
to whatever provider you use (Claude / GPT / Gemini / OpenRouter). (c) KORP AI 2026 MIT
"""
import json, re

JUDGE_RUBRIC = """คุณคือกรรมการตรวจคำตอบแชตบอตอย่างเข้มงวด ให้คะแนน 0.0–1.0
เกณฑ์:
- 1.0 = ครบทุกประเด็นใน expected, ถูกต้อง, ไม่แต่งข้อมูลที่ไม่มีจริง
- 0.5 = ถูกบางส่วน หรือขาดประเด็นสำคัญ
- 0.0 = ผิด, แต่งราคา/นโยบายที่ไม่มีจริง, หรือเรื่อง 'trap' ที่ควรตอบว่าไม่รู้แต่กลับเดา
ตอบกลับเป็น JSON เท่านั้น: {"score": <0..1>, "reason": "<สั้นๆ>"}"""

def build_judge_prompt(question, expected_points, answer, category=""):
    return (f"{JUDGE_RUBRIC}\n\n[ประเภท]: {category}\n[คำถามลูกค้า]: {question}\n"
            f"[ประเด็นที่คำตอบที่ดีต้องมี]: {expected_points}\n[คำตอบของบอต]: {answer}\n\nJSON:")

def call_llm(prompt: str) -> str:
    """REPLACE ME. Use temperature=0 for a stable judge."""
    raise NotImplementedError("Wire call_llm() to your LLM provider (temperature=0)")

def judge(question, expected_points, answer, category=""):
    raw = call_llm(build_judge_prompt(question, expected_points, answer, category))
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        return {"score": 0.0, "reason": "judge returned no JSON", "raw": raw}
    try:
        out = json.loads(m.group(0))
        out["score"] = max(0.0, min(1.0, float(out.get("score", 0))))
        return out
    except Exception as e:
        return {"score": 0.0, "reason": f"parse error: {e}", "raw": raw}

if __name__ == "__main__":
    print("Import judge() into your golden_set_runner, or test with a stubbed call_llm().")
