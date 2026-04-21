# Facebook / Line domain migration → korpai.co

> แผนย้าย presence บนโซเชียล (Facebook Business, Line OA) ให้ผูกกับ domain หลัก `korpai.co`
> **Owner:** บอสไผ่ · **Status:** Planning · **Blocker:** ต้องทำใน Meta Business Suite + Line OA console (บอสเป็นคนทำ Claude ช่วย verify)

---

## 0. ทำไมต้องย้าย

- เว็บ KORP AI ย้ายจาก subdomain เก่า (เช่น `korp-ai.xxx`) → `korpai.co` เป็น main domain
- Facebook Page + Line OA ยัง link กลับไปหา subdomain เก่า → เสียทั้ง brand + lead routing + tracking
- ต้องให้ทุกลูกค้าที่คลิกจาก FB / IG / Messenger / Line → landing บน `https://korpai.co`

**ผลกระทบถ้าไม่ทำ:**
1. FB auto-scrape OG ของ URL เก่า → preview broken
2. Line OA webhook ส่ง message ไปที่ backend เก่า (ปิดไปแล้ว) → ลีดหาย
3. Pixel / Conversions API tracking จับไม่ติด
4. SEO authority รั่วจาก signal fragmentation

---

## 1. Pre-flight checklist (ต้อง ✅ ก่อนเริ่ม)

