---
title: "AI Agency ไทย 2026: เลือกยังไงไม่โดนหลอก — checklist 10 ข้อก่อนเซ็นสัญญา"
description: "ปี 2026 มี AI agency ผุดขึ้นมาเป็นดอกเห็ด ราคาตั้งแต่หมื่นถึงล้าน ขอบเขตงานคล้ายกันแต่คุณภาพต่างกันมาก คู่มือนี้ช่วย SME คัดกรองด้วย 10 checklist ที่ใช้ได้จริง"
pubDate: 2026-05-01
category: "SME Strategy"
tags:
  - AI Agency
  - SME 2026
  - Selection Guide
  - Vendor Evaluation
  - PDPA
readingMinutes: 9
---

ปี 2026 ตลาด AI Agency ไทยขยายตัวเร็วมาก จากเดิมที่นับได้ไม่ถึง 20 เจ้าในปี 2023 ตอนนี้พิมพ์ค้น "AI Agency กรุงเทพ" ใน Google เจอเป็นร้อย หลายเจ้าเปิดใหม่ในรอบ 6 เดือน ทำเว็บสวย เคลม case study ดูดี แต่พอเริ่มงานจริงเจอปัญหาตั้งแต่: ราคาบาน, ส่งงานช้า, deploy แล้วไม่ work, AI ตอบมั่ว, support หาย

บทความนี้คือ **checklist 10 ข้อ** ที่ SME ใช้ตัดสินใจได้ก่อนเซ็นสัญญา — ใช้ได้ทุกเจ้า รวม KORP AI ด้วย ถ้าเจ้าไหนตอบไม่ได้หรือเลี่ยง คือสัญญาณเตือน

## 1. ขอ demo สด ไม่ใช่ video case study

video case study ตัดต่อได้ — ขอเข้าระบบจริงที่เจ้านั้นทำให้ลูกค้าได้ ลองคุยกับ AI ตัวจริง 3-5 นาที ดูว่าตอบยังไง รับมือคำถามนอกสคริปต์ได้ไหม ถ้า agency บอก "ขออนุญาตลูกค้าก่อน" รอ 1-2 วันก็ยอมรับได้ ถ้ายื้อยาวกว่านั้นแปลว่าเขาไม่มีของจริง

