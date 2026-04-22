# KORP AI Landing — PROGRESS

> Live checklist · อัปเดตทุก commit ที่กระทบ phase/task
> **Owner:** บอสไผ่ (korpaiix@gmail.com) · **Repo:** https://github.com/korpaiix-dev/korpai-landing · **Prod:** https://korpai.co
> **VPS:** 139.59.123.146 · `/root/korpai-landing` · serve `/var/www/korpai/` via host nginx
> **Workflow:** ดู `korp-ai-hq/DEV_VPS_WORKFLOW.md` — ทุก commit → push → deploy → verify

---

## 🎯 CURRENT PHASE

**Full sprint (2026-04-22)** — 🟢 บอสสั่ง "ทำมาเลยให้มันสมบูรณ์ฺ100%" — 4 of 4 done
1. **#75 ChatWidget re-enable + 3 SEO blogs + 3 Gemini hero images** — commit `5b7e575` → live
   - `Layout.astro` re-import + render `<ChatWidget />`
   - `ChatWidget.astro`: graceful fallback (`GREETING_BACKEND_DOWN` + auto-handoff to Line/FB + composer disabled) เมื่อ `tryStartSession()` fail — ป้องกันหน้า broken ตอน backend ยังไม่ได้ run install.sh
   - 3 SEO blog ใหม่ (target keyword ไทย low-competition + ≥5 internal link/บทความ):
     - `diy-chatbot-sme-ไม่ต้องเขียนโค้ด.md` — เทียบ ManyChat/Chatfuel/Dialogflow/Tidio + 60-min setup
     - `automation-ราคา-sme-เท่าไหร่.md` — pricing 3 ระดับ (DIY/freelance/agency) + ROI formula + payback case
     - `google-sheet-automation-sme-n8n.md` — 5 use case + docker run + 5 ข้อควรระวัง
   - 3 hero image ใหม่จาก Gemini 3.1 Pro (1024×572 16:9, no-text guarantee):
     - `diy-chatbot.jpg` (92KB) · `automation-roi.jpg` (126KB) · `sheet-n8n-flow.jpg` (108KB)
   - Build: 23 pages (เพิ่มจาก 20 → 23) · blog index 9 posts (เพิ่มจาก 6 → 9)
   - Verified live: 9 blog slugs ใน `/blog/`, ทั้ง 3 image HTTP 200, ChatWidget toggle render ปกติ
2. **#74 Proposal docx — ครัวคุณยาย (fictional Thai restaurant)** — เสร็จ
   - `Downloads/proposal-kruakhunyai.docx` (17KB, 6 pages, A4 + Sarabun font)
   - 6 sections: Cover · Executive Summary · Solution (Chatbot+Automation+Dashboard) · Scope · Timeline 6-week · Pricing 120K + monthly + ROI 1.8 month payback · Terms (40/40/20 + IP + PDPA)
   - Validated PASS via `validate.py`

**1-2-3 sprint (2026-04-22)** — 🟢 ปิดแล้ว — 3 of 3 done
1. **#68 Wire chat backend → VPS** — เตรียมพร้อมรอบอสรัน 1 คำสั่ง
   - `chat-backend/deploy/install.sh` (idempotent: rsync + venv + pip + systemd + nginx auto-patch + health check)
   - `chat-backend/deploy/SETUP.md` (5-step boss guide)
   - `site/src/pages/privacy.astro` (PDPA-compliant — ก่อนหน้านี้ ChatWidget link ไป 404)
   - `Footer.astro` link → `/privacy`
   - Build verified: 20 pages (เพิ่ม /privacy)
   - Deploy: commit `2f3f16c` → live
   - **Action บอส:** SSH VPS · `bash /root/korpai-landing/chat-backend/deploy/install.sh` · กรอก `OPENROUTER_API_KEY` ใน `/opt/korpai-chat/.env` · re-run install · บอกผม → ผม re-import ChatWidget
2. **Agency client intake system** — pipeline + template พร้อมรับ lead จริง
   - `clients/_TEMPLATE.md` (copy-this schema)
   - `clients/_LEADS.md` (Hot/Warm/Cold/Lost funnel + conversion targets)
   - `clients/_INTAKE_QUESTIONS.md` (5 round-1 + 5 round-2 + red flags + auto-handoff trigger)
   - `clients/README.md` (workflow Lead → Proposal → Signed → In Progress)
   - Deploy: commit `1aebbeb` (hub repo)