- [ ] `https://korpai.co` deploy เสร็จ + SSL green + OG image render ถูก (ใช้ https://developers.facebook.com/tools/debug/ ตรวจ)
- [ ] `https://korpai.co/robots.txt` + `/sitemap.xml` + `/llms.txt` serve 200
- [ ] DNS record ถูก: `korpai.co` + `www.korpai.co` ชี้ไป VPS 139.59.123.146
- [ ] Facebook Business Manager บอสมี access level "Admin"
- [ ] Line Developers console บอสมี access เป็น "Admin" ของ OA
- [ ] Backup ของ config เก่า (screenshot Business Manager + Line OA settings เก็บไว้ ก่อนเปลี่ยน)

---

## 2. Facebook Business Manager migration

### 2.1 Domain verification

1. เข้า Business Manager → **Brand Safety** → **Domains**
2. เพิ่ม domain `korpai.co`
3. เลือก verify แบบ **Meta-tag** (ง่ายสุดสำหรับ static site)
4. Meta จะให้ `<meta name="facebook-domain-verification" content="xxxxxxxxxxxx" />`
5. ส่งค่าที่ได้ให้ Claude → Claude จะใส่ใน `site/src/layouts/Layout.astro` ใน `<head>`
6. Deploy + Verify บน FB → สถานะต้องเป็น "Verified"
7. ลบ domain เก่าออก (ถ้ามี) ทิ้งแต่ `korpai.co` เท่านั้น

### 2.2 Facebook Page settings

1. เข้า Facebook Page → **Settings** → **About**
2. Website field — เปลี่ยนเป็น `https://korpai.co`
3. Category/Tagline — อัปเดตให้ตรงกับหน้า About (`AI Agency · Thai SME`)
4. Click **Update** → FB จะ re-scrape OG ทันที

### 2.3 Messenger "Get started" button / CTA

1. Page → **Manage** → **Call-to-action buttons**
2. Primary CTA: `Send Message` หรือ `Contact us`
3. Secondary link (ถ้ามี): ใส่ `https://korpai.co/#contact`
4. Test จากบัญชีอื่น → คลิกแล้วต้องไปถึงหน้า contact section โดยตรง

### 2.4 Pixel / Conversions API (CAPI)

1. Business Manager → **Events Manager** → **Pixels**
2. ถ้ามี pixel เก่าอยู่บน domain เก่า → **ไม่ต้อง** สร้างใหม่ แค่เพิ่ม `korpai.co` เข้า **Allowed domains**
3. Claude จะใส่ pixel JS snippet ใน `Layout.astro` — ต้องรอ ID จากบอส (ยังไม่ใส่ไปก่อน เพื่อไม่ให้ track ที่ dev env)
4. Events ที่ควร track อย่างน้อย: `PageView` (auto), `Lead` (submit contact form), `Contact` (click Line/FB chip), `ViewContent` (blog/services/portfolio detail view)
5. CAPI optional — ถ้าไม่เปิด web pixel พอ

### 2.5 Lead Ads integration (ถ้าใช้)

1. ถ้ามี Lead Ads form เชื่อม webhook เดิม → อัปเดต webhook URL ไป `https://korpai.co/api/fb-lead` (ยังไม่สร้าง, phase ต่อไป)
2. ระยะกลางแนะนำใช้ **Zapier** หรือ **Make** webhook → Line notify → gDoc ก่อน จนกว่า backend CRM เสร็จ

---

## 3. Line Official Account migration

### 3.1 Verify domain

Line OA ไม่ต้อง verify domain แบบ FB — แต่ต้อง whitelist URL ใน LIFF / rich menu ถ้ามี

### 3.2 Rich menu / link in bio

1. **Line OA Manager** → **Home** → **Rich Menu**
2. ปุ่ม/รูปที่ link ไปเว็บ — เปลี่ยน URL เป็น `https://korpai.co/<section>`
3. Suggestions:
   - ปุ่ม "บริการ" → `https://korpai.co/#services`
   - ปุ่ม "ผลงาน" → `https://korpai.co/#portfolio`
   - ปุ่ม "ราคา" → `https://korpai.co/#pricing`
   - ปุ่ม "บล็อก" → `https://korpai.co/blog/`
4. Save → Publish

### 3.3 Webhook URL (ถ้าเปิด bot features)

1. **Line Developers Console** → Messaging API → **Messaging API Settings**
2. Webhook URL — ยังไม่ต้องเปลี่ยน ถ้า backend ไม่ได้ย้าย (phase ต่อไปจะใส่ `https://korpai.co/api/line-webhook`)
3. ถ้าปิด bot เลย ให้ toggle **Use webhook** = OFF ก็พอ จนกว่าพร้อม

### 3.4 Line Login (ถ้าใช้)

1. **Line Developers** → Channel → Line Login tab
2. Callback URL — เพิ่ม `https://korpai.co/auth/line/callback` (จอง slot ไว้ก่อน)
3. Linked OAs — ผูกกับ OA `@korpai` ปัจจุบัน

### 3.5 Greeting message

1. Line OA Manager → **Home** → **Greeting message**
2. ข้อความเริ่มต้นต้องมี link `https://korpai.co` — ไม่ใช่ subdomain เก่า
3. Suggested text: `สวัสดีค่ะ/ครับ ขอบคุณที่ทักมาหา KORP AI · ดูบริการ + ตัวอย่างได้ที่ https://korpai.co · ทีมจะตอบภายใน 24 ชม.`

---

## 4. Verify + Smoke test

### 4.1 FB side

```
1. https://developers.facebook.com/tools/debug/
   → ใส่ https://korpai.co → Fetch new scrape → ดู OG image + title + description
2. https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Fkorpai.co
   → preview card ต้องแสดงรูป og-default.png + title + description ถูก
3. Message หน้า FB Page จากมือถืออีกเครื่อง → ต้องได้ greeting + link ใหม่
```

### 4.2 Line side

```
1. แสกน QR ของ OA จากมือถืออีกเครื่อง → เพิ่มเพื่อน → ต้องได้ greeting ใหม่
2. กด rich menu ทุกปุ่ม → ต้องเข้า korpai.co section ถูก
3. ส่งข้อความ "สวัสดี" → ดูว่าบอทตอบ/admin notify ถูก channel
```

### 4.3 Tracking (หลังใส่ pixel)

```
1. ติดตั้ง **Meta Pixel Helper** Chrome extension
2. เข้า https://korpai.co → ต้องเห็น PageView fired
3. คลิก Line/FB chip → ต้องเห็น Contact event fired
4. Events Manager → Overview → ดู events จริงภายใน 30 นาที
```

---

## 5. Rollback plan

ถ้าหลัง migration พบปัญหา (ลีดหาย, preview พัง, tracking หลุด):

| Symptom | Rollback step |
|---|---|
| OG preview FB แตก | กลับไปตั้ง website field ใน FB Page เป็น URL เก่า 1 วัน รอ cache expire แล้วค่อยลอง verify ใหม่ |
| Line webhook ตอบไม่ทัน | toggle **Use webhook** = OFF ให้ Line ตอบ greeting message อย่างเดียว จนกว่า backend ใหม่พร้อม |
| Pixel ไม่ fire | ถอด pixel snippet ออกจาก Layout.astro → redeploy → ลองเฉพาะ view แทน 1-2 วันแล้วค่อย re-add |

---

## 6. Timeline (ประมาณ 1-2 ชั่วโมง + waiting time)

| Step | Owner | Duration |
|---|---|---|
| Pre-flight + backup screenshot | บอส | 15 min |
| FB domain verify (meta tag round-trip) | บอส + Claude | 30 min (รอ deploy 1 รอบ) |
| FB Page settings + CTA | บอส | 10 min |
| Line rich menu + greeting | บอส | 20 min |
| Pixel install (ถ้าพร้อม) | Claude (ใส่ ID ให้) | 15 min |
| Smoke test all channels | บอส + Claude | 20 min |

---

## 7. Post-migration monitor (7 วันแรก)

- [ ] Check FB Business Manager → Events Manager daily — pixel ต้อง fire สม่ำเสมอ
- [ ] Line OA manager → Insights → ดู "Friend add" trend ว่าไม่ drop เกิน 20% WoW
- [ ] Google Search Console → monitor `korpai.co` coverage (crawl errors, index coverage)
- [ ] ถ้า traffic จาก `fb.com` referer drop เกิน 30% → ตรวจ FB Page + preview อีกครั้ง

---

## 8. Action items — บอสต้องทำเอง (Claude ทำแทนไม่ได้)

1. **FB Business Manager admin access** — Claude ไม่มี login
2. **Line OA console admin access** — Claude ไม่มี login
3. **ส่งค่า FB meta-tag verification** ให้ Claude ใส่ใน Layout.astro
4. **ส่ง Pixel ID (ถ้ามี)** ให้ Claude hook เข้า Layout.astro
5. **Confirm ว่าต้องการเปิด CAPI หรือไม่** (ต้องใช้ token จาก FB)
6. **Rich menu art file (.png)** ถ้าจะเปลี่ยน — ส่งให้ Claude ช่วย optimize ขนาด

> Claude จะเตรียม: meta-tag hook, pixel snippet template, rich menu URL list, OG image preview
> ไว้ให้บอสเอาไปใส่ตอนกดปุ่มจริงใน console

---

## 9. References

- FB Domain verify: https://developers.facebook.com/docs/sharing/domain-verification
- FB sharing debugger: https://developers.facebook.com/tools/debug/
- Line rich menu docs: https://developers.line.biz/en/docs/messaging-api/using-rich-menus/
- Meta Pixel install: https://developers.facebook.com/docs/meta-pixel/get-started
