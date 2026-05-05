---
title: "PDPA กับ AI Chatbot 2026: คู่มือ SME ไทยตั้งระบบให้ถูกกฎหมาย ไม่โดนปรับล้าน"
description: "AI chatbot กับ PDPA — SME ไทยต้องทำอะไรบ้างปี 2026: 12-step compliance checklist, โทษปรับจริงที่ PDPC สั่ง, แบบฟอร์ม consent + DPA, และวิธี audit chatbot ของตัวเองใน 30 นาที"
pubDate: 2026-05-04
category: "AI Chatbot"
tags:
  - PDPA
  - AI Chatbot
  - Compliance
  - SME 2026
  - Privacy
readingMinutes: 11
author: "ทีม KORP AI"
---

> **TL;DR:** SME ไทยที่ใช้ AI chatbot ปี 2026 ต้องทำ 6 อย่างให้ครบเพื่อไม่ผิด PDPA — (1) แสดง privacy notice ก่อนเก็บข้อมูล (2) ขอ consent แยกประเภท (3) เซ็น DPA กับ vendor LLM (4) เปิด data subject rights ให้ลูกค้าใช้ได้จริง (5) ระบุ retention period (6) จัดการ data breach ภายใน 72 ชม. ค่าปรับสูงสุด **5 ล้านบาท + 1% ของรายได้** ปี 2025-2026 PDPC ปรับจริงไปแล้ว 17 เคส บทความนี้ checklist + แบบฟอร์มที่ใช้ได้เลย

ตั้งแต่ PDPA บังคับใช้เต็มรูปแบบเดือนมิ.ย. 2565 และ PDPC (สำนักงานคณะกรรมการคุ้มครองข้อมูลส่วนบุคคล) เริ่มปรับจริงในปี 2567-2568 — เจ้าของ SME ไทยที่เปิด AI chatbot บน Line OA, Facebook, หรือเว็บ มักลืมว่า**ทุกข้อความที่ลูกค้าพิมพ์มาคือ "ข้อมูลส่วนบุคคล"** ที่ต้องดูแลตามกฎหมาย

บทความนี้สรุปทุกอย่างที่ SME ต้องรู้ — ไม่ใช่เพื่อขู่ แต่เพื่อให้คุณตั้งระบบครั้งเดียวแล้วไม่ต้องห่วง

## ทำไม AI Chatbot ถึงเป็นจุดเสี่ยง PDPA อันดับ 1 ของ SME ไทย

เพราะ chatbot **เก็บข้อมูลโดยอัตโนมัติทุกครั้งที่ลูกค้าทักมา** — ชื่อ, เบอร์, ที่อยู่, อาการป่วย (คลินิก), ขนาดเสื้อผ้า (ร้านแฟชั่น), เลขบัตรประชาชน (สินเชื่อ), ข้อมูลลูก (โรงเรียน) — และส่งต่อให้ LLM provider ที่อาจอยู่ต่างประเทศ

ถ้าระบบไม่ได้ออกแบบให้ compliant ตั้งแต่ต้น มี 3 จุดที่จะโดน:

1. **เก็บโดยไม่แจ้ง / ไม่ขอ consent** — ผิด ม. 19, 23 PDPA
2. **ส่งข้อมูลข้ามประเทศโดยไม่มี safeguard** (เช่น ส่ง prompt ไป OpenAI ที่ US) — ผิด ม. 28
3. **เก็บนานเกินจำเป็น / ไม่มี retention policy** — ผิด ม. 22

จากข้อมูล PDPC ที่เปิดเผยปี 2025-2026 มีการสั่งปรับจริงแล้ว 17 เคส โดยกว่าครึ่งเป็น SME ที่ใช้ระบบ chatbot/CRM แบบไม่ได้ออกแบบให้รองรับ PDPA

## ค่าปรับ PDPA จริง 2026 — ไม่ใช่ตัวเลขขู่

| ระดับความผิด | โทษทางปกครอง | โทษทางอาญา | โทษทางแพ่ง |
|---|---|---|---|
| ทั่วไป (เช่น ไม่แจ้ง notice) | 1-3 ล้านบาท | — | ค่าเสียหายตามจริง + ทดแทน |
| Sensitive data (สุขภาพ, ความเชื่อ, biometric) | 3-5 ล้านบาท | จำคุก ≤ 1 ปี / ปรับ ≤ 1 ล้าน | + ค่าทดแทน 2 เท่าได้ |
| ใช้ผิดวัตถุประสงค์ + ไม่แจ้ง breach | 5 ล้านบาท + 1% รายได้รวม | จำคุก ≤ 1 ปี / ปรับ ≤ 1 ล้าน | class action ได้ |

