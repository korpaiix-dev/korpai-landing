---
title: "n8n สำหรับ SME ไทย 2026: คู่มือเริ่มต้น automate ธุรกิจฟรี (ไม่ต้องเขียนโค้ด)"
description: "n8n คือ automation tool ฟรี open-source ที่ SME ไทยใช้แทน Zapier ได้คุ้มกว่า 10 เท่า — คู่มือนี้สอนติดตั้ง, เชื่อม Line/Facebook/Google Sheet, 8 workflow ที่ทำได้เลยในวันแรก"
pubDate: 2026-05-01
updatedDate: 2026-05-09
category: "Automation"
tags:
  - n8n
  - Automation
  - SME ไทย
  - No-code
  - Workflow
readingMinutes: 11
---

> **TL;DR:** n8n เป็น **automation tool ฟรี open-source** ที่ทำงานเหมือน Zapier/Make แต่ **ไม่จำกัด workflow + ราคาถูกกว่า 10-20 เท่า** เหมาะกับ SME ไทยที่อยาก automate งานซ้ำๆ โดยไม่ผูกกับ vendor — บทความนี้สอนตั้งแต่ติดตั้ง 5 นาที จนถึง 8 workflow ที่ทำเงินจริง

ปี 2026 SME ไทยที่จริงจังกับ automation **ย้ายจาก Zapier มา n8n** เกือบหมด — เพราะ Zapier ราคาเริ่ม 19.99 USD (~700 บาท)/เดือน และจำกัดจำนวน task ในขณะที่ n8n self-host บน VPS เดือนละ 200 บาทก็รันได้ไม่จำกัด

แต่หลาย SME ลังเล เพราะ "n8n ต้องเซ็ตอัพเอง ดูยาก" — บทความนี้แก้ไขข้อนี้ให้

## n8n คืออะไร — เปรียบเทียบกับ Zapier และ Make

| | n8n | Zapier | Make (Integromat) |
|---|---|---|---|
| ราคาเริ่มต้น | ฟรี (self-host) หรือ $20/mo cloud | $19.99/mo (100 tasks) | $9/mo (1,000 ops) |
| Task limit | ไม่จำกัด (self-host) | จำกัดตามแพ็กเกจ | จำกัดตามแพ็กเกจ |
| Open-source | ใช่ | ไม่ | ไม่ |
| App integration | 400+ | 6,000+ | 1,500+ |
| Code custom | JavaScript / Python ใน node | จำกัด | จำกัด |
| Self-host บน VPS เราเอง | ใช่ | ไม่ | ไม่ |
| ภาษาไทย | UI อังกฤษ + community ไทยมี | UI อังกฤษ | UI อังกฤษ |
| Learning curve | กลาง-สูง | ง่าย | กลาง |

**สรุป:** ถ้าต้องการ workflow มากกว่า 100 ครั้ง/เดือน + อยากประหยัด → n8n. ถ้าใช้แค่ 1-2 workflow เบสิคและไม่อยากดูแล server → Zapier

## เริ่มใช้ n8n ใน 5 นาที (cloud) หรือ 30 นาที (self-host)

### Option A: n8n Cloud (ง่ายสุด, เริ่มได้ทันที)

1. ไป https://n8n.io/cloud
2. Sign up ด้วย Google account (ฟรี 14 วันแรก)
3. เลือก plan: **Starter** $20/mo (5,000 executions, 5 active workflows)
4. UI จะเปิดขึ้น → เริ่มสร้าง workflow แรกได้

### Option B: Self-host บน VPS (ประหยัดสุด — ระยะยาว)

ต้องการ: VPS Ubuntu 22.04 (DigitalOcean / Vultr / AWS Lightsail) เริ่มต้น $6/mo

```bash
# ติดตั้งผ่าน Docker (วิธีที่แนะนำ)
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  docker.n8n.io/n8nio/n8n
```

หรือใช้ docker-compose สำหรับ production setup (database persistent + reverse proxy + SSL)

