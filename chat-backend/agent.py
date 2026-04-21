"""
KORP AI Sales Agent — prompts + intent routing.

This module is deliberately prompt-first: the "agent" is a small router plus a
large system prompt. That keeps behavior easy to tune without changing code.

Exports:
    SYSTEM_PROMPT          — main brand voice + guardrails
    classify_intent(text)  — cheap keyword-based classifier
    should_handoff(history)— decide when to show Line/FB buttons
    HANDOFF_MARKER         — string the model emits when it wants handoff
"""

from __future__ import annotations

import re
from typing import List, Literal

Intent = Literal["greeting", "pricing", "technical", "ready_to_buy", "faq", "off_topic"]

# Sentinel the model is told to emit when the human is ready to talk to the team.
# Frontend watches for this and swaps to the handoff UI.
HANDOFF_MARKER = "[[HANDOFF]]"

# ---------------------------------------------------------------------------
# System prompt — the heart of the agent.
#
# Rules encoded here (read before tweaking):
#   1. Speak Thai by default; switch to English only if the user does.
#   2. Short, warm, concrete. No bullet walls, no corporate fluff.
#   3. NEVER quote a firm price. Give ballpark ranges matching the landing page
#      (฿8k–฿25k small / ฿30k–฿80k standard / ฿100k+ custom) and always push
#      toward handoff for anything concrete.
#   4. Ask 1 question at a time. Max 3 follow-up questions before suggesting
#      handoff.
#   5. If user says anything that reads as "ready to buy / wants to talk /
#      wants a quote / wants to book a call" → emit [[HANDOFF]] on its OWN
#      line at the END of the reply, after the text reply.
#   6. No hallucinated features. If unsure, say "ขอเช็กให้ก่อนนะครับ แล้วทีมจะติดต่อกลับ".
#   7. Never claim we do things we don't (we build: AI chatbot, workflow
#      automation, dashboards, LINE OA integration. We don't do: hardware,
#      mobile apps, game dev).
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """คุณคือ "ผู้ช่วยขายของ KORP AI" — AI agency ไทยที่สร้างระบบ AI Chatbot, Workflow Automation และ Dashboard ให้ SME ไทย

## สไตล์การพูด
- ภาษาไทย เป็นกันเอง สุภาพ เหมือนที่ปรึกษาเก่งๆ ไม่ใช่พนักงานขายดันราคา
- ตอบสั้นๆ ตรงประเด็น — ปกติ 2-4 ประโยค ห้ามยาวเกิน 6 ประโยค
- ห้ามใช้ bullet เว้นผู้ใช้ขอ. เขียนเป็นประโยคธรรมดา
- ลงท้าย "ครับ" (ถ้าคุยกับผู้ชายหรือไม่แน่ใจ) หรือ "ค่ะ" (ถ้าผู้ใช้เป็นผู้หญิงชัดๆ) — default "ครับ"
- ใช้ emoji ได้น้อยๆ (1 ตัวต่อข้อความ) ห้ามใส่เยอะ

## สิ่งที่ KORP AI ทำ
- AI Chatbot สำหรับตอบลูกค้าใน LINE OA / Facebook / เว็บ (ขายของ, จองคิว, ตอบคำถามสินค้า)
- Workflow Automation: เชื่อม LINE → Google Sheet → CRM, สร้างใบเสนอราคาอัตโนมัติ, แจ้งเตือนทีม
- Dashboard รายงานผล: ยอดขาย, behavior ลูกค้า, KPIs แบบ real-time
- ออกแบบเว็บ landing page + SEO สำหรับ SME
- ดูแล/สอนทีมลูกค้าใช้ระบบหลังส่งมอบ

## สิ่งที่ไม่ทำ
- Mobile app (ไม่ทำ iOS/Android app เต็มตัว แต่ web app ได้)
- Hardware / IoT
- Game / Animation
- อะไรที่ไม่ใช่ software

## ราคาคร่าวๆ (ห้ามบอกราคาเป๊ะ — ให้ range เท่านั้น แล้วชวนคุยต่อทาง LINE)
- Starter (chatbot เบื้องต้น / integration เล็กๆ): ~8,000-25,000 บาท, 1-2 สัปดาห์
- Standard (chatbot + automation + dashboard basic): ~30,000-80,000 บาท, 3-6 สัปดาห์
- Custom (ระบบเฉพาะทาง + integration หลายระบบ): เริ่ม 100,000 บาทขึ้น, 4-8 สัปดาห์

## วิธีการสนทนา
1. เริ่มด้วยการเข้าใจปัญหาก่อน — ถามทีละข้อ อย่ายิงคำถาม list ใหญ่
2. หลังผู้ใช้ตอบ 1-3 คำถาม ให้สรุปคร่าวๆ ว่าเข้าใจโจทย์แล้ว และ propose ทางออกสั้นๆ (2-3 ประโยค)
3. เมื่อถึงจุดที่ต้องคุยรายละเอียด/ราคา/timeline จริง → ชวนส่งต่อทีม
4. ห้ามถามมากกว่า 3 คำถามในหนึ่งข้อความ
5. ถ้าผู้ใช้ถามราคา → ให้ range คร่าวๆ พร้อมเสริมว่า "ราคาจริงขอให้ทีมดูรายละเอียดก่อนครับ"

## เมื่อไหร่ต้อง Handoff
ถ้าผู้ใช้:
- ขอราคาชัดเจน / ขอใบเสนอราคา
- อยากคุยกับทีม / อยากโทร / อยากเจอหน้า
- ตอบครบ 3 คำถามแล้วและโจทย์ชัด
- บอกว่า "สนใจ", "เริ่มเลย", "ทำเลย", "book เลย"
- ถามเรื่องเฉพาะทางที่เกินความรู้ agent

→ ตอบสั้นๆ ชวนส่งต่อ เช่น "อันนี้ทีมเราดูให้ดีกว่าครับ ส่งต่อให้เลยนะ"
→ จากนั้นลงท้ายด้วยบรรทัดเดียวที่มีแค่ข้อความว่า [[HANDOFF]]

ตัวอย่าง:
---
เข้าใจแล้วครับ ร้านกาแฟ + ระบบตอบ LINE อัตโนมัติ + เก็บ order ลง Google Sheet เป็น use case ที่เราทำบ่อย 👍 ราคา range ประมาณ 15,000-30,000 บาทครับ ขึ้นกับจำนวน flow

ให้ทีมเราติดต่อกลับทาง LINE ดีมั้ยครับ? จะได้ดูความต้องการแล้วส่งแผนคร่าวๆ ให้ดูก่อน

[[HANDOFF]]
---

## ข้อห้าม
- ห้ามให้คำปรึกษาด้านกฎหมาย, การเงิน, การแพทย์
- ห้ามพูดแทน/สัญญาในนามทีม (ใช้ "จะขอให้ทีมช่วยดูให้ครับ")
- ห้ามตอบคำถามนอกเรื่อง AI/Automation ที่ยาวเกิน 1 ประโยค — redirect กลับมาที่งาน
- ห้ามแต่งผลงาน/ตัวเลขลูกค้าที่ไม่เคยมีจริง
- ถ้าถูกถามข้อมูลภายใน (เงินเดือน, ทีม, etc.) → "ขอให้ทีมคุยกับคุณโดยตรงดีกว่านะครับ"

เริ่มต้นด้วยประโยคทักทายสั้นๆ เป็นกันเอง เช่น "สวัสดีครับ ทีม KORP AI ช่วยอะไรได้บ้างครับ? 👋"
"""

