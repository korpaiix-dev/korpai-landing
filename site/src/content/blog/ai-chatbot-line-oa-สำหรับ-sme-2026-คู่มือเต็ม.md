---
title: "AI Chatbot Line OA สำหรับ SME 2026: คู่มือเต็ม — ตั้งแต่เลือก plan, เซ็ต API, ถึง launch ใน 14 วัน"
description: "Line OA + AI Chatbot สำหรับธุรกิจไทย SME — คู่มือเต็มตั้งแต่เลือก Line OA plan, ขอ Channel Access Token, เชื่อม Claude/GPT API, ทำ knowledge base, ถึง launch รับลูกค้าจริงใน 14 วัน"
pubDate: 2026-05-01
category: "AI Chatbot"
tags:
  - Line OA
  - AI Chatbot
  - SME 2026
  - LINE Messaging API
  - Channel Access Token
readingMinutes: 13
---

> **TL;DR:** Line OA คือ "หน้าด่าน" หลักของ SME ไทยปี 2026 ลูกค้า 90% เริ่มจากที่นี่ — แต่ตอบเอง 24 ชม. ไม่ไหว AI Chatbot คือคำตอบ คู่มือนี้สอนตั้งแต่ **เลือก Line OA plan**, **ขอ Channel Access Token**, **เชื่อม API**, **ทำ knowledge base**, จน **launch จริง** ใน **14 วัน**

ปี 2026 ลูกค้าไทยติดต่อธุรกิจผ่าน 3 ช่องทาง — Line OA (60%), Facebook Messenger (25%), เว็บ chat (15%) — Line OA นำห่างเพราะคนไทยทุกวัยใช้ Line อยู่แล้ว

ปัญหาคือ: **Line OA ลูกค้า 100+/วัน = ตอบไม่ทัน** → AI Chatbot คือทางออก แต่หลาย SME ไม่รู้จะเริ่มยังไง บทความนี้คือ playbook เต็ม

> อ่านเปรียบเทียบช่องทางก่อน: [Line OA vs Messenger vs เว็บ — เลือกช่องไหนคุ้มสุดปี 2026](/blog/line-oa-vs-messenger-vs-เว็บ)

## ขั้นที่ 1 — เลือก Line OA plan (15 นาที)

Line OA มี 3 plan หลัก (อัปเดต 2026):

| Plan | ราคา/เดือน | Free message | After free | เหมาะกับ |
|---|---|---|---|---|
| Free | 0 บาท | 200 ข้อความ | ส่งไม่ได้ | ทดลอง / ธุรกิจเล็กมาก |
| Light | 1,200 บาท | 5,000 ข้อความ | 0.08 บาท/ข้อความ | SME 100-1,000 ลูกค้า/เดือน |
| Standard | 1,500 บาท | 25,000 ข้อความ | 0.04 บาท/ข้อความ | 1,000-10,000 ลูกค้า/เดือน |

**Tips:**
- **Reply message** (ตอบกลับใน 1 ชม. หลังลูกค้าทัก) = **ฟรี ไม่นับ** ทุก plan
- **Push message** (ส่งโปรโมชั่นไปหาลูกค้าเอง) = นับใน quota
- ส่วนใหญ่ AI chatbot ใช้แต่ reply → ลูกค้าทักก่อน AI ตอบ = แทบไม่นับ quota
- Plan Light หรือ Standard ก็พอสำหรับ SME ทั่วไป

## ขั้นที่ 2 — ตั้ง Line OA + เปิด Messaging API (30 นาที)

1. ไป https://www.linebiz.com/th/login/ → สมัคร Line OA
2. เปิด **Line Official Account Manager** → Settings → **Messaging API** → กด "Enable"
3. คัดลอก **Channel Secret** + กด "Issue Channel Access Token (long-lived)" → คัดลอก token
4. ที่หน้า Messaging API → ตั้ง **Webhook URL** = `https://your-domain.com/webhooks/line`
5. **เปิด "Allow bot to join group/multi-person chat"** ถ้าต้องการ
6. **ปิด "Auto-reply messages"** + **ปิด "Greeting messages"** (เพราะเราจะให้ AI handle เอง)

> ⚠️ **สำคัญ:** ต้องมี HTTPS server (cert SSL) — ถ้ายังไม่มี deploy บน VPS + Let's Encrypt ฟรี ใช้เวลา 30 นาที

## ขั้นที่ 3 — เลือก backend stack (15 นาที)

3 ทางเลือก สำหรับ Line OA + AI:

### Option A: ทำเอง Python/Node.js (เหมาะกับมีนักพัฒนา)

```python
# FastAPI handler — webhook รับจาก Line OA
@app.post("/webhooks/line")
async def line_webhook(req: Request):
    body = await req.body()
    signature = req.headers.get("x-line-signature")
    # verify signature
    events = json.loads(body)["events"]
    for event in events:
        if event["type"] == "message" and event["message"]["type"] == "text":
            text = event["message"]["text"]
            user_id = event["source"]["userId"]
            # call AI
            reply = await call_claude(text, user_id)
            # send back via Line API
            await line_reply(event["replyToken"], reply)
    return {"ok": True}
```

