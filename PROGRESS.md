# KORP AI Landing — PROGRESS

> Live checklist · อัปเดตทุก commit ที่กระทบ phase/task
> **Owner:** บอสไผ่ (korpaiix@gmail.com) · **Repo:** https://github.com/korpaiix-dev/korpai-landing · **Prod:** https://korpai.co
> **VPS:** 139.59.123.146 · `/root/korpai-landing` · serve `/var/www/korpai/` via host nginx
> **Workflow:** ดู `korp-ai-hq/DEV_VPS_WORKFLOW.md` — ทุก commit → push → deploy → verify

---

## 🎯 CURRENT PHASE

**Day 3 — Blog + SEO articles + Chatbot mock UI** — 🟡 ยังไม่เริ่ม (Day 1–2 เสร็จแล้ว)
**Pending deploy:** commits `f4686ca` (real logo) + `e3b371c` (Opera perf fix) ยังค้างบน VPS
**Next immediate:** boss paste deploy command บน SSH → verify → เริ่ม Day 3

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
- [x] `ff98511` — tone down site-wide ambient backdrop (Safari/FF smoothness)
- [x] `e3b371c` — kill `mix-blend-mode:screen` + orb/halo animations in Hero (Opera lag) **⚠ not deployed yet**

### Brand
- [x] `f4686ca` — swap placeholder logos with boss's real Icon/Horizontal/Stacked + favicon + apple-touch-icon **⚠ not deployed yet**

---

## 🚧 IN PROGRESS

- [ ] **Deploy pending commits** (`f4686ca` + `e3b371c`) — รอ boss paste SSH deploy command
- [ ] Verify Opera smooth scroll ตรงกับ expectation

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
- [ ] `sitemap.xml` (Astro integration auto) + `robots.txt` + `llms.txt`
- [ ] Auto-gen OpenGraph images per route
- [ ] Schema.org JSON-LD: Organization ✅ / FAQPage ✅ / Service / BlogPosting
- [ ] Lighthouse audit ≥ 95 ทั้ง 4 หมวด · LCP < 2s · JS < 150KB
- [ ] Full deploy checklist ใน `docs/DEPLOYMENT.md` §7
- [ ] Final smoke test flow: เข้า Hero → scroll ทุก section → กด LINE/FB CTA → verify URL

### Phase 1.5 — Docker + auto-pull migration (หลัง landing เสร็จ)
- [ ] `Dockerfile` (multi-stage: node build → nginx-alpine serve)
- [ ] `docker-compose.yml` — `landing` + `ttyd` services
- [ ] host nginx reverse_proxy → container ports
- [ ] `scripts/auto-pull.sh` + cron entry
- [ ] embed commit SHA → `version.txt` → Claude verify ผ่าน curl
- [ ] migrate existing `/var/www/korpai/` static → container

---

## 🔥 BLOCKERS / NEED DECISION

- [ ] **Pricing tier numbers:** ราคาที่ผมใส่ (฿15k/฿49k) เป็นเลขเดา — boss confirm หรือแก้
- [ ] **Portfolio = real vs mock:** 6 case เป็น persona หมด — ตอน Day 3 เปลี่ยนเป็น case จริงไหม หรือปล่อยไว้แบบนี้
- [ ] **FAQ Q10 claim:** "ลูกค้าบางรายอยู่กับเรา 12+ เดือน" — เขียนไว้แต่ถ้ายังไม่มีลูกค้าจริงต้องแก้
- [ ] **Tone-of-voice:** ใช้ "เรา" ทั่วเว็บแล้ว — confirm OK

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
