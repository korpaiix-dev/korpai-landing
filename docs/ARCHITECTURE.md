# Architecture — KORP AI Landing

## 1. High-level diagram

```
                       ┌──────────────────────────────────────────────┐
                       │            ผู้ใช้เว็บไซต์ (Browser)            │
                       └────────────┬─────────────────────────────────┘
                                    │ HTTPS
                                    ▼
                      ┌──────────────────────────────┐
                      │  Nginx  (Let's Encrypt SSL)  │
                      │  /etc/nginx/sites-enabled/   │
                      │          korpai              │
                      └────┬────────────────────────┬┘
                           │ static                 │ /api/chat/*
                           │ (index, blog,          │
                           │  portfolio)            │
                           ▼                        ▼
             ┌──────────────────────┐    ┌──────────────────────────┐
             │  /var/www/korpai/    │    │ Chat backend (FastAPI)   │
             │  Astro build output  │    │ 127.0.0.1:8100           │
             └──────────────────────┘    │                          │
                                         │ - Session mgmt           │
                                         │ - LLM routing            │
                                         │ - Handoff logic          │
                                         │ - Rate limiting          │
                                         └─┬────────────┬──────────┘
                                           │            │
                                           ▼            ▼
                                ┌─────────────┐   ┌──────────────┐
                                │   Redis     │   │ OpenRouter   │
                                │   127.0.0.1 │   │ LLM API      │
                                │   :6379/5   │   │ Haiku→Sonnet │
                                └─────────────┘   └──────────────┘
                                                        │
                                                        ▼
                                              ┌──────────────────┐
                                              │ Lead notification │
                                              │ (Slack / Tele /   │
                                              │  Email)           │
                                              └──────────────────┘
```

## 2. Component responsibilities

### 2.1 Astro frontend (`site/`)
- Static-first: Hero, Services, Process, Portfolio, Pricing, FAQ, About, Contact, Blog render เป็น HTML ธรรมดา ตอน build time
- Hydrate เฉพาะส่วนที่จำเป็น: Chat widget (island architecture)
- SEO / GEO built-in:
  - `<meta>` tags + OpenGraph
  - Schema.org JSON-LD (`Organization`, `Service`, `FAQPage`, `BlogPosting`)
  - Sitemap.xml auto-gen
  - `llms.txt` — ช่วยให้ AI crawler เข้าใจเว็บไว
- i18n: TH primary (`/`), EN secondary (`/en/`) — Day 5 ค่อยเปิด

### 2.2 Chat widget (React island ใน Astro)
- Floating button มุมขวาล่าง (light blue/green gradient)
- เปิดเป็น panel ซ้อนด้านข้าง (ไม่ modal เต็มจอ — เลี่ยงบัง content)
- States: idle / typing / thinking / awaiting-handoff / handoff-complete
- Animations: Framer Motion
- Messages เก็บ local state (useState) — ไม่ต้อง persist ฝั่ง client
- Session cookie (`korpai_chat_sid`) ผูกกับ backend session

### 2.3 Chat backend (`chat-backend/` — FastAPI)

```python
POST /api/chat/session          # สร้าง session ใหม่, set cookie
POST /api/chat/message          # ส่งข้อความ, รอ LLM reply
GET  /api/chat/history          # ดึง history ของ session
POST /api/chat/handoff          # ส่งต่อ → Line/FB + ส่ง Slack notify
POST /api/chat/feedback         # thumbs up/down
GET  /api/chat/health           # liveness
```

**Agent logic:**
1. รับข้อความ → classify intent (greeting / pricing / technical / ready-to-buy / faq / off-topic)
2. ตาม intent:
   - greeting / faq → Haiku ตอบทันที จาก knowledge base
   - pricing / technical → Sonnet (deep context + brand voice guard)
   - ready-to-buy → trigger handoff flow
