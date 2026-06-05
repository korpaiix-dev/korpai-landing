---
title: "n8n Self-Host บน VPS สำหรับ SME ไทย 2026: เลือก Spec, ต้นทุนจริงต่อเดือน, จุดคุ้มทุน vs Cloud และวิธี Backup"
description: "n8n self-host บน VPS ต้นทุนจริงเท่าไหร่ ใช้ spec ไหนพอ? เทียบราคา VPS ไทย vs Hetzner vs DigitalOcean, จุดคุ้มทุน vs n8n Cloud และ checklist backup กัน data หาย สำหรับ SME ไทย 2026"
pubDate: 2026-06-05
updatedDate: 2026-06-05
category: "Automation"
tags:
  - n8n
  - Self-host
  - VPS
  - Automation
  - SME ไทย
readingMinutes: 12
author: "ทีม KORP AI"
---

> **TL;DR:** สำหรับ SME ไทยส่วนใหญ่ n8n self-host รันได้สบายบน VPS **2 vCPU / 4 GB RAM / 40 GB SSD** ซึ่งราคา **~350–450 บาท/เดือน** (VPS ไทย) หรือ **~€8–9 (~330 บาท)** ถ้าใช้ Hetzner — และได้ execution **ไม่จำกัด** ต่างจาก n8n Cloud Starter ที่ ~900 บาท/เดือนแต่จำกัด 2,500 execution. **จุดคุ้มทุนจึงมาถึงแทบจะทันที** ถ้าคุณรัน workflow เกิน ~80 ครั้ง/วัน หรืออยากได้ไม่จำกัด — แลกกับการที่คุณต้องดูแล server เอง + **ตั้ง backup ให้ดี** (โดยเฉพาะ `N8N_ENCRYPTION_KEY`)

ปี 2026 SME ไทยที่ใช้ automation จริงจังเลือก [n8n](/blog/n8n-สำหรับ-sme-ไทย-คู่มือเริ่มต้น) เพราะ self-host แล้วรันได้ไม่จำกัดในราคาคงที่ แต่คำถามที่ตามมาเสมอคือ **"ต้องใช้ server สเปกเท่าไหร่? เดือนละกี่บาทจริง ๆ? แล้วคุ้มกว่า n8n Cloud ตรงไหน?"** บทความนี้ตอบครบด้วยตัวเลขจริงเดือนมิถุนายน 2026 พร้อม checklist backup ที่หลาย SME มองข้ามจนข้อมูลหายมาแล้ว

## n8n Self-Host ต้องใช้ Spec เท่าไหร่ — ตารางตามปริมาณงาน

หัวใจของการเลือก spec คือ: **n8n กิน RAM มากกว่า CPU** ทุก execution จะถือ payload ไว้ในหน่วยความจำ และ workflow เดียวที่รับ JSON ก้อนใหญ่กินได้ถึง 150–300 MB ดังนั้นเวลาวางแผน ให้โฟกัสที่ RAM ก่อน

| ปริมาณงาน (SME) | vCPU | RAM | SSD | Database | หมายเหตุ |
|---|---|---|---|---|---|
| ทดลอง / 1–2 workflow เบา | 1 | 2 GB | 20 GB | SQLite | ขั้นต่ำสุด — 1 GB **ไม่พอ** เจอ memory error แน่ |
| SME ใช้จริง (แนะนำ) | 2 | 4 GB | 40 GB | PostgreSQL | รัน n8n + PostgreSQL + reverse proxy ได้สบาย |
| หลาย workflow + RAG / AI | 4 | 8 GB | 60 GB | PostgreSQL | เริ่มมี workflow ที่ดึงข้อมูลก้อนใหญ่ |
| Volume สูง / หลาย client | 8+ | 16 GB+ | 100 GB+ | PostgreSQL + queue mode | แยก worker, ใช้ Redis queue |

**สรุปง่าย ๆ:** SME ไทยทั่วไป (ร้านค้า, คลินิก, เอเจนซี) เริ่มที่ **2 vCPU / 4 GB** พอ แล้วค่อยขยายเมื่อ RAM เริ่มเต็ม — ไม่ต้องจ่ายเกินตั้งแต่วันแรก

## ต้นทุน VPS จริงต่อเดือน 2026 — VPS ไทย vs Hetzner vs DigitalOcean/Vultr

ราคานี้อ้างอิงสเปกมาตรฐาน **2 vCPU / 4 GB RAM** (สเปกแนะนำสำหรับ SME) ข้อมูลเดือนมิถุนายน 2026:

