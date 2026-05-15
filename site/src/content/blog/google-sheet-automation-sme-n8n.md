---
title: "Google Sheet + n8n สำหรับ SME ไทย: ทำ automation จาก Sheet เดียวภายใน 1 วัน"
description: "Step-by-step ใช้ Google Sheet เป็น 'database น้องใหม่' สำหรับ SME — เชื่อม n8n อัตโนมัติส่ง Line/Email/CRM, 5 use case จริงพร้อม template ใช้ฟรี"
pubDate: 2026-04-22
updatedDate: 2026-05-16
category: "Automation"
tags: ["Google Sheet", "n8n", "Automation", "SME", "Database", "Workflow"]
readingMinutes: 8
heroImage: "/assets/img/sheet-n8n-flow.jpg"
author: "ทีม KORP AI"
---

## ทำไม Google Sheet + n8n = stack คุ้มสุดสำหรับ SME ไทย

ลูกค้า SME ที่เริ่มต้น automation 90% มี Google Sheet อยู่แล้ว — เก็บลูกค้า, stock, order, นัดหมาย ฯลฯ เพียงแต่ทุกอย่างทำมือ

n8n (อ่านว่า "n-eight-n") คือ open-source automation tool ที่ self-host ได้ฟรี · เชื่อม Google Sheet กับระบบอื่นได้แทบทุกเจ้า · ราคาถูกกว่า Zapier 5–10 เท่า

stack นี้เหมาะกับ SME เพราะ:

- **ไม่ต้องเรียน database** — ทีมเข้าใจ Sheet อยู่แล้ว
- **เห็นข้อมูลจริงที่หน้าจอ** — ไม่ใช่ตาราง backend ลึกลับ
- **ต้นทุน 0–500 บาท/เดือน** — Google Sheet ฟรี · n8n self-host ที่ VPS 200–500 บาท/เดือน
- **scale ได้ถึง ~10,000 row** — เกินนั้นค่อย migrate ไป Supabase/Postgres

ถ้าโจทย์ใหญ่กว่านี้แล้วอยากปรึกษาว่าควร migrate ไป custom system ตอนไหน [ดู service custom AI](/services/custom-ai) ของเรา

## 5 Use case ที่ทำได้ใน 1 วัน

### Use case 1: Form กรอก → Sheet → Line แจ้งทีมขาย

**Flow:** Google Form → Google Sheet (ใหม่ row) → n8n trigger → ส่ง Line ทีมขายพร้อมรายละเอียด lead

**ค่าทำ:** ฟรี (Google Form + Sheet + n8n self-host)

**เวลา setup:** 30 นาที

**ผลลัพธ์ลูกค้า KORP:** Lead reply เร็วขึ้นจาก 4 ชม. → 3 นาที · close rate +35%

### Use case 2: Sheet stock → ตัดอัตโนมัติเมื่อ shopee order มา

**Flow:** Shopee Open API webhook → n8n → ลด stock ใน Sheet · ถ้า stock < 5 ส่ง Line เจ้าของให้สั่ง

**ค่าทำ:** ฟรี (ถ้า Shopee API ใช้ฟรี tier)

**เวลา setup:** 2 ชม. (ติด API ครั้งแรกใช้เวลา)

**ผลลัพธ์:** ของหมดสต็อกโดยไม่รู้ตัว = 0 (เคย พลาด ขายของหมดเดือนละ 5–10 ครั้ง)

### Use case 3: Booking calendar → Sheet → reminder Line ก่อนถึงเวลา

**Flow:** Google Calendar event → n8n watch trigger → 1 ชม. ก่อนถึงเวลาส่ง Line OA หาลูกค้า

**ค่าทำ:** ฟรี

**เวลา setup:** 45 นาที

**ผลลัพธ์ลูกค้า spa จริง:** No-show ลดจาก 22% → 8% (อ่าน [เคส wellness spa เต็ม ๆ](/portfolio/wellness-spa-booking))

### Use case 4: รายงานยอดขายรายวัน — ส่ง Line CEO ทุก 18:00

**Flow:** Cron 18:00 → n8n อ่าน Sheet ยอดวันนี้ → format ข้อความ → ส่ง Line Notify

**ค่าทำ:** ฟรี

**เวลา setup:** 20 นาที

**ผลลัพธ์:** CEO ไม่ต้องถามทีมเช้าทุกวัน · ทีมไม่ต้องทำ daily report

### Use case 5: ลูกค้าทักแชทบอกชื่อ → AI สรุป → เก็บ Sheet → ส่ง welcome email

**Flow:** Line/Messenger webhook → n8n → OpenAI extract ข้อมูล → Sheet → SendGrid welcome email

**ค่าทำ:** ~300 บาท/เดือน (OpenAI + SendGrid)

**เวลา setup:** 3 ชม.