3. **PageSpeed Insights official run** — สร้าง checklist ให้บอสกด (Google block sandbox)
   - `Downloads/korpai-pagespeed-checklist.md` (4 URL + ตารางบันทึกคะแนน + fallback Chrome DevTools Lighthouse)
   - **Action บอส:** กด PageSpeed 4 URL · ส่งคะแนนกลับ · ผมแก้ถ้า < 90

**Lighthouse audit + perf fix (2026-04-22)** — 🟢 ปิด task #71 — รอบ audit หลัง QA retrofit
- เครื่องมือ: PageSpeed API ติด quota 429, PageSpeed UI ค้าง, sandbox ไม่มี Chromium → ใช้ manual audit ผ่าน fetch + DOMParser ตรวจทุกเกณฑ์ Lighthouse
- ผล audit (4 URL ตัวแทน: `/`, `/services/ai-chatbot/`, `/portfolio/fashion-line-commerce/`, `/blog/rag-คืออะไร/`):
  - **SEO PERFECT** — title/desc/canonical/viewport/lang/charset/OG/twitter/JSON-LD ครบทุกหน้า (Service + CreativeWork + BlogPosting + Organization + FAQPage)
  - **A11y PERFECT** — h1=1, all imgs alt, 0 inaccessible links/buttons, all 4 landmarks ทุกหน้า
  - **Best Practices PERFECT** — https, doctype, theme-color, favicon ครบ
  - **Perf gap เจอ:** 18 imgs ขาด `width/height` → CLS เสี่ยง (landing 10/12, services 4/6, portfolio 4/6)
- Fix `3efb680`: เพิ่ม `width="1024" height="572" decoding="async"` (+ `fetchpriority="high"` บน hero) ใน 6 จุด img — Services.astro, Portfolio.astro, services/[slug] ×2, portfolio/[slug] ×2
- Verified live: services/ai-chatbot 6/6 imgs, portfolio/fashion 6/6 imgs, landing 10/10 imgs มี dimensions แล้ว
- **Last deploy:** 2026-04-22 — commit `3efb680` (perf img dims) → VPS auto-pull แล้ว ตรวจสอบ HTML production OK