ใช้ Claude/GPT/Gemini API ส่งคำตอบกลับ — รายละเอียดดู [Claude vs GPT-5 vs Gemini สำหรับธุรกิจไทย 2026](/blog/claude-vs-gpt5-vs-gemini-ธุรกิจไทย-2026)

### Option B: No-code platform (เหมาะกับ DIY)

- **Manychat** — รองรับ Line OA, มี AI integration
- **Botpress** — open-source, รองรับ multi-channel
- **Botnoi** — สัญชาติไทย, รองรับ Line OA โดยตรง

> ดูรายละเอียดทำเองที่ [DIY Chatbot SME 2026 — ทำเองไม่ต้องเขียนโค้ด](/blog/diy-chatbot-sme-ไม่ต้องเขียนโค้ด)

### Option C: จ้าง agency (เหมาะกับ scale + integration ซับซ้อน)

KORP AI deploy stack: FastAPI + OpenRouter (multi-LLM) + Postgres + Redis + RAG + Line OA SDK

> ดูเปรียบเทียบราคา agency vs DIY: [AI Chatbot ราคาเท่าไหร่ 2026 — คู่มือคำนวณงบ SME](/blog/ai-chatbot-ราคา-2026-คู่มือ)

## ขั้นที่ 4 — Knowledge Base (1 วัน)

AI ตอบดีหรือไม่ขึ้นกับ **knowledge base** ที่เราป้อน

**เนื้อหาที่ควรเตรียม (สำหรับร้านค้า/บริการ):**
- catalog สินค้า + ราคา + รายละเอียด
- โปรโมชั่นเดือนนี้
- เงื่อนไขส่ง / ชำระเงิน
- คำถามที่ถามบ่อย (FAQ) 30-50 ข้อ
- เงื่อนไขสมาชิก / สะสมแต้ม
- เวลาทำการ / ที่ตั้ง / เบอร์ติดต่อ
- โปรโมชั่นพิเศษ (เฉพาะลูกค้าทักผ่าน Line)

**Format ที่เหมาะ:**
- PDF / DOCX → upload ใส่ vector database (Pinecone, pgvector)
- หรือใส่ใน Google Sheet → sync เข้า knowledge base

> RAG (Retrieval-Augmented Generation) คือเทคนิคให้ AI ตอบจากเอกสารเรา ดู [RAG คืออะไร และทำไม SME ไทยควรรู้จัก](/blog/rag-คืออะไร)

## ขั้นที่ 5 — Prompt Engineering (1 วัน)

AI ตอบ "เป็นแบรนด์เรา" หรือไม่ ขึ้นกับ system prompt

**Template prompt สำหรับ Line OA chatbot:**

```
คุณเป็น AI assistant ของร้าน [ชื่อร้าน]

หน้าที่:
- ตอบคำถามลูกค้าเรื่องสินค้า/บริการ/โปรโมชั่น
- รับ order / จองคิว
- ส่งต่อทีมงานเมื่อจำเป็น

โทน:
- สุภาพ เป็นกันเอง ไม่เป็นทางการเกิน
- ใช้ "ค่ะ/นะคะ" เพราะลูกค้า 70% เป็นผู้หญิง
- ห้ามใช้ emoji เกิน 2 ตัวต่อข้อความ

ข้อห้าม:
- ห้ามตอบเรื่องการเมือง / ศาสนา
- ห้ามรับประกันราคาที่ไม่อยู่ใน knowledge base
- ห้ามให้ส่วนลดเองโดยไม่ได้รับอนุมัติ

หาก:
- ไม่แน่ใจคำตอบ → ตอบ "ขอส่งต่อทีมงานนะคะ" + แท็ก @human_handoff
- ลูกค้าโกรธ → ขอโทษ + ส่งต่อทันที
- คำถามเรื่องเงินคืน → ส่งต่อทันที
```

> เรียนรู้การ tune prompt: [Prompt Engineering สำหรับ SME](/blog/prompt-engineering-sme-strategy)

## ขั้นที่ 6 — Test + Refine (3-5 วัน)

ก่อน launch ต้องเทสด้วย **โจทย์จริง 50-100 ข้อ**:

- คำถามทั่วไป: "ราคาเท่าไหร่?", "ส่งจังหวัดไหนได้บ้าง?"
- คำถามนอกขอบเขต: "ทำงานจันทร์ไหม?" (ถ้าเราตอบไม่ได้ → AI ต้องส่งต่อ ไม่ใช่เดา)
- คำถามที่อยากให้ upsell: "ซื้อ 1 จานพอไหม?" → AI แนะนำ "+50 บาทได้เซ็ตคู่"
- ลูกค้าโกรธ: "ของยังไม่มาเลย!" → AI ขอโทษ + ส่งต่อทันที

แต่ละรอบเทสเจอ pattern ผิด → tune prompt → เทสใหม่