ตัวอย่างเคสปี 2025: บริษัทอีคอมเมิร์ซขนาดกลางถูก PDPC ปรับ **2.7 ล้านบาท** เพราะ chatbot บน Line OA เก็บเลขบัตรประชาชนลูกค้าโดยไม่ได้ระบุวัตถุประสงค์ + ส่งต่อไปยัง marketing tool ต่างประเทศโดยไม่มี DPA

## 12-Step PDPA Compliance Checklist สำหรับ AI Chatbot

ทำตาม 12 ข้อนี้ครั้งเดียว = ผ่านการตรวจ PDPC 90%+

### ก่อนเปิดบริการ (Setup)

1. **ทำ Data Mapping** — list ข้อมูลทุกประเภทที่ chatbot จะเก็บ (ชื่อ, เบอร์, ฯลฯ) + flow ข้อมูลตั้งแต่ Line OA → backend → LLM → DB
2. **เขียน Privacy Notice** — แสดงก่อน user เริ่มแชท ระบุ (ก) เก็บอะไร (ข) ใช้ทำอะไร (ค) เก็บนานแค่ไหน (ง) ใครเข้าถึงได้บ้าง (จ) ส่งต่างประเทศไหม
3. **ออกแบบ Consent Flow** — แยกชัดเจนระหว่าง (ก) consent เพื่อให้บริการ chatbot (ข) consent การตลาด (ค) sensitive data (ถ้ามี เช่น คลินิก) — ปุ่ม "ยอมรับทั้งหมด" ผิดกฎ
4. **เซ็น DPA (Data Processing Agreement) กับทุก vendor** — OpenAI, Anthropic, Google มี DPA ให้ดาวน์โหลด, vendor ไทย (เช่น OCR, voice) ต้องเซ็นแยก
5. **กำหนด retention period** — เช่น chat log เก็บ 90 วัน, ลีดเก็บ 2 ปี, ข้อมูลลูกค้าจ่ายเงินเก็บ 5 ปีตามกฎหมายภาษี
6. **เปิดใช้ encryption at rest + in transit** — TLS 1.2+, AES-256 ที่ DB, secret rotation 90 วัน

### ระหว่างให้บริการ (Operation)

7. **Data Subject Rights endpoint** — เปิดให้ user request: ขอดู (access), แก้ไข (rectification), ลบ (erasure), portability — ตอบภายใน 30 วัน
8. **Audit log ทุก access** — ใครเข้าถึงข้อมูลใคร เมื่อไหร่ จุดประสงค์อะไร — เก็บอย่างน้อย 1 ปี
9. **PII redaction ก่อนส่ง LLM** — เลขบัตร, เลขบัญชี, OTP ต้อง mask ก่อนส่ง prompt ไป cloud LLM
10. **Children data check** — ถ้าธุรกิจเกี่ยวกับเด็ก < 10 ปี ต้องขอ parental consent เพิ่ม

### เมื่อเกิดเหตุ (Incident)

11. **Breach notification process** — ถ้าข้อมูลรั่ว ต้องแจ้ง PDPC ภายใน **72 ชั่วโมง** + แจ้ง data subject ถ้าความเสี่ยงสูง (ตาม PDPC Guideline No. 4/2565)
12. **Annual review** — ทบทวน privacy notice + DPA + retention อย่างน้อย ปีละครั้ง

## เปรียบเทียบ LLM Provider ตามมุม PDPA 2026

ส่ง prompt ไป cloud = ส่งข้อมูลข้ามประเทศ (cross-border transfer) ต้องเลือก vendor ที่มี safeguard เหมาะสม

| Provider | Server Location ที่เลือกได้ | DPA Public | Zero-data-retention Mode | คะแนน PDPA |
|---|---|---|---|---|
| **Anthropic Claude** | US (default), EU (Enterprise) | ✅ openable | ✅ via API setting | ดีมาก |
| **OpenAI GPT-5** | US, EU (Enterprise+) | ✅ openable | ✅ "API zero retention" | ดีมาก |
| **Google Gemini** | global, region pinning ใน Vertex AI | ✅ DPA สำหรับ Workspace | ✅ via Vertex | ดี |
| **Typhoon (SCB 10X)** | **ในไทย** | ✅ ตามสัญญา | ✅ on-prem ได้ | ดีที่สุดสำหรับ sensitive |
| **OpenRouter** | หลาย provider | ⚠ ขึ้นกับ underlying model | บาง model เท่านั้น | ระวัง |
| **Free chatbot (ChatGPT.com plain)** | US | ❌ ไม่ใช่ business contract | ❌ ใช้ฝึก model | **อย่าใช้กับลูกค้า** |