ใช้ Caddy หรือ nginx เป็น reverse proxy + Let's Encrypt SSL → เปิด n8n.yourcompany.com ใช้งานได้

> เรามี [Service: Workflow Automation](/services/automation) ที่ deploy n8n บน VPS ลูกค้าให้พร้อมใช้ + training ใน 1 สัปดาห์

## 8 workflow ที่ SME ไทยทำได้เลยในวันแรก

### 1. Facebook Lead Ads → Google Sheet → Line OA แจ้งทีม

**ปัญหาที่แก้:** ลีดจาก Facebook Ads ตกหายเพราะไม่มีคนเช็ค

**Workflow:**
- Trigger: Facebook Lead Ads new lead
- Action 1: Append row ใน Google Sheet (ทำ database ลีดอัตโนมัติ)
- Action 2: Send Line OA message ไปที่กลุ่มทีมขาย: "ลีดใหม่: ชื่อ X, เบอร์ Y"
- เวลาเซ็ต: 15 นาที

### 2. Order จาก Shopee/Lazada → Line OA แจ้ง warehouse

**ปัญหาที่แก้:** order ค้าง ไม่ pack เพราะไม่รู้ว่ามี order ใหม่

**Workflow:**
- Trigger: Webhook จาก Shopee Open API (หรือ poll ทุก 5 นาที)
- Action: Send Line message: "Order #12345, สินค้า: เสื้อ size M × 2, ที่อยู่: ..."
- เวลาเซ็ต: 30 นาที

### 3. ใบเสนอราคาอัตโนมัติจาก Google Form

**ปัญหาที่แก้:** ลูกค้ากรอก form แล้วต้องรอแอดมินเขียน quote 1-2 ชม.

**Workflow:**
- Trigger: Google Form submission
- Action 1: Pull ข้อมูล + คำนวณราคาตาม template
- Action 2: Generate PDF ผ่าน node "HTML to PDF" หรือเรียก API DocRaptor
- Action 3: Email PDF กลับไปลูกค้าทันที + CC ทีมขาย
- เวลาเซ็ต: 2-3 ชม. (แต่ใช้ทุกวัน คุ้ม)

> อ่านต่อ: [Google Sheet + n8n สำหรับ SME ไทย — automation ใน 1 วัน](/blog/google-sheet-automation-sme-n8n)

### 4. Reminder การจอง 1 วันก่อน

**ปัญหาที่แก้:** no-show เพราะลูกค้าลืม

**Workflow:**
- Trigger: Cron daily 9:00
- Action 1: Query database (Google Sheet/Airtable/Postgres) — หาคนที่จองพรุ่งนี้
- Action 2: Loop → ส่ง Line OA reminder คนละข้อความ
- เวลาเซ็ต: 1 ชม.
- ผล: no-show ลด 30-50%

### 5. Daily sales report ส่ง Line OA ตอนปิดร้าน

**ปัญหาที่แก้:** เจ้าของไม่รู้ยอดวันนี้จนกว่าจะถามแอดมิน

**Workflow:**
- Trigger: Cron daily 22:00
- Action 1: Query Shopify/Loyverse/POS API — สรุปยอดวันนี้
- Action 2: Format เป็นข้อความสวยๆ → ส่ง Line OA เจ้าของ
- เวลาเซ็ต: 30 นาที

### 6. Customer feedback form → Notion + Slack alert ถ้า rating ต่ำ

**ปัญหาที่แก้:** เจอ feedback ลูกค้าไม่พอใจ ต้องรอแอดมินบอก

**Workflow:**
- Trigger: Typeform/Google Form submission
- Action 1: Append ใน Notion table
- Action 2: IF rating < 3 → Slack alert ทีม customer success
- เวลาเซ็ต: 20 นาที

### 7. RSS feed → AI summarize → ส่งทีม

**ปัญหาที่แก้:** ทีมไม่ได้ตามข่าวอุตสาหกรรม

**Workflow:**
- Trigger: Cron daily 8:00
- Action 1: Read RSS feeds (5-10 sources)
- Action 2: Call OpenAI/Claude API → ขอ summary 3 bullet
- Action 3: Send Line OA + email
- เวลาเซ็ต: 1 ชม.