| ผู้ให้บริการ | ที่ตั้ง server | ราคา/เดือน (โดยประมาณ) | จุดเด่น | ข้อควรระวัง |
|---|---|---|---|---|
| VPS ไทย (เช่น DriteStudio, Z.com, PTNK) | ไทย | **~350–450 บาท** | latency ต่ำในไทย, จ่ายเงินบาท, support ไทย, ดีต่อ PDPA | สเปก/IOPS ต่างกันมากแต่ละเจ้า ต้องเช็ค |
| Hetzner | เยอรมนี / ฟินแลนด์ | **~€8–9 (~330–360 บาท)** | ถูกสุดในกลุ่ม performance ดี | latency มาไทย ~150–250 ms (โอเคสำหรับงานหลังบ้าน ไม่เหมาะ chat realtime), ราคาปรับขึ้นเม.ย. 2026 |
| Hetzner (region สิงคโปร์) | สิงคโปร์ | ~€9+ | latency ดีกว่ายุโรปสำหรับไทย | ค่า bandwidth ส่วนเกินแพงกว่ายุโรปมาก (~€7.40/TB) |
| DigitalOcean | สิงคโปร์ ฯลฯ | **~$24 (~850 บาท)** | UI ดี, docs เยอะ, มี region สิงคโปร์ | แพงกว่า Hetzner ~2 เท่าที่สเปกเท่ากัน |
| Vultr | สิงคโปร์ / โตเกียว | **~$24 (~850 บาท)** | region เอเชียเยอะ, High Frequency เร็ว | ราคาใกล้ DigitalOcean |

**คำแนะนำสำหรับ SME ไทย:** ถ้า workflow ของคุณแตะข้อมูลลูกค้าคนไทย (ชื่อ, เบอร์, ที่อยู่) การวาง server ที่ **ไทยหรือสิงคโปร์** ช่วยทั้ง latency และความสบายใจเรื่อง [PDPA / data residency](/blog/pdpa-ai-chatbot-sme-ไทย-2026) ถ้าเป็นงานหลังบ้านล้วน ๆ ที่ไม่ต้องตอบเร็วระดับวินาที Hetzner ยุโรปคือตัวเลือกที่คุ้มเงินที่สุด

## Self-Host vs n8n Cloud — จุดคุ้มทุน (Break-even) คำนวณจริง

n8n Cloud คิดเงินตาม **execution** (1 execution = workflow รัน 1 รอบเต็ม ไม่ว่าจะมีกี่ step) ราคาเดือนมิถุนายน 2026:

| แพ็กเกจ n8n Cloud | ราคา/เดือน | Execution/เดือน | ต่อวันโดยเฉลี่ย |
|---|---|---|---|
| Starter | €24 (~900 บาท) | 2,500 | ~83 |
| Pro | €60 (~2,300 บาท) | 10,000 | ~333 |
| Business | €800 (~30,000 บาท) | 40,000 | ~1,333 |

(หมายเหตุ: เมษายน 2026 n8n ยกเลิกลิมิตจำนวน active workflow ทุกแพ็กเกจแล้ว เหลือคิดที่ execution อย่างเดียว)

ทีนี้เทียบกับ self-host VPS ไทย ~400 บาท/เดือนที่รัน **ไม่จำกัด execution**:

### 3 กรณีตามปริมาณงาน

1. **ถ้าคุณรัน < 2,500 execution/เดือน (< 83/วัน):** ทั้งสองทางใกล้กัน — VPS ไทย (~400) ถูกกว่า Cloud Starter (~900) แต่ Cloud ไม่ต้องดูแล server เลย ถ้าเวลาคุณมีค่ามากและไม่อยากแตะ Linux → **Cloud Starter คุ้มกว่าในแง่เวลา**
2. **ถ้าคุณรัน 2,500–10,000 execution/เดือน:** Cloud บังคับให้ขึ้น Pro (~2,300 บาท) ทันที ในขณะที่ self-host ยังคงที่ ~400 บาท → **self-host เริ่มคุ้มชัดเจน**
3. **ถ้าคุณรัน > 10,000 execution/เดือน:** ส่วนต่างยิ่งถ่างออก self-host ยังเท่าเดิม (อาจอัป RAM เป็น 8 GB ~600–900 บาท) ส่วน Cloud พุ่งเข้าใกล้ Business → **self-host คุ้มแบบไม่ต้องคิด**

