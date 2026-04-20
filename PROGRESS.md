# KORP AI Landing Page — PROGRESS.md

> **วัตถุประสงค์ไฟล์นี้:** บันทึกสถานะงานล่าสุดเพื่อให้ session ถัดไปเข้าใจบริบททันที ไม่ทำงานซ้ำซ้อน
> **อัปเดตทุกครั้ง:** ก่อนเริ่มงาน (กำลังจะทำอะไร) และหลังจบงาน (ทำอะไรไปแล้ว / ยังเหลืออะไร)
> **Owner:** บอสไผ่ (korpaiix@gmail.com)
> **Repo:** https://github.com/korpaiix-dev/korpai-landing
> **Local path (VPS):** /root/korpai-landing
> **Prod domain:** https://korpai.co (serve from /var/www/korpai/ via nginx)

---

## 📌 CURRENT STATE (2026-04-20)

**Phase:** Day 0 — Setup & scaffolding **(COMPLETE)**
**Status:** 🟢 Repo + docs ครบ พร้อมลุย Day 1 ได้เลย
**Next action:** Day 1 — ติดตั้ง Astro + สร้าง Hero/Services/Process/Contact

**Docs ครบตามที่บอสขอ:**
- `README.md` (187 บรรทัด) — โปรเจกต์คืออะไร + ทำเพื่ออะไร + stack + structure + setup + workflow + roadmap
- `.env.example` (131 บรรทัด) — env vars ทุกหมวด (site/contact/AI/chat/redis/ratelimit/notify/analytics/SEO/feature flags)
- `docs/ARCHITECTURE.md` (144 บรรทัด) — high-level diagram + component responsibility + data flow + security + performance
- `docs/DEPLOYMENT.md` (238 บรรทัด) — DNS + nginx config + frontend/backend deploy + systemd + rollback + smoke test + cost ops
- `PROGRESS.md` (ไฟล์นี้) — session tracker

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
  - Sections: ครบชุด
  - Timeline: 3-5 วัน
  - Portfolio: ห้ามเปิดชื่อลูกค้าจริง, ใช้ persona ได้
  - Pricing: "ปรึกษาฟรี" เท่านั้น

### Session 2026-04-20 (current)
- [x] สร้าง GitHub repo ใหม่: `korpaiix-dev/korpai-landing` (public)
- [x] Git init local ที่ /root/korpai-landing + ตั้ง remote + PAT auth
- [x] `.gitignore` + PROGRESS.md + README.md (ฉบับสั้น)
- [x] snapshot `/var/www/korpai/index.html` เก็บที่ `snapshots/placeholder-2026-04-19.html`
- [x] First commit + push (`e8c7964`)
- [x] ตาม request บอส: เขียน docs ชุดเต็ม
  - [x] README.md ขยาย — 10 หัวข้อ (โปรเจกต์คืออะไร, ทำเพื่ออะไร, stack, structure, setup, env vars, deploy, workflow, roadmap, license)
  - [x] `.env.example` — ครอบคลุม 10 กลุ่ม env vars
  - [x] `docs/ARCHITECTURE.md` — diagram + component + data flow + security + performance
  - [x] `docs/DEPLOYMENT.md` — full deploy runbook

---

## 🚧 IN PROGRESS

- [ ] Commit + push docs batch (about to do)
- [x] Cross-link repo นี้ → `korp-ai-hq` (hub repo ส่วนกลาง) — เพิ่มหัวข้อ §0 ใน README

---

## 📋 NEXT (ตามลำดับ)

### Day 1 — Astro scaffold + Hero/Services/Process/Contact
- [ ] Create `site/` subdir
- [ ] `cd site && npm create astro@latest . -- --template minimal --typescript strict --install --no-git --yes`
- [ ] Add integrations: Tailwind, React (for chat island), sitemap
- [ ] Config: `astro.config.mjs` + `tailwind.config.mjs` + design tokens (สีขาว/ฟ้าอ่อน/เขียวอ่อน)
- [ ] ติดตั้ง Prompt font + Lucide + Framer Motion
- [ ] Layout.astro (header + footer + SEO meta + schema.org stub)
- [ ] Components: Hero, Services, Process, Contact (ภาษาไทยเต็ม)
- [ ] Build → preview → push

### Day 2 — Portfolio + Pricing + FAQ + About
- [ ] Portfolio cards (6 ธุรกิจ persona: ร้านกาแฟ, คลินิก, อีคอมเมิร์ซ, โรงงาน, โรงเรียน, real estate) — โม้ได้แต่ไม่น่าเกลียด
- [ ] Pricing: "ปรึกษาฟรี" CTA อย่างเดียว (ห้ามโชว์ราคา)
- [ ] FAQ accordion
- [ ] About page (story, value prop, contact)

### Day 3 — Blog + SEO articles + Chatbot mock
- [ ] Astro Content Collections setup
- [ ] 5 บทความ SEO/GEO (AI Agent SME ไทย, Chatbot Line, Automation n8n, Dashboard Metabase, ROI AI)
- [ ] Chatbot mock UI (animated demo สำหรับ marketing)
- [ ] Web AI agentic animations (typing, thinking states, shimmer)