### 8. AI Chatbot Line OA + RAG จาก Google Drive

**ปัญหาที่แก้:** อยากให้ AI ตอบลูกค้าจากเอกสารธุรกิจเรา

**Workflow:**
- Trigger: Line OA webhook (ลูกค้าส่งข้อความ)
- Action 1: Vector search ใน Pinecone/pgvector หา context ที่เกี่ยวข้อง
- Action 2: Call Claude API พร้อม context
- Action 3: Reply กลับ Line OA
- เวลาเซ็ต: 1 วัน (advanced)

> นี่คือ workflow ที่ KORP AI ทำให้ลูกค้า — ถ้าซับซ้อนเกินไปทำเอง [ทักมาคุย](/services/ai-chatbot)

## คำถามที่ SME ถามบ่อย

**Q: n8n ปลอดภัยไหม? เก็บข้อมูลลูกค้าได้ไหม?**
A: ปลอดภัย ถ้า self-host บน VPS เรา = data ไม่ออกจาก server เรา (ตรงข้ามกับ Zapier/Make ที่ data วิ่งผ่าน server เขา) เหมาะกับ PDPA compliance

**Q: workflow บน n8n cloud หรือ self-host ดีกว่า?**
A: cloud = ตั้งง่าย เริ่มเร็ว แต่ราคา $20-50/mo ตามใช้. self-host = ตั้งยากครั้งแรก แต่ระยะยาวประหยัด + data privacy ดีกว่า

**Q: Zapier มี integration เยอะกว่า ใช่ไหม?**
A: ใช่ Zapier มี 6,000+ vs n8n 400+ แต่ 90% ของ workflow ที่ SME ไทยใช้ — Line / FB / Google / Shopee / Lazada / Notion / Slack / Stripe — n8n มีหมด

**Q: ถ้า n8n บน VPS ล่ม เกิดอะไรขึ้น?**
A: workflow หยุดทำงานทันที. แก้ด้วย: monitoring + auto-restart (systemd) + database backup ประจำ. KORP AI deploy พร้อมพวกนี้ครบ

**Q: เปลี่ยนจาก Zapier มา n8n ต้อง migrate ยังไง?**
A: ต้องสร้าง workflow ใหม่ใน n8n (ไม่มี import direct จาก Zapier) ใช้เวลาประมาณ 30 นาที-1 ชม. ต่อ workflow

## บทสรุป — เริ่มยังไง?

1. **ถ้าจะทำเอง** → สมัคร n8n cloud ($20/mo) ลองทำ workflow แรก (Lead Ads → Sheet → Line) ใน 1 ชม.
2. **ถ้าอยากประหยัดระยะยาว** → ติดตั้ง self-host บน VPS DigitalOcean $6/mo
3. **ถ้าอยากระบบจริงจัง พร้อมใช้** → ทักมา [KORP AI](/services/automation) — เรา deploy + ตั้ง 5-10 workflow แรก + training ทีมใน 2 สัปดาห์

เปิด demo workflow สดได้ที่ [korpai.co/demo/business](https://korpai.co/demo/business) — ดูตัวอย่าง quote generator + KPI dashboard ที่ทำด้วย n8n

---

**บทความที่เกี่ยวข้อง:**
- [n8n vs Make vs Zapier — SME ไทยควรเลือกตัวไหน 2026](/blog/n8n-vs-make-vs-zapier-sme-ไทย-2026)
- [Google Sheet + n8n — automation ใน 1 วัน](/blog/google-sheet-automation-sme-n8n)
- [Automation ราคาเท่าไหร่ SME 2026](/blog/automation-ราคา-sme-เท่าไหร่)
- [Automation ลดต้นทุน SME — 5 flow ใน 2 สัปดาห์](/blog/automation-ลดต้นทุน-sme)
- [AI Chatbot ราคาเท่าไหร่ — คู่มือคำนวณงบ SME](/blog/ai-chatbot-ราคา-2026-คู่มือ)
