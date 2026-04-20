# KORP AI Landing Page — PROGRESS.md

> **วัตถุประสงค์ไฟล์นี้:** บันทึกสถานะงานล่าสุดเพื่อให้ session ถัดไปเข้าใจบริบททันที ไม่ทำงานซ้ำซ้อน
> **อัปเดตทุกครั้ง:** ก่อนเริ่มงาน (กำลังจะทำอะไร) และหลังจบงาน (ทำอะไรไปแล้ว / ยังเหลืออะไร)
> **Owner:** บอสไผ่ (korpaiix@gmail.com)
> **Repo:** https://github.com/korpaiix-dev/korpai-landing
> **Local path (VPS):** /root/korpai-landing
> **Prod domain:** https://korpai.co (serve from /var/www/korpai/ via nginx)

---

## 📌 CURRENT STATE (2026-04-20)

**Phase:** Day 0 — Setup & scaffolding
**Status:** 🟡 งานเริ่มต้น — repo สร้างแล้ว, ยังไม่มี Astro scaffold, landing page ยังเป็น placeholder
**Next action:** Day 1 — ติดตั้ง Astro + สร้าง Hero/Services/Process/Contact

---

## ✅ DONE

### Session 2026-04-19 (previous)
- [x] Audit VPS 139.59.123.146 — พบ 26+ containers (client projects ถูกกฎหมาย)
- [x] ลบไฟล์เก่า KORP AI v1:
  - `korpai.backup.20260416-065640.tgz`
  - Containers: `korpaiix-office`, `korpaiix-middleware`
  - Images: `korpaiix-fb-manager`, `korpaiix-fb-manager-tg-bot`
  - Folders: phase1-deploy, aidesigner-run/test, fb-share-tool, stitch-test
  - Files: engine_v1_backup.py, engine_v3.py, dispatch-articles.sh, expand_articles.py, patch_*.py
- [x] Disk ว่างขึ้นจาก 77% → 58% (33G ว่าง)
- [x] ยืนยัน webhook backend (port 8001) + dashboard (port 3000) = DEAD
- [x] แทนที่ landing เดิมที่ /var/www/korpai/ ด้วย placeholder "Coming Soon"
- [x] ยืนยัน design brief กับบอส:
  - Theme: ขาว + ฟ้าอ่อน + เขียวอ่อน (สบายตา, ติดต่อง่าย)
  - Chat widget: AI Sales Agent จริง → ส่งต่อ Line/FB (ไม่จบงานหน้าเว็บ)
  - Sections: ครบชุด (Hero + Services + Process + Contact + Portfolio + Pricing + FAQ + Blog + About + SEO articles + Chatbot mock + Web AI agentic style)
  - Timeline: 3-5 วัน
  - Portfolio: โชว์ได้แต่ห้ามเปิดชื่อธุรกิจจริง, ใส่ธุรกิจที่เรา "โม้" ขึ้นมาได้ (แต่ไม่น่าเกลียด)
  - Pricing: "ปรึกษาฟรี" อย่างเดียว (ราคาคุยกันเอง)

### Session 2026-04-20 (current)
- [x] สร้าง GitHub repo ใหม่: `korpaiix-dev/korpai-landing` (public)
- [x] Git init local ที่ /root/korpai-landing
- [x] ตั้ง remote + .gitignore + PROGRESS.md (ไฟล์นี้)

---

## 🚧 IN PROGRESS

- [ ] First commit + push PROGRESS.md (about to do)

---

## 📋 NEXT (ตามลำดับ)

### Day 1 — Astro scaffold + Hero/Services/Process/Contact
- [ ] `npm create astro@latest .` (minimal template, TypeScript strict)
- [ ] ติดตั้ง Tailwind, Framer Motion, Lucide
- [ ] ตั้ง i18n (TH primary, EN secondary)
- [ ] ติดตั้ง Prompt font (Google Fonts)
- [ ] สร้าง design tokens (colors: ขาว/ฟ้าอ่อน/เขียวอ่อน, gradient, shadows)
- [ ] Layout.astro (header + footer + SEO meta)
- [ ] Components: Hero, Services, Process, Contact
- [ ] Commit + push "Day 1 — Hero/Services/Process/Contact"