> KORP AI: ดู demo สดที่ [korpai.co/demo](https://korpai.co/demo) ได้เลย ไม่ต้องสมัคร

## 2. ถามว่าใช้ LLM ตัวไหน — ถ้าตอบ "Claude อย่างเดียว" หรือ "GPT-4 อย่างเดียว" ระวัง

ปี 2026 model ใหม่ออกทุก 2-3 เดือน Claude Sonnet 4.6, GPT-5, Gemini 2.5 Pro — แต่ละตัวเก่งคนละด้าน Agency ที่ดีต้องมี **multi-LLM strategy**: ใช้ผ่าน gateway อย่าง OpenRouter ที่ย้าย model ได้ทันที ไม่ต้อง rewrite ระบบเมื่อ vendor ออกรุ่นใหม่

ถ้าเจ้าไหนยังบอก "Claude 3.5" หรือ "GPT-4o" = อัพเดทช้าไปอย่างน้อย 6 เดือน

## 3. ราคา — รวมค่า API LLM หรือคิดแยก?

นี่คือ **gotcha ที่ใหญ่ที่สุด** ของวงการนี้ในปี 2026:
- ค่า project: 50,000-500,000 บาท
- ค่า API LLM ต่อเดือน: 2,000-30,000 บาท ขึ้นกับ traffic

agency จำนวนมากเสนอราคา project แล้วไม่บอกว่า "ค่า API ลูกค้าจ่ายเอง" → ลูกค้าเปิดบิล Anthropic/OpenAI เดือนแรกแล้วช็อค

**ถามตรงๆ:** "API cost รวมในแพ็กเกจไหม? ถ้าไม่รวม คาดว่าเดือนละกี่บาทตาม traffic ที่ผมมี?"

## 4. ดูแลรายเดือน — มีหรือไม่ + ทำอะไรให้บ้าง

AI Chatbot ไม่ใช่ "ทำเสร็จแล้วใช้ตลอด" ต้อง update knowledge base, retrain prompt เมื่อสินค้าเปลี่ยน, fix bugs เมื่อ AI เริ่มตอบมั่ว

**คำถามที่ต้องได้ scope ชัด:**
- ดูแลรายเดือนรวมอะไรบ้าง? (server, monitoring, prompt update, knowledge base sync)
- ราคาเดือนละเท่าไหร่ (หลัง launch)?
- ตอบ support ภายในกี่ชม.?
- ถ้า AI ตอบผิดในวันหยุดทำยังไง?

## 5. เจ้าของ data + export ได้ไหม

ใครเป็นเจ้าของ:
- บทสนทนาลูกค้า?
- knowledge base ที่สร้าง?
- prompt ที่ tune แล้ว?

ถ้า agency บอก "เป็นของเรา" หรือ "อยู่ในระบบของเรา" → เลิกคุยทันที **ทุกอย่างต้องเป็นของลูกค้า** export เป็น JSON/CSV ได้ ทุก asset ต้อง portable

## 6. PDPA — เข้าใจจริงหรือแค่พูด

PDPA คือ พรบ. คุ้มครองข้อมูลส่วนบุคคล มีมาตั้งแต่ 2562 แต่หลาย agency ยังตอบไม่ได้ว่า:
- เก็บข้อมูลลูกค้าที่ไหน (server ในไทย/ต่างประเทศ)?
- ใช้ explicit consent ก่อน opt-in chatbot ไหม?
- มี data retention policy ไหม?
- ส่งข้อมูลลูกค้าเข้า public training data ของ LLM ไหม? (สำคัญ — ถ้าใช้ OpenAI ChatGPT ตรงๆ default = yes)

## 7. ทีมลูกค้าใช้ต่อเองได้ไหม — มี training + เอกสารไหม

agency ที่อยากผูก vendor lock-in จะทำให้ลูกค้าใช้เองไม่ได้ ต้องจ้างเขาตลอดไป

ถาม:
- มี documentation user manual ไหม?
- training ทีมลูกค้ากี่ชั่วโมง?
- ถ้าทีมลูกค้าอยากเปลี่ยน prompt เองได้ไหม?
- ระบบ admin มี UI ไหม หรือต้อง edit code?

## 8. ส่งของช่วงสั้น 1-2 สัปดาห์ vs รอ 3 เดือน

แนวคิด "agile delivery" — ส่งของให้ใช้จริงทุก 1-2 สัปดาห์ ไม่ใช่หายไป 3 เดือนแล้วโผล่กับ "deliverable สมบูรณ์"

agency ที่ทำงานแบบเก่า (waterfall): brief → spec → design → build 8 สัปดาห์ → demo → ลูกค้าบอก "ไม่ใช่อย่างนี้" → กลับไปแก้อีก 4 สัปดาห์

agency ที่ทำงานแบบใหม่ (iterative): brief → MVP 2 สัปดาห์ส่งให้ใช้ → feedback → ปรับ 1 สัปดาห์ → ขยาย scope → repeat

ถาม: "delivery cadence ของทีมเป็นยังไง? นานสุดที่ผมไม่ได้เห็น progress คือกี่วัน?"

## 9. มี guardrail กัน AI ตอบมั่วไหม

AI hallucinate ได้ ถ้า agency ไม่มี guardrail = ลูกค้าจะเจอกรณี chatbot บอกราคาผิด สัญญาบริการผิด นัดหมายผิด

ระบบ guardrail พื้นฐานที่ควรมี:
1. **Knowledge base whitelisting** — AI ตอบจากเอกสารที่ลูกค้าอนุมัติเท่านั้น
2. **Handoff to human** — ถ้า AI ไม่แน่ใจ ส่งต่อทีมขายแทนเดา
3. **Conversation log** — ทุกบทสนทนา record + review ได้
4. **Tone + content filter** — กรองคำหยาบ คำที่ไม่ควรพูด

## 10. ยกเลิกได้ไหม + ผูกมัดกี่ปี

red flag ที่สำคัญสุด:
- ผูกมัด 12-24 เดือน ยกเลิกเสียค่าปรับ
- ค่า setup สูง + monthly แพง = sunk cost ให้ออกยาก
- ไม่มี trial period

**Standard ที่ควรเป็น (ปี 2026):**
- ทดลอง 14 วันแรก คืนเงินถ้าไม่พอใจ
- ดูแลรายเดือนยกเลิกได้ล่วงหน้า 30 วัน ไม่มีค่าปรับ
- annual contract เป็น optional (มีส่วนลด ~15%) ไม่บังคับ
- ข้อมูล + asset เป็นของลูกค้า 100% ออกจากระบบไปได้

---

## ตัวอย่าง response card

ลองส่ง checklist 10 ข้อนี้เข้าไปถาม agency 2-3 เจ้า เปรียบเทียบคำตอบ — เจ้าที่ตอบชัด มีตัวอย่างจริง ไม่เลี่ยงคำถาม คือเจ้าที่มีความรู้จริง ไม่ใช่ขายฝัน

ถ้าอยากลองส่งให้ KORP AI ตอบ ทักได้ที่ [Line OA](https://lin.ee/Qt6Vri4) หรือ [Facebook](https://www.facebook.com/korpaiix) — เราตอบทุกข้อภายใน 24 ชม. พร้อม screenshot ระบบจริงให้ดู

ดูบริการได้ที่ [korpai.co/services](https://korpai.co/services) · ลองสด demo template 3 ธุรกิจที่ [korpai.co/demo](https://korpai.co/demo)
