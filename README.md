# KORP AI Landing — korpai.co

> Landing page ของ **KORP AI AUTOMATION** — AI Agency สำหรับ SME ไทย
> โดเมน: [korpai.co](https://korpai.co)
> Repo: [github.com/korpaiix-dev/korpai-landing](https://github.com/korpaiix-dev/korpai-landing)

---

## 0. ก่อนเริ่ม — repo นี้เป็นเฉพาะ landing page

Repo นี้เก็บแค่โค้ด landing page (public). **Source of truth ของทั้ง agency** อยู่ที่ repo กลางชื่อ **`korp-ai-hq`** (private):

- Master spec, project map, VPS inventory, credentials index, session memory, rules, playbook
- 👉 https://github.com/korpaiix-dev/korp-ai-hq (ขออนุญาตบอสไผ่ก่อนเข้า)

ถ้าเป็น session ใหม่ที่ต้องสานงานต่อ — **เริ่มอ่านที่ `korp-ai-hq` ก่อน** แล้วค่อยกลับมาทำงานใน repo นี้ จะไม่ทำงานซ้ำซ้อน

---

## 1. โปรเจกต์นี้คืออะไร

เว็บไซต์ **หน้าเดียวครบ** (Multi-section single-page + blog + portfolio) ที่ทำหน้าที่เป็น:

1. **หน้าร้าน (Sales page)** — อธิบายบริการ AI Agent / Chatbot / Automation / Dashboard ให้ SME ไทยเข้าใจและตัดสินใจติดต่อ
2. **Lead magnet** — มี AI Sales Agent chat widget ฝังหน้าเว็บ คอยให้ข้อมูลเบื้องต้น 24/7 แล้วส่งต่อลูกค้าเข้า Line OA / Facebook Page (ไม่จบงานหน้าเว็บ — ปิดการขายในแชท Line/FB ตามเดิม)
3. **SEO / GEO hub** — บทความ 5+ เรื่องสำหรับให้ Google และ AI search engines (Perplexity, ChatGPT search, Gemini) อ้างอิงถึง KORP AI เมื่อมีคนค้นหาเรื่อง AI Agent SME ไทย
4. **Portfolio showcase** — โชว์ผลงานลูกค้า (ไม่เปิดชื่อจริง ใช้ persona ของธุรกิจ)

## 2. ทำมาเพื่ออะไร

- **วัตถุประสงค์ธุรกิจ:** สร้างช่องทางรับลูกค้าใหม่ (inbound lead) ให้ KORP AI AUTOMATION โดยไม่ต้องพึ่ง cold outreach
- **กลุ่มเป้าหมาย:** เจ้าของธุรกิจ SME ไทย (10-200 พนักงาน) ที่เริ่มสนใจ AI แต่ยังไม่รู้ว่าต้องเริ่มยังไง
- **KPI:**
  - Lead ผ่าน chat widget ≥ 30/เดือน
  - Lead ผ่าน Line/FB direct ≥ 50/เดือน
  - Organic SEO traffic ≥ 2,000 sessions/เดือน ภายใน 3 เดือน
  - Lighthouse score ≥ 95 ทุกหน้า

## 3. Tech Stack

| Layer | Choice | ทำไมเลือก |
|---|---|---|
| Framework | **Astro 4.x** | Static-first → SEO/GEO ดี, ขึ้นเร็ว, มี island architecture สำหรับ widget |
| Styling | **Tailwind CSS 3** | Dev เร็ว, bundle เล็ก, design tokens ควบคุมสีได้ชัด |
| Animations | **Framer Motion** | สำหรับ "Web AI agentic" vibe — typing, thinking, transitions |
| Icons | **Lucide React** | Light-weight, consistent |
| Font | **Prompt** (Google Fonts) | อ่านภาษาไทยดี, modern, เข้ากับ light theme |
| i18n | **Astro i18n** | TH primary, EN secondary |
| Content | **Astro Content Collections** | Blog + portfolio ใช้ MD/MDX ที่ type-safe |
| Chat backend | **FastAPI (Python)** | Reuse pattern จาก client projects อื่น ๆ ของ KORP AI |
| LLM routing | **OpenRouter** | รองรับ Haiku (เร็ว) → Sonnet (คิดซับซ้อน) fallback |
| Session store | **Redis** (ใช้ container เดิมของ VPS) | เก็บ chat session state |
| Web server | **Nginx** | Reverse proxy + SSL termination (Let's Encrypt ผ่าน Certbot) |
| Hosting | **DigitalOcean Droplet** | VPS 139.59.123.146 (korpaiix-server) |

## 4. โครงสร้างโปรเจกต์ (ตาม plan — Day 1 เป็นต้นไป)

```
korpai-landing/
├── PROGRESS.md              # Single source of truth ของ session
├── README.md                # ไฟล์นี้
├── .env.example             # Template ของ environment variables
├── .gitignore
├── docs/
│   ├── ARCHITECTURE.md      # รายละเอียดสถาปัตยกรรม
│   └── DEPLOYMENT.md        # ขั้นตอน deploy
├── snapshots/               # เก็บ snapshot ของ placeholder/landing เก่า
├── site/                    # Astro project (Day 1 ขึ้นไป)
│   ├── astro.config.mjs
│   ├── tailwind.config.mjs
│   ├── tsconfig.json
│   ├── package.json
│   ├── public/              # static assets (og-image, favicon, robots.txt, llms.txt)
│   └── src/
│       ├── layouts/         # Layout.astro (header + footer + SEO meta)
│       ├── components/
│       │   ├── Hero.astro
│       │   ├── Services.astro
│       │   ├── Process.astro
│       │   ├── Portfolio.astro
│       │   ├── Pricing.astro
│       │   ├── FAQ.astro
│       │   ├── About.astro
│       │   ├── Contact.astro
│       │   └── ChatWidget.astro   # AI Sales Agent floating widget
│       ├── content/
│       │   ├── blog/        # 5+ SEO/GEO articles
│       │   └── portfolio/   # 6 ธุรกิจ persona
│       ├── pages/
│       │   ├── index.astro
│       │   ├── blog/
│       │   ├── portfolio/
│       │   └── api/         # Chat widget API endpoints (fallback ถ้าไม่ใช้ FastAPI)
│       └── styles/
│           └── global.css
├── chat-backend/            # FastAPI chat agent (Day 4)
│   ├── main.py
│   ├── agents.py
│   ├── routers.py
│   ├── requirements.txt
│   └── Dockerfile
└── scripts/
    ├── deploy.sh            # build + copy to /var/www/korpai + reload nginx
    └── dev.sh               # local dev (astro dev + uvicorn)
```

## 5. วิธีติดตั้ง / Setup (local dev)

### Prerequisites
- Node.js ≥ 20 (ใช้ 24.14.0 บน VPS)
- npm ≥ 10
- Python ≥ 3.11 (สำหรับ chat backend)
- Redis (ถ้ารัน chat backend — สามารถใช้ container Redis ที่มีอยู่บน VPS ได้)

### 1. Clone + install
```bash
git clone https://github.com/korpaiix-dev/korpai-landing.git
cd korpai-landing
cp .env.example .env     # แล้วแก้ค่าให้ครบ
cd site
npm install
```

### 2. Run dev server
```bash
# Frontend (Astro)
cd site
npm run dev              # → http://localhost:4321

# Backend (FastAPI chat agent — Day 4 ขึ้นไป)
cd chat-backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8100
```

### 3. Build production
```bash
cd site
npm run build            # output → site/dist/
```

## 6. Environment Variables

ดู [`.env.example`](./.env.example) สำหรับ template เต็ม สรุปกลุ่มหลัก:

| กลุ่ม | ตัวแปรหลัก | ใช้ทำอะไร |
|---|---|---|
| Site meta | `PUBLIC_SITE_URL`, `PUBLIC_SITE_NAME` | Canonical URL + brand name |
| AI Chat | `OPENROUTER_API_KEY`, `OPENROUTER_MODEL_FAST`, `OPENROUTER_MODEL_SMART` | LLM routing สำหรับ AI Sales Agent |
| Handoff | `PUBLIC_LINE_OA_URL`, `PUBLIC_FB_PAGE_URL`, `PUBLIC_PHONE`, `PUBLIC_EMAIL` | Deep links ที่ agent ใช้ส่งต่อลูกค้า |
| Session | `SESSION_SECRET`, `REDIS_URL` | Chat widget session state |
| Analytics | `PUBLIC_GA_ID`, `PUBLIC_UMAMI_URL` (optional) | Traffic tracking |
| Notifications | `SLACK_WEBHOOK_URL` (optional) | แจ้งเตือนเมื่อมี lead ใหม่ |
| Rate limit | `RATE_LIMIT_WINDOW`, `RATE_LIMIT_MAX` | กันสแปม chat widget |

> **⚠️ ห้าม commit `.env`** (อยู่ใน `.gitignore` แล้ว) — ตัวแปร `PUBLIC_*` เท่านั้นที่ safe ฝังใน client bundle ของ Astro

## 7. Deploy

ดู [`docs/DEPLOYMENT.md`](./docs/DEPLOYMENT.md) ฉบับเต็ม สรุป:

```bash
# บน VPS
cd /root/korpai-landing
git pull
cd site && npm install && npm run build
sudo cp -r dist/* /var/www/korpai/
sudo systemctl reload nginx
```

Nginx config อยู่ที่ `/etc/nginx/sites-enabled/korpai` — serve static จาก `/var/www/korpai/` + reverse proxy `/api/chat/*` → chat backend (port 8100)

## 8. Workflow กฎของ repo

1. **อ่าน [`PROGRESS.md`](./PROGRESS.md) ก่อนเริ่มงานเสมอ** — จะรู้ว่า session ก่อนหน้าทำอะไรถึงไหน
2. **Git push ก่อน+หลังทุก session** — commit message ชัดเจน + อัปเดต PROGRESS.md ด้วย
3. **ห้ามเปิดชื่อลูกค้าจริงใน portfolio** — ใช้ persona
4. **Pricing = "ปรึกษาฟรี" เท่านั้น** — ไม่โชว์ราคาแพ็กเกจ
5. **Commit message รูปแบบ:** `<type>(<scope>): <subject>`
   - types: `feat`, `fix`, `chore`, `docs`, `style`, `refactor`, `perf`, `test`
   - ตัวอย่าง: `feat(hero): add Hero section with CTA`

## 9. Roadmap

| Day | Scope | Status |
|---|---|---|
| 0 | Cleanup + scaffold + docs | ✅ Done |
| 1 | Astro + Hero/Services/Process/Contact | ⏳ Next |
| 2 | Portfolio + Pricing + FAQ + About | ⏳ |
| 3 | Blog + SEO/GEO articles + Chatbot mock | ⏳ |
| 4 | Real AI Sales Agent chat widget + backend | ⏳ |
| 5 | Polish + SEO/GEO meta + Deploy prod | ⏳ |

## 10. License

Proprietary — © KORP AI AUTOMATION 2026. ห้ามทำซ้ำ / ดัดแปลง โดยไม่ได้รับอนุญาตเป็นลายลักษณ์อักษร