3. Handoff flow:
   - Show "ส่งต่อทีม KORP AI ทาง Line / Facebook" buttons
   - Click → deep link ออก + ส่ง notification ไปหา owner
4. Safety:
   - Output sanitizer (กันข้อความเสี่ยง)
   - Rate limit per IP/session
   - System prompt ห้ามให้ราคาแบบเจาะจง → ต้อง handoff เสมอ

### 2.4 Data layer
- **Redis (DB 5)** — session state + rate limit counters
  - `session:<sid>` → JSON (messages, intent, started_at, last_active)
  - `rl:<ip>` → counter + TTL
- **File-based CMS** — Astro Content Collections (MD/MDX ใน git)
  - `src/content/blog/*.mdx`
  - `src/content/portfolio/*.mdx`
- **ไม่ใช้ database ใหญ่** สำหรับ MVP — ลด ops overhead

### 2.5 Infrastructure
- **VPS:** DigitalOcean Droplet `korpaiix-server` (139.59.123.146)
- **Nginx:** `/etc/nginx/sites-enabled/korpai`
  - `server_name korpai.co www.korpai.co`
  - SSL: Let's Encrypt managed by Certbot
  - Static: `root /var/www/korpai`
  - API proxy: `location /api/chat/ { proxy_pass http://127.0.0.1:8100/; }`
- **Systemd service:** `korpai-chat.service` รัน uvicorn
- **Docker (optional for chat backend)** — ใช้ Dockerfile ถ้าอยากแยกออก container

## 3. Data flow (typical chat session)

1. User เข้า `korpai.co` → Astro ส่ง HTML + widget JS
2. User click chat bubble → widget mount, เรียก `POST /api/chat/session`
3. Backend สร้าง `sid`, set cookie, return `{greeting: "..."}`
4. User พิมพ์ "อยากได้ chatbot ร้านกาแฟ" → `POST /api/chat/message`
5. Backend: Redis load session → classify intent (pricing) → Sonnet
6. Sonnet reply: "ยินดีครับ! ขอถามเพิ่ม 3 ข้อ ..." → บันทึก Redis → return reply
7. หลัง 3-5 turn → intent = ready-to-buy → show handoff buttons
8. User click "เปิด Line" → redirect + `POST /api/chat/handoff` ส่ง Slack notify
9. Slack channel ได้ลิงก์ session + ข้อมูลเบื้องต้น → ทีมรับต่อใน Line

## 4. Security considerations
- **CSP headers** ใน Nginx (block inline script ยกเว้น nonce)
- **Secrets**: ใน `.env` เท่านั้น (ไม่มี `PUBLIC_` prefix)
- **Rate limit** ที่ backend + Nginx level (limit_req_zone)
- **Input validation**: Pydantic models, max message length 1000 chars
- **Output sanitizer**: strip unsafe HTML/URLs ก่อนส่งกลับ client
- **Session cookie**: `HttpOnly` + `Secure` + `SameSite=Lax`
- **PAT** สำหรับ git: rotate ทุก 90 วัน (ปัจจุบันเก็บใน git remote URL — ต้องแยกเข้า git credential helper ก่อน production)

## 5. Performance targets
| Metric | Target | Tool |
|---|---|---|
| Lighthouse Performance | ≥ 95 | Chrome DevTools |
| LCP | < 2.0s | Web Vitals |
| CLS | < 0.1 | Web Vitals |
| Total bundle (gz) | < 150KB | rollup analyzer |
| Chat reply latency (fast) | < 2s | Haiku P50 |
| Chat reply latency (smart) | < 6s | Sonnet P50 |

## 6. Future extensions
- A/B testing บน Hero CTA
- LINE Login ถ้าต้องการ lead qualification ก่อน handoff
- Webhook รับ messages จาก LINE/FB เข้า dashboard กลาง
- Multi-tenant — ใช้ landing pattern นี้ขายเป็น service ให้ลูกค้า SME รายอื่น