**บรรทัดสรุป:** "ต้นทุน" จริงของ self-host ไม่ใช่แค่ค่า VPS แต่รวม **เวลาดูแล ~1–2 ชม./เดือน + ความเสี่ยงถ้าไม่ backup** ถ้าตีค่าเวลาตรงนี้ไหว self-host ชนะเรื่องเงินเกือบทุกกรณีที่มี volume จริง อยากเห็นการเทียบเครื่องมือแบบเต็ม ดู [n8n vs Make vs Zapier](/blog/n8n-vs-make-vs-zapier-sme-ไทย-2026) และภาพรวม [ราคา automation สำหรับ SME](/blog/automation-ราคา-sme-เท่าไหร่)

## ทำไม RAM คือคอขวด ไม่ใช่ CPU (และวิธีจัดการ)

n8n ไม่ใช่งานที่ใช้ CPU หนัก แต่ละ execution จะถือข้อมูลทั้งก้อนไว้ใน memory ระหว่างทำงาน ปัญหาที่ SME เจอบ่อยคือ workflow ดึง JSON/ไฟล์ก้อนใหญ่หลายรอบพร้อมกันแล้ว RAM เต็มจน process ถูก kill วิธีรับมือ:

- ตั้ง `EXECUTIONS_DATA_PRUNE=true` และ `EXECUTIONS_DATA_MAX_AGE` (เช่น 168 ชม. = 7 วัน) เพื่อไม่ให้ execution log บวมกินดิสก์/แรม
- ใช้ **PostgreSQL** แทน SQLite ตั้งแต่ production แรก — SQLite ล็อกไฟล์เดียวและพังง่ายเมื่อมี execution พร้อมกันเยอะ
- ถ้า workflow ประมวลผล array ใหญ่ ให้ใช้ node **Split in Batches** แบ่งทีละก้อน แทนที่จะโหลดทั้งหมดเข้า memory
- เมื่อ volume สูงจริง เปิด **queue mode** (n8n main + worker แยก + Redis) เพื่อกระจายโหลด

## Checklist ติดตั้ง + ความปลอดภัย (ทำตามลำดับ)

ก่อนเปิด n8n ออกอินเทอร์เน็ต ทำให้ครบ 9 ข้อนี้:

1. **Reverse proxy + HTTPS** — ตั้ง Caddy หรือ Nginx ออกใบ SSL อัตโนมัติ (อย่ารัน n8n เปลือย ๆ บนพอร์ต 5678)
2. **เปิด owner account / basic auth** — ห้ามปล่อย instance ให้ใครเข้าก็ตั้ง workflow ได้
3. **Firewall (ufw)** — เปิดเฉพาะ 80, 443, 22 ปิดที่เหลือทั้งหมด
4. **SSH key-only + เปลี่ยนพอร์ต** — ปิด password login กัน brute-force
5. **ตั้ง `N8N_ENCRYPTION_KEY` เอง** (อย่าให้ n8n สุ่มให้) — และ **เก็บสำรองคีย์นี้ไว้นอกเครื่องทันที** (ดูเหตุผลในหัวข้อ backup)
6. **ใช้ PostgreSQL** ตั้งค่า `DB_TYPE=postgresdb` ตั้งแต่แรก
7. **ตั้ง `WEBHOOK_URL`** ให้ตรงกับโดเมนจริง ไม่งั้น webhook จาก Line/Facebook จะ callback ไม่ถูก
8. **อัปเดต n8n สม่ำเสมอ** — `docker compose pull && up -d` ทุก 2–4 สัปดาห์ ปิดช่องโหว่
9. **เปิด `EXECUTIONS_DATA_PRUNE`** กันดิสก์เต็มจาก log เก่า

## Backup ไม่ให้ข้อมูลหาย — กลยุทธ์ 3-2-1

เคสที่เจอบ่อยสุดคือ VPS ถูกรีเซ็ต/ลบ แล้วไม่มี backup — workflow หลายสิบอันหายเกลี้ยง

### 4 อย่างที่ต้องสำรอง (ห้ามขาด)

สิ่งที่ **ต้อง** สำรองมี 4 อย่าง:

- **PostgreSQL dump** (workflows + credentials ที่เข้ารหัส + execution history)
- โฟลเดอร์ `.n8n` (ถ้ายังใช้ SQLite จะอยู่ตรงนี้)
- **`N8N_ENCRYPTION_KEY`** ⚠️ สำคัญสุด — ถ้าหายคีย์นี้ **credentials ทุกอันที่เข้ารหัสไว้จะถอดไม่ได้** ต้องตั้ง connection (Line, Google, Facebook ฯลฯ) ใหม่ทั้งหมด
- `docker-compose.yml` + ไฟล์ `.env`

### กฎ 3-2-1 และการทดสอบ restore