**ผลลัพธ์:** Onboard ลูกค้าใหม่อัตโนมัติ · ทีม customer success มี backlog 0 ([อ่านวิธีใช้ AI กับ chatbot ใน blog](/blog/ai-chatbot-ร้านอาหาร-คาเฟ่))

## Setup n8n + Google Sheet ใน 60 นาที

### Step 1: Setup n8n (15 นาที)

ทางเลือก:

- **n8n Cloud** ($20/mo, ใช้เลย) — เหมาะถ้าไม่อยากดูแล server
- **Self-host บน VPS** (DigitalOcean $6/mo + Docker) — เหมาะถ้าต้องการคุมค่าใช้จ่าย

```bash
docker run -it --rm -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n
```

เปิด http://localhost:5678 ตั้ง admin password เสร็จ

### Step 2: Connect Google Sheet (10 นาที)

n8n → Credentials → Google Sheet OAuth2 → กดให้สิทธิ์ → ใส่ Sheet ID

Sheet ID หาจาก URL: `docs.google.com/spreadsheets/d/[SHEET_ID_HERE]/edit`

### Step 3: Build flow แรก (30 นาที)

ตัวอย่าง flow "Lead from Google Form → Line":

1. **Trigger:** "On New Row" Google Sheet
2. **Action:** "Format Message" (Function node) — รวมข้อมูลเป็นข้อความสวย
3. **Action:** "HTTP Request" → POST ไป Line Notify webhook URL
4. **Test:** กรอก form → เห็น Line message ขึ้นภายใน 30 วินาที

### Step 4: Activate + monitor (5 นาที)

กดปุ่ม Active บนมุมขวาบน · เปิด Executions tab ดูทุก run · พังตรงไหนคลิกดู error log

## 5 ข้อควรระวัง (จากเคสจริงลูกค้า KORP)

1. **Sheet เกิน 5,000 row → ช้า** — query เริ่ม timeout · ควร migrate ไป database
2. **Concurrent write → ข้อมูลทับ** — ถ้า 5 form กรอกพร้อมกัน บาง row อาจหาย — แก้ด้วย queue หรือ append-only mode
3. **Google rate limit** — fetch Sheet เกิน 60 ครั้ง/นาทีจะโดน throttle
4. **OAuth expire ทุก 6 เดือน** — n8n cloud reload เอง · self-host ต้องมา re-auth
5. **Sheet ถูกแก้ผิดโดยพนักงาน** — flow พังหมด · ควรล็อค header row + protect sheet

## เมื่อไหร่ Sheet+n8n เริ่มไม่พอ

อยู่ที่ stack ที่ดีจะแสดงสัญญาณก่อนพัง:

- เกิน 5,000 row และ query ช้า > 5 วินาที
- ต้อง multi-user concurrent edit เกิน 3 คน
- ต้อง audit log ละเอียด (ใครแก้อะไรเมื่อไหร่)
- ต้อง role-based permission ลึก
- ต้องรองรับ traffic > 100,000 event/เดือน

ตอนเจอ 2/5 ข้อข้างบน คือเวลา migrate ไป Supabase / Postgres + dashboard custom ([อ่านเรื่อง dashboard SME เพิ่มเติม](/blog/dashboard-sme-grafana-metabase-powerbi))

## Template ฟรี — แจกใช้เลย

ทีม KORP เปิด 3 template ฟรีให้ลูกค้า SME (ทักมาขอที่ Line OA หรือเว็บ):

1. **Lead Form → Line** — flow Use case 1 ครบ
2. **Daily Sales Report** — flow Use case 4 ครบ
3. **Booking Reminder** — flow Use case 3 ครบ (ใช้ได้กับ [ฟิตเนส/สตูดิโอโยคะ](/blog/ai-chatbot-ฟิตเนส-ยิม-สตูดิโอโยคะ-sme-2026) ที่ต้อง reminder คลาส 24/2/0.5 ชม. หรือ [คลินิก/สปา](/blog/ai-chatbot-คลินิก-สปา-2026) ที่ต้อง confirm appointment)

เปิด n8n ของคุณ → Import → JSON → ลากใส่ → ปรับ credential เสร็จ ใช้ได้

## สรุป

Google Sheet + n8n คือ stack เริ่มต้นที่ทำให้ SME ทำ automation ได้ฟรี (หรือเกือบฟรี) ภายใน 1 วัน · เพียงพอสำหรับ 70% ของโจทย์ที่ลูกค้าทักมาเรา

ถ้าโจทย์ของคุณยังเล็ก — ลอง DIY ก่อนได้ ([อ่าน 5 flow ที่ทำได้ใน 2 สัปดาห์](/blog/automation-ลดต้นทุน-sme))

ถ้าโจทย์เริ่มเกิน Sheet หรือต้อง integrate ลึก [ทักมาเล่าโจทย์](/#contact) ทีม KORP ประเมินว่าควรอยู่ stack ไหนคุ้มสุด ([เทียบ pricing รวมที่นี่](/blog/automation-ราคา-sme-เท่าไหร่))

— ทีม KORP AI
