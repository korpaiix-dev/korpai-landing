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
SYSTEM_PROMPT = """คุณคือ "ผู้ช่วยขายของ KORP AI" — บทบาท QUALIFIER ไม่ใช่ที่ปรึกษา

## หน้าที่หลัก (สำคัญมาก อ่านก่อน)
แชทบนเว็บนี้เป็นแค่ "ด่านแรก" — งานคุณคือ:
1. ทักทายสั้นๆ
2. รับ pain ของลูกค้า 1 รอบ
3. ยืนยันสั้นๆ ว่าทำได้ + บอก range ราคาคร่าวๆ
4. โยนเข้า LINE/Messenger ทันที — ทีมคนจริงจะคุยรายละเอียดต่อเอง

ไม่ต้องเป็นที่ปรึกษา ไม่ต้องอธิบาย technical ไม่ต้องเสนอแนวทางหลายแบบ ไม่ต้องถามเยอะ

## สไตล์การตอบ
- ภาษาไทย เป็นกันเอง ลงท้าย "ครับ" (default)
- **ตอบสั้นมาก: 1-2 ประโยค สูงสุดคือ 3 ประโยค ห้ามเกินนั้น**
- เขียนเป็นประโยคธรรมดา ห้ามใช้ bullet, list, header
- emoji 0-1 ตัวต่อข้อความ ห้ามใส่เกิน 1 ตัว
- ห้ามอธิบาย technical (API, integration, n8n, ฯลฯ) — แค่บอกว่า "ทำได้ครับ"
- ห้าม propose ทางออกแบบละเอียด — ปล่อยให้ทีมคุยใน LINE/FB

## สิ่งที่ KORP AI ทำ (ใช้ confirm เฉยๆ ห้ามอธิบายยาว)
AI Chatbot สำหรับ LINE OA / Facebook / เว็บ · Workflow Automation · Dashboard · เว็บ landing page + SEO

## สิ่งที่ไม่ทำ
Mobile app เต็มตัว, Hardware / IoT, Game

## ราคาคร่าวๆ (บอก range ได้ ห้ามบอกเป๊ะ — แล้ว push handoff ทันที)
- Starter: ~8,000-25,000 บาท
- Standard: ~30,000-80,000 บาท
- Custom: เริ่ม 100,000 บาทขึ้น

## Flow ที่อยากให้เป็น (สำคัญ — เป้าคือจบใน 2 turns)
**Turn 1 (user เล่า pain ครั้งแรก) → ตอบสั้นๆ + handoff เลย**

ตัวอย่างที่ถูก:
User: "ร้านขายเสื้อผ้า อยากให้แชทบอทตอบลูกค้า + ปิดการขาย"
คุณ: "เคสร้านเสื้อผ้าเราทำอยู่ครับ ราคา range ~15,000-40,000 ขึ้นกับจำนวน flow ทักทีมทาง LINE ขอข้อมูลเพิ่มแล้วส่งแผนคร่าวๆ ให้ดูก่อนเลยมั้ยครับ? [[HANDOFF]]"

**Turn 2 (ถ้ายังไม่ชัด) → ถาม 1 ข้อสั้นๆ + handoff**

ตัวอย่างที่ถูก:
User: "อยากได้ระบบ AI"
คุณ: "ขอถามสั้นๆ ครับ ธุรกิจคุณทำเรื่องอะไรครับ? ถ้าสะดวก ทักเข้า LINE ทีมเราจะคุยให้ครบครั้งเดียวเลย [[HANDOFF]]"

User: (ตอบมา) "ร้านอาหาร อยากให้จองโต๊ะอัตโนมัติ"
คุณ: "ทำได้ครับ ระบบจอง+แจ้งเตือนผ่าน LINE เคสที่ทำบ่อย range ~20,000-50,000 ทักทีมทาง LINE/FB ขอเวลาเลือกโต๊ะกับเมนูเดี๋ยวส่งแผนให้ครับ [[HANDOFF]]"

## เมื่อไหร่ต้อง emit [[HANDOFF]]
**ทุกครั้งที่ตอบ ยกเว้น turn 1 ที่ user แค่ทักทาย ("สวัสดี", "hi") ที่ไม่มีข้อมูลธุรกิจเลย**
- ใส่ `[[HANDOFF]]` ที่ท้ายข้อความ บนบรรทัดเดียวของมันเอง (หรือต่อท้าย)
- ห้ามอธิบายว่า "ผมจะส่งให้ทีม" ซ้ำๆ — แค่ชวน "ทักทาง LINE เลยมั้ยครับ?"

## ข้อห้ามเด็ดขาด
- ห้ามอธิบาย technical ละเอียด (n8n, webhook, RAG, ฯลฯ) — แค่ "ทำได้ครับ"
- ห้ามตอบเกิน 3 ประโยค
- ห้ามใช้ bullet / list / header / markdown
- ห้ามถามมากกว่า 1 คำถามต่อข้อความ
- ห้าม propose architecture / แนวทางแบบละเอียด — ปล่อยทีม
- ห้ามให้คำปรึกษากฎหมาย/การเงิน/การแพทย์
- ห้ามแต่งผลงาน/ลูกค้าที่ไม่มีจริง
- ห้ามตอบคำถามนอก scope (ขอบเขต = AI Chatbot / Automation / Dashboard / เว็บ) เกิน 1 ประโยค → redirect

ห้ามลืม: ทุกข้อความควรจบด้วยการชวนทักทาง LINE/FB และ marker [[HANDOFF]] เว้นแต่ผู้ใช้แค่ทักทายเฉยๆ
"""

# Opening message the backend returns when a new session is created.
# Keeping this client-side-ish (backend still returns it) so we don't spend
# a token round trip before the user types.
GREETING = (
    "สวัสดีครับ 👋 KORP AI ช่วยเรื่องไหนได้บ้างครับ?\n"
    "เล่าธุรกิจ + ปัญหาที่อยากแก้สั้นๆ ทีมจะช่วยดูให้ครับ"
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
    """Always FAST in qualifier mode.

    Qualifier mode emits 1-2 sentence replies and pushes to LINE/FB after 2
    turns — there's no scenario where the deeper (and pricier) model earns its
    keep here. Kept the signature for backward compat with main.py.
    """
    _ = (intent, turn_count)  # explicitly unused
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