**QA retrofit (2026-04-22)** — 🟢 ปิดแล้ว
- Layout.astro: ถอด `ChatWidget` import + render ออก (รอ task #68 backend wire-up — กัน /privacy 404 link โผล่ทุกหน้า)
- `src/pages/services/[slug].astro`: เพิ่ม Service + BreadcrumbList JSON-LD (4 หน้า)
- `src/pages/portfolio/[slug].astro`: เพิ่ม CreativeWork (case study) + BreadcrumbList JSON-LD (6 หน้า)
- `src/pages/404.astro` ใหม่: branded 404 พร้อม link กลับ + 4 service cards
- Blog 6 บทความ: เพิ่ม `heroImage` + `author` ใน frontmatter ทั้งหมด
- Blog internal links retrofit: ทุกบทความมี ≥3 lookup link ไป /services/, /portfolio/, blog อื่น (กฎใหม่: บทความใหม่ต้อง ≥5 internal link default)
- Build verified: 19 pages (เพิ่ม /404), JSON-LD `@type":"Service"` + `@type":"CreativeWork"` อยู่ใน HTML จริง
- Deploy: commit `dd604d2`

---

**Earlier — Overnight batch — site polish + Phase 1.5 foundation + FB migration plan** — 🟢 รอบนี้ทำค้างคืนตามที่บอสสั่ง "ไปทำส่วนอื่นมาให้จบเลย"
- OG default image `/og-default.png` (199KB, 1200x630, branded) ✅
- Dockerfile multi-stage + `docker-compose.yml` + `deploy/nginx.conf` + `.dockerignore` ✅
- `docs/DEPLOYMENT.md` §6.5 Phase 1.5 switchover plan (ยังไม่ execute บน prod) ✅
- `docs/FB_MIGRATION.md` — แผนย้าย FB Page + Line OA ไปผูกกับ `korpai.co` (บอสเป็นคนกดใน console) ✅
- Bug fix: `deploy/nginx.conf` location `/_astro/` → `/_assets/` ตาม astro.config ✅
- Site audit: `npm run build` ผ่าน 18 pages clean, sitemap ครบ, ไม่มี dead link/TODO ✅
**Last deploy:** 2026-04-21 — commit `d4479a3` (overnight batch: OG image + Phase 1.5 + FB plan) · verified live: og:image OK, 9 sections render, 12 images 0 broken
**Next (เช้าบอสตื่น):**
1. Gemini image gen — model "รวดเร็ว" ไม่ gen รูป ต้อง switch เป็น Imagen 3 / Gemini 2.5 Pro / DALL-E ก่อนต่อ
2. FB / Line migration — บอสส่ง meta-tag + Pixel ID กลับมา (อ่าน `docs/FB_MIGRATION.md` §8)
3. Docker switchover — ถ้าบอส go ก็ flip nginx block ไป `proxy_pass http://127.0.0.1:8080` (docs/DEPLOYMENT.md §6.5.3)

---

## ✅ DONE

### Scaffold & docs
- [x] `e8c7964` — repo init + gitignore + placeholder snapshot
- [x] full docs — README (187L), `.env.example` (131L), `docs/ARCHITECTURE.md`, `docs/DEPLOYMENT.md`
- [x] cross-link → `korp-ai-hq` (hub repo) §0 ใน README

### Day 1 — Astro scaffold + core sections
- [x] Astro 4 + Tailwind 3 + TypeScript strict + sitemap integration
- [x] Design tokens: navy/cyan/violet + IBM Plex Sans Thai Looped + Inter
- [x] `Layout.astro` (SEO meta + OG + Twitter card + Organization JSON-LD)
- [x] `Hero.astro` — Raycast-style diagonal beams + mouse parallax + stats row + LINE/FB chips
- [x] `Services.astro` — 4 services (AI Chatbot / Automation / Dashboard / Custom)
- [x] `ChatDemo.astro` — left-right animated chat demo
- [x] inline `Process` section (3 steps) in `index.astro`
- [x] `Footer.astro` + `Header.astro` — sticky nav pill

### Day 2 — Portfolio + Pricing + About + FAQ (`72f2a22`)
- [x] `Portfolio.astro` — 6 case personas (ร้านกาแฟ/คลินิก/อีคอมเมิร์ซ/โรงงาน/โรงเรียน/อสังหา) + 10 Unsplash photos
- [x] `Pricing.astro` — 3 tiers (Starter ฿15k+฿3.5k/mo, Growth ฿49k+฿8.5k/mo popular, Enterprise custom)
- [x] `About.astro` — story + 4 values + 12 stack chips
- [x] `FAQ.astro` — 10 คำถาม + FAQPage JSON-LD schema
- [x] restructure `index.astro` order: Hero → ChatDemo → Services → Process → Portfolio → Pricing → About → FAQ → Contact

### Perf fixes
- [x] `ff98511` — tone down site-wide ambient backdrop (Safari/FF smoothness) · deployed
- [x] `e3b371c` — kill `mix-blend-mode:screen` + orb/halo animations in Hero (Opera lag) · deployed 2026-04-21

### Brand
- [x] `f4686ca` — swap placeholder logos with boss's real Icon/Horizontal/Stacked + favicon + apple-touch-icon · deployed 2026-04-21

### Raycast-feel pass + pricing cleanup
- [x] `cb2fd06` — Services section Raycast-ified (eyebrow mono label, diagonal beam, glass cards + accent stripe, slide arrow CTA) + kp-eyebrow/kp-rc-card reusable utilities + auto-pull.sh cron script
- [x] `7526f8b` — remove numeric prices from landing (Pricing/Header/FAQ/ChatWidget) — ประเมินตามโจทย์ "ปรึกษาฟรี" แบบเดียว

### Day 3 — Blog system + 6 articles (deployed this round)
- [x] Astro Content Collections config (`src/content/config.ts`)
- [x] Blog list route `/blog/` — card grid, category color, reading minutes
- [x] Blog post route `/blog/[...slug]` — breadcrumb, typography scoped to `.kp-post-body`, CTA card
- [x] BlogPosting JSON-LD + canonical + OG per post
- [x] "บทความ" link added to Header nav (auto-routes back to `/#...` from blog pages)
- [x] 6 articles (Thai SME focused):
  - [x] `rag-คืออะไร` — RAG คืออะไร และทำไม SME ไทยควรรู้จัก
  - [x] `ai-chatbot-ร้านอาหาร-คาเฟ่` — Chatbot เริ่มยังไงใน 2 สัปดาห์
  - [x] `automation-ลดต้นทุน-sme` — 5 flow คืนเวลา 40+ ชม./เดือน
  - [x] `dashboard-sme-grafana-metabase-powerbi` — tool เลือกยังไง
  - [x] `line-oa-vs-messenger-vs-เว็บ` — channel strategy ปี 2026
  - [x] `prompt-engineering-sme-strategy` — template prompt ใช้ได้จริง

### Day 5 — Polish + SEO/GEO (deployed last round)
- [x] `@astrojs/sitemap` integration → auto-gen `/sitemap-index.xml` + `/sitemap-0.xml`
- [x] Pinned sitemap 3.2.1 (3.7+ ต้อง Astro 5 — เรา Astro 4)
- [x] `/llms.txt` — structured company brief for LLM/GEO agents
- [x] `/robots.txt` references sitemap-index.xml (มีแล้วแต่ verified)
- [x] Portfolio reframe → "ตัวอย่างโจทย์" + NDA note (เคารพ persona rule)
- [x] FAQ Q10 rewrite → ตัด "12+ เดือน" claim, พูดเรื่อง demo + NDA แทน
- [x] Build ผ่าน 8 pages — landing + blog index + 6 posts · ~1.5s build time

### Detail pages + ChatWidget removal (`f6afb53` — deployed this round)
- [x] ตัด ChatWidget ออก (import + tag + component file ลบหมด) ตามที่บอสสั่ง
- [x] `site/src/data/services.ts` — 4 services พร้อม highlights/whoFor/useCases/workflow/tech/timeline
- [x] `site/src/data/portfolio.ts` — 6 case personas พร้อม challenge/approach/outcome/tech/handoff
- [x] `/services/[slug].astro` dynamic route — hero + highlights + fit + use cases + process + tech + CTA + other services (4 pages)
- [x] `/portfolio/[slug].astro` dynamic route — hero + metric badge + challenge + approach + outcome + meta + CTA + more cases (6 pages)
- [x] Services.astro + Portfolio.astro refactor → import จาก data · การ์ดคลิกเข้า detail page
- [x] llms.txt เพิ่ม service + portfolio detail URLs สำหรับ GEO indexing
- [x] Build 18 pages (landing + 6 blog + 6 portfolio + 4 services + sitemap)

---

## 📋 NEXT

### Day 3 — Blog + SEO articles + Chatbot mock UI
- [ ] Astro Content Collections setup (`src/content/blog/`)
- [ ] Blog list route `/blog/` + blog post route `/blog/[slug]`
- [ ] BlogPosting JSON-LD schema per post
- [ ] 5 บทความ SEO/GEO focused Thai-SME:
  - [ ] "AI Chatbot สำหรับร้านอาหาร/คาเฟ่: เริ่มยังไงให้ใช้ได้จริง"
  - [ ] "Automation ลดต้นทุน SME: 5 flow ที่ทำแล้วเห็นผลใน 2 สัปดาห์"
  - [ ] "Dashboard สำหรับ SME: Grafana vs Metabase vs Power BI"
  - [ ] "Line OA vs Messenger vs เว็บ: AI ตอบลูกค้าช่องไหนคุ้มสุด"
  - [ ] "RAG คืออะไร และทำไม SME ไทยควรรู้จัก"
- [ ] Chatbot mock UI (floating bottom-right, animated, demo UX only — ยังไม่ต่อ backend)

### Day 4 — Real AI Sales Agent chat widget + backend
- [ ] Chat widget frontend (React island, floating, connected to API)
- [ ] `chat-backend/` — FastAPI skeleton ตาม `docs/ARCHITECTURE.md` §2.3
- [ ] Session mgmt + Redis DB 5
- [ ] OpenRouter routing (Haiku fast + Sonnet smart + Gemini fallback)
- [ ] Handoff logic → Line/FB deep links + Slack notify
- [ ] systemd service + Docker compose entry

### Day 5 — Polish + SEO/GEO + production deploy
- [x] `sitemap.xml` (Astro integration auto) + `robots.txt` + `llms.txt` — all serve 200 in build output
- [x] Default OpenGraph image `/og-default.png` (branded 1200x630, from `scripts/gen-og-image.py`)
- [x] Schema.org JSON-LD: Organization ✅ / FAQPage ✅ / BlogPosting ✅ (Service detail pages ใช้ meta+canonical+OG แต่ไม่มี dedicated Service JSON-LD — phase ถัดไป)
- [ ] Lighthouse audit ≥ 95 ทั้ง 4 หมวด · LCP < 2s · JS < 150KB (รอ deploy แล้วค่อยวัดบน prod)
- [x] Full deploy checklist ใน `docs/DEPLOYMENT.md` §7
- [ ] Final smoke test flow: เข้า Hero → scroll ทุก section → กด LINE/FB CTA → verify URL (ทำหลัง deploy)

### Phase 1.5 — Docker + auto-pull migration (หลัง landing เสร็จ)
- [x] `Dockerfile` (multi-stage: node:20-alpine build → nginx:1.27-alpine serve) + GIT_SHA→version.txt
- [x] `docker-compose.yml` — `landing` (127.0.0.1:8080:80) + `ttyd` (ops profile, 127.0.0.1:7681)
- [x] `deploy/nginx.conf` — in-container server, port 80, 1y cache `/_assets/`, 30d images/fonts, no-store `/version.txt`
- [x] `.dockerignore` — exclude node_modules, dist, .astro, .env*, .git
- [x] switchover plan documented (`docs/DEPLOYMENT.md` §6.5) — replace `root /var/www/korpai;` → `proxy_pass http://127.0.0.1:8080;`
- [x] `scripts/auto-pull.sh` + cron entry — ติดไว้แล้วรอบก่อน (commit `cb2fd06`)
- [ ] **Execute on prod** — `GIT_SHA=$(git rev-parse --short HEAD) docker compose up -d --build` (บอส go/no-go)

### Overnight batch (2026-04-21 night) — social + SEO ops docs
- [x] `docs/FB_MIGRATION.md` — 9-section plan (FB domain verify meta-tag, Page settings, CTA, Pixel/CAPI, Lead Ads, Line rich menu/webhook/Login/greeting, smoke tests, rollback, timeline, boss action items)
- [x] `scripts/gen-og-image.py` — reproducible 1200x630 OG generator (PIL, navy+cyan+violet, logo, English tagline)
- [x] Site audit — 18 pages build clean, sitemap-index.xml + sitemap-0.xml ครบ, robots+llms ดี, ไม่มี dead link/TODO
- [x] Bug fix — `deploy/nginx.conf` location `/_astro/` → `/_assets/` ให้ตรงกับ `astro.config.mjs`'s `build.assets`

---

## 🔥 BLOCKERS / NEED DECISION

- [x] **Pricing tier numbers:** เอาออกหมดแล้ว — หน้า Pricing ขายขอบเขตแทนราคา
- [x] **Portfolio = real vs mock:** รีไรท์ heading เป็น "ตัวอย่างโจทย์" + เพิ่ม disclaimer "persona · ตัวเลขจริงลูกค้าแตกต่างกัน"
- [x] **FAQ Q10 claim:** ลบ "12+ เดือน" ออก เปลี่ยนเป็น "มีผลงานให้ดูก่อนตัดสินใจไหม?" — เคารพ NDA
- [ ] **Tone-of-voice:** ใช้ "เรา" ทั่วเว็บแล้ว — confirm OK (น่าจะ OK ใช้มานานแล้วไม่มี feedback)
- [x] **OG image:** `/og-default.png` branded 199KB พร้อม — custom artistic pass ค่อย iterate หลังเปิด Pixel
- [ ] **Gemini image gen (task #58):** model "รวดเร็ว" ไม่ gen รูป ได้แค่ echo prompt — ต้อง switch เป็น Imagen 3 / 2.5 Pro หรือ DALL-E เช้านี้ก่อนเริ่มต่อ
- [ ] **FB / Line migration (boss-only):** อ่าน `docs/FB_MIGRATION.md` §8 — ส่ง meta-tag + Pixel ID กลับมาให้ hook เข้า Layout

---

## 📁 KEY PATHS (VPS)

| Purpose | Path |
|---|---|
| Landing repo | `/root/korpai-landing/` |
| Serve root | `/var/www/korpai/` |
| Nginx site | `/etc/nginx/sites-enabled/korpai` |
| SSL cert | `/etc/letsencrypt/live/korpai.co/` |
| Old archived | `/root/prod/korp-ai-automation/` (DO NOT TOUCH) |

## 🔗 IMPORTANT URLs

- Prod: https://korpai.co
- Repo: https://github.com/korpaiix-dev/korpai-landing
- VPS web console: https://cloud.digitalocean.com/droplets/558619958/terminal/ui/

## 🚨 RULES (บอสกำชับ)

1. Commit + push ทุก unit of work → อัปเดตไฟล์นี้ด้วย commit hash
2. Portfolio ห้ามเปิดชื่อลูกค้าจริง — persona OK
3. Pricing ไม่ fake — ต้อง confirm ก่อน ship
4. ห้ามแก้งาน repeated — อ่านไฟล์นี้ + `korp-ai-hq/SESSION_MEMORY.md` ก่อนเริ่ม
5. Commit message: `<type>(<scope>): <subject>` + body why