ยึดกฎ **3-2-1**: เก็บ 3 สำเนา, 2 ที่ต่างชนิดกัน, 1 ชุด offsite (เช่น object storage / Google Drive คนละที่กับ VPS) ตั้ง cron ทำ `pg_dump` ทุกคืนแล้ว push ขึ้น offsite อัตโนมัติ — เราเตรียม [โค้ดสคริปต์ backup อัตโนมัติ](https://korpai.co/snippets/2026-06-05/) ไว้ให้ก๊อปไปใช้ได้เลย และ **อย่าลืมทดสอบ restore จริง** อย่างน้อยเดือนละครั้ง — backup ที่กู้ไม่ได้ = ไม่มี backup

ถ้าอยากต่อ n8n เข้ากับ Google Sheet / ระบบจริงต่อ อ่าน [คู่มือ Google Sheet automation ด้วย n8n](/blog/google-sheet-automation-sme-n8n) เพิ่มได้

## คำถามที่ SME ถามบ่อย (FAQ)

**Q: n8n self-host ฟรีจริงไหม?**
ตัว software ฟรี (Community Edition ใช้ภายใต้ Sustainable Use License — ใช้ในธุรกิจตัวเองได้) แต่มีค่า VPS ~350–450 บาท/เดือน + เวลาดูแลของคุณเอง ไม่ใช่ "ฟรี 100%" แต่ถูกกว่า Cloud มากเมื่อมี volume

**Q: ควรใช้ SQLite หรือ PostgreSQL?**
Production ใช้ **PostgreSQL** เสมอ SQLite เหมาะแค่ลองเล่น เพราะล็อกไฟล์เดียวและเสี่ยงพังเมื่อมี execution พร้อมกันหลายตัว

**Q: ถ้ามีแค่ 2–3 workflow ต้อง self-host ไหม?**
ไม่จำเป็น ถ้าใช้ < 2,500 execution/เดือนและไม่อยากแตะ server → n8n Cloud Starter คุ้มกว่าในแง่เวลา เริ่ม self-host เมื่อ volume โต หรืออยากคุมข้อมูลเอง

**Q: ลืม backup `N8N_ENCRYPTION_KEY` จะเป็นอะไร?**
credentials ทั้งหมดที่เข้ารหัสด้วยคีย์เก่าจะถอดไม่ได้ ต้องลบแล้วตั้ง connection ใหม่ทุกอัน ดังนั้นสำรองคีย์นี้แยกไว้ที่ปลอดภัยตั้งแต่วันแรก

**Q: ตั้ง server ไทย/สิงคโปร์ vs ยุโรป ต่างกันยังไง?**
ไทย/สิงคโปร์ = latency ต่ำกว่า + สบายใจเรื่อง PDPA เมื่อมีข้อมูลคนไทย; ยุโรป (Hetzner) = ถูกกว่าแต่ latency ~150–250 ms เหมาะงานหลังบ้านที่ไม่ต้องตอบทันที

**Q: queue mode คืออะไร ต้องใช้ไหม?**
เป็นโหมดแยก worker หลายตัว + Redis สำหรับ volume สูง SME ทั่วไปยังไม่ต้องใช้ เปิดเมื่อ execution หนาแน่นจน instance เดียวรับไม่ไหว

## บทสรุป — เริ่มยังไงดี?

สำหรับ SME ไทยส่วนใหญ่: เริ่มที่ **VPS 2 vCPU / 4 GB (~400 บาท/เดือน)** + PostgreSQL + reverse proxy HTTPS + ตั้ง backup cron ตั้งแต่วันแรก เท่านี้ก็ได้ automation ไม่จำกัดในราคาคงที่ที่คุ้มกว่า n8n Cloud เมื่อมี volume จริง — โดยมี "ต้นทุนซ่อน" คือเวลาดูแล ~1–2 ชม./เดือนและวินัยเรื่อง backup

ถ้าไม่อยากดูแล server เอง KORP AI รับ **ติดตั้ง + ดูแล n8n self-host บน VPS ของลูกค้าเอง** พร้อม backup อัตโนมัติ, monitoring และ training ให้ทีมใช้ต่อได้ — [คุยโจทย์กับเราที่หน้า demo](https://korpai.co/demo) หรือทักผ่าน Line / Facebook ของ KORP AI ได้เลย

---

*เขียนโดยทีม KORP AI — AI Agency ไทยที่ออกแบบ สร้าง และดูแลระบบ AI Chatbot, Automation และ Dashboard ให้ SME ไทยใช้งานต่อเองได้จริง*