### Day 2 — Portfolio + Pricing + FAQ + About
- [ ] Portfolio cards (ธุรกิจโม้ ~6 ราย: ร้านกาแฟ, คลินิก, อีคอมเมิร์ซ, โรงงาน, โรงเรียน, real estate)
- [ ] Pricing: "ปรึกษาฟรี" CTA อย่างเดียว
- [ ] FAQ accordion
- [ ] About page (story, value prop, contact)
- [ ] Commit + push "Day 2 — Portfolio/Pricing/FAQ/About"

### Day 3 — Blog + SEO articles + Chatbot mock
- [ ] Astro Content Collections setup
- [ ] 5 บทความ SEO/GEO (topic: AI Agent SME ไทย, Chatbot Line, Automation n8n, Dashboard Metabase, ROI AI)
- [ ] Chatbot mock UI (animated demo)
- [ ] Web AI agentic animations (typing, thinking states)
- [ ] Commit + push "Day 3 — Blog/Chatbot mock"

### Day 4 — Real AI Sales Agent chat widget
- [ ] Chat widget frontend (floating, light theme)
- [ ] Backend API (FastAPI หรือ Astro API routes)
- [ ] Session management
- [ ] OpenRouter routing (Haiku fast + Sonnet escalate)
- [ ] Handoff logic → Line/FB deep links
- [ ] Commit + push "Day 4 — AI Sales Agent"

### Day 5 — Polish + SEO/GEO + Deploy
- [ ] Sitemap, robots.txt, llms.txt
- [ ] OpenGraph images
- [ ] Schema.org JSON-LD (Organization, Service, FAQPage, BlogPosting)
- [ ] Performance (Lighthouse > 95)
- [ ] Deploy production: build → /var/www/korpai/ → nginx reload
- [ ] Commit + push "Day 5 — SEO/GEO + deploy"

---

## 🔥 BLOCKERS / DECISIONS NEEDED

- [ ] **DNS**: ยังต้องยืนยัน www. subdomain + HSTS (ปัจจุบัน korpai.co ทำงานแล้ว, www.korpai.co ต้องเช็ค)
- [ ] **AI model budget**: ยังไม่คุยว่า chat agent ใช้ model อะไร → Haiku + Sonnet รวม budget/เดือน?
- [ ] **Line OA / FB Page URL**: ต้องได้ link ต้นทางที่ chat agent จะส่งต่อ

---

## 📁 KEY PATHS (VPS)

| Purpose | Path |
|---|---|
| Landing repo (local) | `/root/korpai-landing/` |
| Landing serve root | `/var/www/korpai/` |
| Nginx config | `/etc/nginx/sites-enabled/korpai` |
| SSL cert (Certbot) | `/etc/letsencrypt/live/korpai.co/` |
| Old archived repo | `/root/prod/korp-ai-automation/` (don't touch) |

## 🔗 IMPORTANT URLs

- Landing live: https://korpai.co (placeholder)
- GitHub repo: https://github.com/korpaiix-dev/korpai-landing
- VPS console: https://cloud.digitalocean.com/droplets/558619958/terminal/ui/
- VPS IP: 139.59.123.146

## 🔐 CREDENTIALS NOTE

- GitHub PAT stored in git remote URL (rotate before archiving repo publicly)
- SSH: use DigitalOcean web console (no local SSH key setup)

---

## 🚨 RULES (บอสกำชับ)

1. **Git push ก่อน/หลังทำงานทุกครั้ง** — commit message ชัดเจน + อัปเดต PROGRESS.md
2. **Portfolio ห้ามเปิดชื่อลูกค้าจริง** — ใช้ธุรกิจโม้ได้แต่ไม่น่าเกลียด
3. **Pricing = "ปรึกษาฟรี" เท่านั้น** — ไม่โชว์ราคาแพ็กเกจ
4. **ห้ามทำงานซ้ำ** — อ่านไฟล์นี้ก่อนเริ่มเสมอ

---

## 📝 SESSION LOG

### 2026-04-20 — Session #2
- สร้าง repo ใหม่ (คนละ repo กับ `korp-ai-automation` ที่มี code Lion/sanitizer project อื่น)
- Setup git workflow + PROGRESS.md tracker
- เตรียม Day 1 Astro scaffold