## ขั้นที่ 7 — Launch + Monitor (ต่อเนื่อง)

หลัง launch ต้อง monitor:
- **Conversation log** — ดูทุกบทสนทนา หา pattern ที่ AI ตอบผิด
- **Handoff rate** — ถ้า AI ส่งต่อทีมเกิน 30% = knowledge base ขาด
- **Customer satisfaction** — ส่ง survey ทุก 10 conversation
- **API cost** — track ทุกวัน ตั้ง budget alert

**Tools ที่ใช้ monitor:**
- Grafana / Metabase สำหรับ KPI dashboard ([เปรียบเทียบ Dashboard tools](/blog/dashboard-sme-grafana-metabase-powerbi))
- Sentry สำหรับ error tracking
- LangSmith / Helicone สำหรับ LLM observability

## คำถามที่ถามบ่อย

**Q: Line OA ฟรี vs Premium ต่างกันมากไหมในเชิง chatbot?**
A: เกือบไม่ต่าง — Messaging API ใช้ได้ทุก plan ต่างกันแค่ message quota + Rich Menu บางฟีเจอร์

**Q: ใช้ AI ตอบ Line OA แล้วลูกค้าจะรู้ไหมว่าเป็น bot?**
A: ลูกค้าควรรู้ — ใส่ greeting "🤖 AI ผู้ช่วยตอบทันที 24/7 ถ้าจริงจังจะส่งต่อทีมงาน" เพื่อ trust + transparency

**Q: ถ้า AI ตอบผิด ลูกค้าโกรธ ทำยังไง?**
A: ใส่ guardrail — AI ส่งต่อทีมทันทีเมื่อเจอคำว่า "โกรธ", "complaint", "ขอผู้จัดการ" + log ทุก conversation ให้ admin review ได้

**Q: PDPA — Line OA chat data ต้องเก็บยังไง?**
A: เก็บแค่ user_id (ไม่ใช่ชื่อจริง) + ข้อความ + retention 90-180 วัน + ลบเมื่อลูกค้าขอ + ห้ามส่งเข้า public training data ของ LLM

**Q: ทำเองได้ไหม ถ้าไม่ใช่นักพัฒนา?**
A: ได้ ถ้าใช้ no-code platform แบบ Manychat / Botnoi — แต่ scale จำกัด + custom integration ทำไม่ได้ ดู [DIY Chatbot SME](/blog/diy-chatbot-sme-ไม่ต้องเขียนโค้ด)

**Q: ใช้เวลานานแค่ไหนถึงคืนทุน?**
A: ตามขนาดธุรกิจ — ร้านค้า 1,000+ ลูกค้า/เดือน คืนทุนใน 2-3 เดือน. ดู ROI calculator ใน [AI Chatbot ราคาเท่าไหร่ 2026](/blog/ai-chatbot-ราคา-2026-คู่มือ)

## บทสรุป — เริ่มยังไง?

**Path A: ทดลองด้วยตัวเอง (7-14 วัน)**
1. สมัคร Line OA Free plan
2. เปิด Messaging API + ขอ Channel Access Token
3. ใช้ Manychat / Botnoi (no-code) เชื่อม
4. ใส่ FAQ 30 ข้อ
5. test กับเพื่อน 1 สัปดาห์
6. launch กับลูกค้าจริง

**Path B: จ้าง KORP AI (3-5 สัปดาห์ go live)**
- ดู demo สดที่ [korpai.co/demo](https://korpai.co/demo) — ลองคุยกับ chatbot จริง
- ทักโจทย์ผ่าน [Line OA](https://lin.ee/Qt6Vri4) — ตอบใน 24 ชม. พร้อมใบเสนอราคา
- รวม Channel Access Token setup + RAG + monitoring + training ทีม + 14-day trial money back

ทางไหนก็ตามที่เลือก — **Line OA + AI Chatbot คือลงทุนที่คุ้มที่สุดของ SME ไทยปี 2026** เพราะลูกค้าหลักมาจากตรงนี้

---

**บทความที่เกี่ยวข้อง:**
- [AI Chatbot ราคาเท่าไหร่ 2026 — คู่มือคำนวณงบ SME](/blog/ai-chatbot-ราคา-2026-คู่มือ)
- [Line OA vs Messenger vs เว็บ — ช่องไหนคุ้มสุด](/blog/line-oa-vs-messenger-vs-เว็บ)
- [Claude vs GPT-5 vs Gemini สำหรับธุรกิจไทย](/blog/claude-vs-gpt5-vs-gemini-ธุรกิจไทย-2026)
- [DIY Chatbot SME 2026 — ทำเองไม่ต้องเขียนโค้ด](/blog/diy-chatbot-sme-ไม่ต้องเขียนโค้ด)
- [RAG คืออะไร — สำคัญสำหรับ SME ไทย](/blog/rag-คืออะไร)
- [Prompt Engineering สำหรับ SME](/blog/prompt-engineering-sme-strategy)
