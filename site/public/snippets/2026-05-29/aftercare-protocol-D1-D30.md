# Aesthetic clinic aftercare auto-message protocol (D+1, D+7, D+14, D+30)
*KORP AI — 2026-05-29 — MIT*

Aftercare LINE message schedule that all aesthetic-clinic chatbots should send.
Drops no-show on follow-up visits, catches early complications, and unlocks
upsell (touch-up / next session) without sales pressure.

## Schedule

| Stage | Send time (local) | Channel | Purpose | Asks for |
|-------|-------------------|---------|---------|----------|
| D+0   | 2h post-procedure | LINE push | Aftercare instructions reminder | optional pain scale 1-10 |
| D+1   | 10:00 next day    | LINE push | Check swelling + pain | photo (optional) + 3-option survey |
| D+7   | 10:00 day 7       | LINE push | Healing milestone + booking touch-up if applicable | photo + book D+14 visit |
| D+14  | 10:00 day 14      | LINE push | 2-week check + ROI ask | satisfaction 1-5 |
| D+30  | 10:00 day 30      | LINE push | 1-month assessment + invite to next cycle (for filler/botox refresh) | rebook? Y/N + reason |
| D+90  | 10:00 day 90      | LINE push | (botox only) refresh reminder | book? |
| D+180 | 10:00 day 180     | LINE push | (filler hyaluronic) refresh window starts | book? |

## Decision tree per stage

### D+1 swelling check
1. Bot: "วันนี้บวมระดับไหนคะ?" 3 buttons: น้อย/ปานกลาง/มาก
2. **น้อย** → "great! Keep iced 15 min × 4. ค่อยพบกัน D+7 นะคะ"
3. **ปานกลาง** → "นี่ปกติค่ะ แต่ขอ photo ส่งให้พยาบาลดูได้ไหมคะ?"
4. **มาก** → **trigger complication red-flag swarm** (do NOT respond — escalate MD 4 min)

### D+7 photo request
1. Bot: "ขอภาพ pre/post นิดนึงค่ะ — ภาพนี้จะเก็บเฉพาะใน medical record ตามที่คุณ consent ไว้"
2. If consent.scope == "marketing_allowed" AND face_blur_acknowledged → after upload, append: "ขอบคุณค่ะ ทีม marketing อาจขออนุญาตใช้ภาพ (ปกปิดใบหน้า) ในอนาคต — ปฏิเสธได้ทุกเมื่อ"
3. Photo → uploaded to S3 → encrypted → linked to photo_consent.id

### D+30 ROI ask
1. Bot: "ผลลัพธ์เป็นยังไงบ้างคะ? 1-5 ดาว"
2. ≤ 2 → escalate to MD for callback within 24h (do not LLM-respond)
3. = 3 → "ขอบคุณค่ะ ทีม QA จะติดต่อกลับเพื่อ feedback"
4. ≥ 4 → "ขอบคุณมากค่ะ ✨ ถ้าสะดวกขอ Google review เล็กน้อยได้ไหมคะ?" + Google review link

## Anti-spam rule

- Maximum 1 message per day. If patient replies, all subsequent scheduled
  messages pause for 48h (avoid feeling spammed).
- Patient can pause schedule with "หยุดข้อความเตือน" → resume only by request.

## Implementation note

Use a job table:

```sql
CREATE TABLE aftercare_job (
  id          BIGSERIAL PRIMARY KEY,
  patient_id  BIGINT NOT NULL,
  stage       TEXT NOT NULL,
  fire_at     TIMESTAMPTZ NOT NULL,
  fired_at    TIMESTAMPTZ,
  paused      BOOLEAN DEFAULT FALSE
);
```

Cron every 5 min: `SELECT * WHERE fire_at < now() AND fired_at IS NULL AND NOT paused`.