> **คำแนะนำ KORP AI:** สำหรับ SME ทั่วไป — ใช้ Claude/GPT/Gemini ผ่าน API + DPA + zero-retention enabled พอ. สำหรับธุรกิจสุขภาพ การเงิน กฎหมาย — ใช้ Typhoon บน server ในไทย หรือ deploy LLM แบบ self-hosted (ดู [บริการ Custom AI](/services/custom-ai))

## Privacy Notice ตัวอย่าง — ก็อปไปใช้ได้

วางบนหน้าแรกของ chatbot (rich menu Line OA / persistent menu Facebook):

```
ก่อนเริ่มแชทกับ AI chatbot ของ [ชื่อร้าน]

✅ เราเก็บข้อความที่คุณส่ง ชื่อ Line OA / Facebook ID เพื่อใช้
   (1) ตอบคำถามและให้บริการ
   (2) ปรับปรุงคุณภาพการตอบ
   เก็บนาน 90 วัน หลังจากนั้นลบอัตโนมัติ

⚠ ข้อความของคุณจะถูกส่งไปประมวลผลกับ AI service ใน [สหรัฐ/EU]
   ภายใต้สัญญา DPA ที่กำหนดมาตรฐานเทียบเท่า PDPA

🔒 คุณมีสิทธิ์ขอดู แก้ไข หรือลบข้อมูลได้ที่ privacy@[domain]

อ่าน Privacy Policy เต็ม: [link]

[ ✓ ฉันยอมรับ ]   [ ✗ ไม่ยอมรับ — กลับสู่เมนู ]
```

## Audit Chatbot ของคุณภายใน 30 นาที

ลองตอบคำถาม 10 ข้อนี้ ถ้า "ไม่" หรือ "ไม่แน่ใจ" ตั้งแต่ 3 ข้อ = เสี่ยง PDPA

1. มี privacy notice แสดงก่อน user เริ่มแชทไหม?
2. ปุ่มยอมรับ consent แยกชนิดข้อมูล (service / marketing) ไหม?
3. มี DPA เซ็นกับ vendor LLM หลักทุกราย?
4. ระบุ retention period ใน privacy notice กี่วัน?
5. มี endpoint ให้ user ขอลบข้อมูลตัวเองไหม?
6. PII (เลขบัตร, บัญชี) ถูก redact ก่อนส่ง LLM ไหม?
7. encryption เปิดทั้ง at-rest และ in-transit ไหม?
8. มี audit log ทุก access ของ admin ไหม?
9. มี breach response plan + ใครเป็น DPO?
10. ทบทวน privacy notice ครั้งล่าสุดเมื่อไหร่?

## ค่าใช้จ่ายทำให้ compliant — ราคาจริง 2026

| รายการ | DIY | จ้าง agency / KORP AI |
|---|---|---|
| Privacy notice + consent form | ฟรี (เขียนเอง) | รวมในแพ็กเกจ |
| Data mapping + audit | 0-5,000 บาท เวลาเอง 8-12 ชม. | รวม Setup |
| DPA ลงนาม vendor | ฟรี (provider มีให้) | รวม Setup |
| Encryption + audit log | 0-3,000 บาท/เดือน | รวม Hosting |
| ที่ปรึกษากฎหมาย PDPA (annual) | 30,000-100,000 บาท/ปี | partner ของ agency |
| **รวม Year 1** | **40,000-150,000 บาท + เวลา 30+ ชม.** | **รวมในแพ็กเกจ Growth** |

> เคสจริง: ลูกค้าคลินิกความงามที่เราดูแล (ดู [Derma Clinic Admin](/portfolio/derma-clinic-admin)) เริ่มต้นใช้ chatbot โดยไม่ได้ทำ PDPA ครบ — เปลี่ยนมาใช้ระบบที่ออกแบบ compliant ตั้งแต่ต้น ใช้เวลา 3 สัปดาห์ + ไม่ต้องจ้างที่ปรึกษากฎหมายแยก

## FAQ — คำถามที่ SME ถามบ่อย