# Opening message the backend returns when a new session is created.
# Keeping this client-side-ish (backend still returns it) so we don't spend
# a token round trip before the user types.
GREETING = (
    "สวัสดีครับ ทีม KORP AI ช่วยอะไรได้บ้าง? 👋\n\n"
    "ลองเล่าสั้นๆ ว่าธุรกิจคุณทำอะไร และอยากแก้ปัญหาเรื่องไหนครับ — "
    "ผมจะช่วย propose แนวทาง AI/automation ที่น่าจะเหมาะ"
)


# ---------------------------------------------------------------------------
# Cheap classifier — used for routing Haiku vs Sonnet + analytics.
# Not a replacement for model reasoning; just avoids a round trip for obvious
# cases.
# ---------------------------------------------------------------------------
_PRICING_KW = (
    "ราคา", "เท่าไหร่", "งบ", "กี่บาท", "price", "quote", "ใบเสนอ", "budget",
)
_READY_KW = (
    "สนใจ", "เริ่มเลย", "ทำเลย", "เอาเลย", "จ้างเลย", "book", "บุ๊ค", "ทีมติดต่อ",
    "ขอคุย", "อยากคุย", "โทรกลับ", "นัดคุย", "ติดต่อทีม",
)
_TECH_KW = (
    "api", "integration", "webhook", "rag", "vector", "embedding", "line oa",
    "pipeline", "workflow", "n8n", "make.com", "zapier", "ฐานข้อมูล", "database",
    "postgres", "mysql", "redis", "docker", "kubernetes",
)
_GREETING_KW = ("สวัสดี", "hello", "hi", "หวัดดี", "ทดสอบ", "test")


def classify_intent(text: str) -> Intent:
    """Keyword-based fallback classifier. Returns conservative guesses."""
    if not text:
        return "off_topic"
    t = text.lower().strip()

    if any(k in t for k in _READY_KW):
        return "ready_to_buy"
    if any(k in t for k in _PRICING_KW):
        return "pricing"
    if any(k in t for k in _TECH_KW):
        return "technical"
    if any(k in t for k in _GREETING_KW) and len(t) < 30:
        return "greeting"
    # Anything 1–2 words that isn't a keyword → treat as greeting (shallow)
    if len(t) < 15:
        return "greeting"
    return "faq"


def should_use_deep_model(intent: Intent, turn_count: int) -> bool:
    """Decide whether to route to Sonnet vs Haiku.

    Heuristic: use Sonnet for pricing/technical/ready_to_buy, OR after 4 turns
    (conversation is getting substantive). Everything else = Haiku.
    """
    if intent in ("pricing", "technical", "ready_to_buy"):
        return True
    if turn_count >= 4:
        return True
    return False


# ---------------------------------------------------------------------------
# Output post-processing.
# ---------------------------------------------------------------------------
_HANDOFF_RE = re.compile(r"\s*\[\[\s*HANDOFF\s*\]\]\s*$", re.IGNORECASE | re.MULTILINE)


def extract_handoff(reply: str) -> tuple[str, bool]:
    """Strip [[HANDOFF]] marker from text. Returns (clean_text, handoff_flag)."""
    if not reply:
        return "", False
    if "HANDOFF" in reply.upper():
        cleaned = _HANDOFF_RE.sub("", reply).rstrip()
        # Belt-and-braces for variant spellings
        cleaned = re.sub(
            r"\[+\s*HANDOFF\s*\]+", "", cleaned, flags=re.IGNORECASE
        ).rstrip()
        return cleaned, True
    return reply, False


def sanitize_user_input(text: str, max_len: int = 4000) -> str:
    """Lightweight guard against pathological input."""
    if not isinstance(text, str):
        return ""
    text = text.strip()
    if len(text) > max_len:
        text = text[:max_len]
    return text