### Day 4 — Real AI Sales Agent chat widget
- [ ] Chat widget frontend (floating, light theme, React island)
- [ ] `chat-backend/` — FastAPI skeleton ตาม ARCHITECTURE.md §2.3
- [ ] Session mgmt + Redis
- [ ] OpenRouter routing (Haiku + Sonnet)
- [ ] Handoff logic → Line/FB deep links + Slack notify
- [ ] Systemd service

### Day 5 — Polish + SEO/GEO + Deploy
- [ ] Sitemap, robots.txt, llms.txt
- [ ] OpenGraph images (auto-gen)
- [ ] Schema.org JSON-LD (Organization, Service, FAQPage, BlogPosting)
- [ ] Performance tuning (Lighthouse ≥ 95)
- [ ] Deploy production + nginx config update
- [ ] Smoke test ทั้ง checklist ใน `docs/DEPLOYMENT.md` §7

---

## 🔥 BLOCKERS / DECISIONS NEEDED

- [ ] **DNS www subdomain**: ต้อง confirm ว่า `www.korpai.co` ก็ชี้ IP เดียวกันไหม
- [ ] **Line OA URL + FB Page URL**: ต้องได้ link ต้นทางจริงของ KORP AI — ปัจจุบัน .env.example ใช้ placeholder `@korpai` / `korpai.automation`
- [ ] **OpenRouter API key**: บอสต้องสมัคร https://openrouter.ai/keys แล้วเติมใน `.env` (server-only)
- [ ] **Brand assets**: โลโก้ + OG image + favicon — ยังไม่มี, ใช้ placeholder ได้ไหม?
- [ ] **Tone of voice**: เว็บใช้สรรพนามอะไร? ("ผม" / "เรา" / "ทีม KORP AI") — ใน .env.example set เป็น "เรา"

---

## 📁 KEY PATHS (VPS)

| Purpose | Path |
|---|---|
| Landing repo (local) | `/root/korpai-landing/` |
| Landing serve root | `/var/www/korpai/` |
| Nginx config | `/etc/nginx/sites-enabled/korpai` |
| SSL cert (Certbot) | `/etc/letsencrypt/live/korpai.co/` |
| Old archived repo | `/root/prod/korp-ai-automation/` (don't touch — มี Lion/sanitizer จาก project อื่น) |

## 🔗 IMPORTANT URLs

- Landing live: https://korpai.co (placeholder)
- GitHub repo: https://github.com/korpaiix-dev/korpai-landing
- VPS console: https://cloud.digitalocean.com/droplets/558619958/terminal/ui/
- VPS IP: 139.59.123.146

## 🔐 CREDENTIALS NOTE

- GitHub PAT stored in git remote URL (rotate ทุก 90 วัน — ดู ARCHITECTURE.md §4)
- SSH: use DigitalOcean web console (ไม่มี SSH key setup)
- ไม่มี secret ใน repo — ทุกอย่างอยู่ใน `.env` (ignored)

---

## 🚨 RULES (บอสกำชับ)

1. **Git push ก่อน/หลังทำงานทุกครั้ง** — commit message ชัดเจน + อัปเดต PROGRESS.md ด้วย
2. **Portfolio ห้ามเปิดชื่อลูกค้าจริง** — ใช้ persona / ธุรกิจโม้ได้แต่ไม่น่าเกลียด
3. **Pricing = "ปรึกษาฟรี" เท่านั้น** — ไม่โชว์ราคาแพ็กเกจ
4. **ห้ามทำงานซ้ำ** — อ่านไฟล์นี้ก่อนเริ่มเสมอ
5. **Commit message format:** `<type>(<scope>): <subject>` — ดู README §8

---

## 📝 SESSION LOG

### 2026-04-20 — Session #2
- 00:50 สร้าง repo ใหม่ `korpaiix-dev/korpai-landing` (คนละ repo กับ `korp-ai-automation` ที่มี code Lion/sanitizer project อื่น)
- 00:52 First commit: scaffold + PROGRESS.md tracker + placeholder snapshot
- 01:00 ตามที่บอสขอ: เขียน docs ชุดเต็ม — README, .env.example, ARCHITECTURE, DEPLOYMENT
- 01:0x Commit #2: full project docs

### 2026-04-20 — Session #3 (hub bootstrap)
- สร้าง private hub repo **`korpaiix-dev/korp-ai-hq`** เป็น source of truth ของทั้ง agency
  - ใส่ไฟล์: README, SESSION_MEMORY, RULES, MASTER_SPEC, PROJECTS, VPS_INVENTORY, CREDENTIALS (index only), PROGRESS
  - `docs/` — ARCHITECTURE, COST_MODEL, DELIVERY_PLAYBOOK
  - `clients/charoenpon.md` (stub + DO-NOT-TOUCH: `charoenpon-postgres`)
  - `projects/korpai-landing.md` — project sheet + runbook อ้างกลับมาที่ repo นี้
- Repo นี้ (landing): เพิ่มหัวข้อ §0 ใน README ชี้ไปที่ hub เพื่อให้ session ใหม่อ่านก่อน
- ย้ำ ritual: **start = `git pull` + อ่าน SESSION_MEMORY.md ของ hub; end = update PROGRESS ทั้งสอง repo แล้ว commit + push**