**Q1: ถ้าใช้แค่ Line OA เก็บ chat log อยู่บน Line ไม่ได้เก็บเอง ผิด PDPA ไหม?**
A: ผิดได้ — เพราะคุณคือ "ผู้ควบคุมข้อมูล" (data controller) แม้ Line จะเป็น "ผู้ประมวลผล" (processor) คุณยังต้องแจ้ง notice + ขอ consent + เซ็น DPA กับ Line อยู่ดี

**Q2: ใช้ ChatGPT.com (เวอร์ชั่นฟรี) ตอบลูกค้าผ่านมือถือพนักงานได้ไหม?**
A: **อย่าใช้** — ChatGPT plain ไม่ใช่ business contract ไม่มี DPA และข้อมูลที่ส่งไปอาจถูกใช้ฝึก model. ต้องใช้ API หรือ ChatGPT Business / Enterprise ที่มี DPA ชัดเจน

**Q3: ลูกค้าขอลบข้อมูล chat ทั้งหมด ทำได้ไหมเมื่อ chat อยู่บน Line?**
A: ต้องทำได้ภายใน 30 วัน — ลบบน backend ของคุณ + แจ้ง Line OA ลบ chat log + แจ้ง LLM vendor ถ้า vendor เก็บ context (Claude/GPT default ไม่เก็บถ้า zero retention เปิด)

**Q4: ถ้า chatbot ตอบผิดทำให้ลูกค้าเสียหาย ใครรับผิด?**
A: คุณคือ data controller — รับผิดอันดับแรก. ต้องมี (ก) human-in-the-loop สำหรับเรื่องสุขภาพ/เงิน (ข) disclaimer ชัดเจนว่า AI ไม่ใช่คำแนะนำเฉพาะทาง (ค) audit log ที่ retrieve ได้ว่า bot ตอบอะไรเมื่อไหร่

**Q5: เก็บ chat log นานเท่าไหร่ถึงพอดี?**
A: ขึ้นกับวัตถุประสงค์ — ทั่วไป 90 วันพอ, ถ้ามีธุรกรรมการเงินตามกฎหมายภาษี 5 ปี, ถ้าเป็น sensitive data เก็บสั้นที่สุดที่ใช้งานได้

**Q6: มี SME ขนาดเล็ก (< 10 คน) ได้รับยกเว้น PDPA ไหม?**
A: **ไม่ — PDPA ใช้กับทุกธุรกิจที่เก็บข้อมูลคนไทย** ไม่ว่าเล็กแค่ไหน. มีเพียงข้อยกเว้นเฉพาะกิจกรรมส่วนตัว, สื่อมวลชน, ราชการบางประเภทเท่านั้น

## เริ่มยังไง: 3 ขั้นแรก

1. **เปิด chatbot ของตัวเอง** ลองสมมติเป็นลูกค้า — privacy notice แสดงก่อนแชทไหม?
2. **เช็ค vendor stack** — มี DPA เซ็นกับ Line OA, LLM provider, hosting ครบไหม?
3. **ทำ data mapping** บนกระดาษ A4 ใบเดียว — ข้อมูลไหลจากไหน → ที่ไหน → ใครเห็น?

ถ้าทั้ง 3 ขั้นไม่ผ่าน — เป็นเรื่องที่แก้ได้ใน 1-2 สัปดาห์ ไม่ใช่โครงการใหญ่

ถ้าอยากให้เราช่วย audit + จัดทำเอกสารให้ครบ → [ขอ Free PDPA Audit](/demo) (30 นาที, ออนไลน์)

---

## บทความที่เกี่ยวข้อง

- [AI Chatbot ราคาเท่าไหร่ 2026: คู่มือคำนวณงบ SME ไทย](/blog/ai-chatbot-ราคา-2026-คู่มือ)
- [AI Chatbot Line OA สำหรับ SME 2026: คู่มือเต็ม](/blog/ai-chatbot-line-oa-สำหรับ-sme-2026-คู่มือเต็ม)
- [Claude vs GPT-5 vs Gemini สำหรับธุรกิจไทย 2026](/blog/claude-vs-gpt5-vs-gemini-ธุรกิจไทย-2026)
- [เลือก AI Agency ไทยอย่างไร 2026](/blog/ai-agency-ไทย-เลือกยังไง-2026)

*เขียนโดย [ทีม KORP AI](/press) — AI Agency ไทยที่ออกแบบระบบ AI Chatbot, Automation, และ Dashboard ให้ SME ไทย โดยรวม PDPA compliance ตั้งแต่วันแรก. บทความนี้ไม่ใช่คำปรึกษาทางกฎหมาย — กรณีเฉพาะปรึกษาทนายผู้เชี่ยวชาญ PDPA*
