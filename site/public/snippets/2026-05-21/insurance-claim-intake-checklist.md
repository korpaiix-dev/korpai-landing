# Insurance Claim Intake — Bot Checklist (Thailand 2026)

> Bot is the document collector and triage. Bot does NOT estimate payouts or promise coverage.
> All claims escalate to the licensed agent + claim staff at the underwriting company.

## Step 1 — Identify claim type

Bot asks user to select:
- รถยนต์ — ชน / โดนชน / สูญหาย / กระจกแตก
- สุขภาพ — IPD / OPD / อุบัติเหตุ
- ทรัพย์สิน — ไฟไหม้ / น้ำท่วม / โจรกรรม
- ชีวิต — สินไหมมรณกรรม / ทุพพลภาพ

## Step 2 — Required documents by type

### Motor — accident
- [ ] รูปที่เกิดเหตุ 4 มุม (ใกล้-ไกล + ทะเบียนคู่กรณี)
- [ ] บันทึกประจำวันตำรวจ (ถ้ามี)
- [ ] ใบขับขี่ตัวเอง (ทั้ง 2 ด้าน)
- [ ] ทะเบียนรถ
- [ ] กรมธรรม์ปัจจุบัน (เลข policy)
- [ ] เบอร์ติดต่อ + เวลาสะดวกให้สำรวจภัย

### Health — IPD
- [ ] ใบรับรองแพทย์ (medical certificate)
- [ ] ใบเสร็จ + ใบสรุปค่ารักษา (itemized)
- [ ] สำเนาประวัติการรักษา
- [ ] บัตร รพ. + บัตรประชาชน (สำเนา)
- [ ] กรมธรรม์ + ใบรับรองสิทธิ์ประกัน
- [ ] *PDPA explicit consent ก่อนถ่ายส่งเอกสารสุขภาพ*

### Property — fire
- [ ] รูปทรัพย์สินก่อน-หลัง (ถ้ามี)
- [ ] รายงานเพลิงไหม้ของสถานีดับเพลิง
- [ ] กรมธรรม์ปัจจุบัน
- [ ] บันทึกประจำวันตำรวจ
- [ ] รายการทรัพย์สิน + ใบเสร็จที่ยังเก็บได้

## Step 3 — Bot actions per file received

1. OCR (Google Vision / Tesseract Thai) → extract policy_no, date, amount
2. Validate file type/size (jpg/png/pdf, max 20MB each)
3. Encrypt + upload to S3 (server-side AES-256)
4. Generate audit row { user_id, file_hash, claim_no, timestamp }
5. Append to claim record in CRM
6. When all required docs present → notify agent + claim staff (Line + email)

## Step 4 — Bot MUST NOT

- Estimate payout amount ("จะได้ประมาณ X บาท") → forbidden
- Promise approval ("เคลมผ่านแน่นอน") → forbidden
- Suggest user delete/alter photos → forbidden, escalate immediately
- Give medical opinion → forbidden

## Step 5 — Time SLA bot communicates to user

- เอกสารครบ → ส่งบริษัทประกันภายใน 24 ชม. (ทำการ)
- บริษัทประกันแจ้งผลภายใน 7-15 วัน (motor) / 30 วัน (health/property/life)
- *ทุก SLA เป็นของบริษัทประกัน ไม่ใช่ของตัวแทน — bot ต้องระบุชัด*

---

KORP AI · 2026-05-21 · ใช้ในตัวแทนประกัน 64 คน รวมเคลม 412 case Q1/2026
