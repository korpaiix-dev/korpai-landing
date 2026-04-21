# KORP AI — Landing page image prompt set

**Style lock:** **Mix 1+3** — Editorial photorealistic **with abstract tech overlay**
(Raycast / Linear / Stripe homepage feel).

- Real Thai people / real Thai business interiors — warm editorial grade
- Abstract tech overlay: floating UI cards, soft grid, cyan/violet glow
- No text, no watermark, no logo — 16:9 aspect ratio

**Model:** Gemini 3.1 Pro on account `korpaiix@gmail.com`
**Output path:** `site/public/assets/img/{slug}.jpg` (each page already
references this via the `img` field in `site/src/data/portfolio.ts` and
`site/src/data/services.ts`)

---

## Prompt skeleton (applied to every prompt)

```
editorial 16:9 photorealistic photo, {subject scene}.
cinematic warm color grade — clean white + soft teal shadow, shallow depth of field.
premium editorial aesthetic, Monocle / Apple keynote feel.

overlay subtle abstract tech elements (Raycast / Linear homepage style):
semi-transparent floating UI panels, soft cyan (#26D7F6) + violet (#7C5FFF)
glow accents, thin grid lines, minimal data-viz touches — integrated into
the scene, never dominating the real photo.

no text, no watermark, no logo. 8K.
```

---

## 10 production prompts — matched to real slugs

### Services — 4 images

**1. `ai-chatbot`** → `/services/ai-chatbot`
subject: Thai female support specialist, late 20s, headset on, warm smile,
at a minimal workstation. Soft daylight from left. Overlay: a single
floating chat-bubble UI card near her screen, very subtle cyan glow.

**2. `automation`** → `/services/automation`
subject: Thai duo (one female, one male), 30s, standing side-by-side at
a tall desk with two laptops open. Warm loft office. Overlay: thin lines
connecting abstract workflow nodes above the desk, cyan + violet glow.

**3. `dashboard`** → `/services/dashboard`
subject: Thai founder, 30s, seated at a glass table looking at a laptop —
reflection of soft glow on their face. Minimal modern office. Overlay:
translucent floating data cards + thin bar/line chart accents in cyan.

**4. `custom-ai`** → `/services/custom-ai`
subject: Thai consultant, 40s, at a quiet modern home office — white wall +
single warm lamp. Writing on a tablet. Overlay: delicate constellation of
abstract AI nodes + very subtle grid, violet-lean.

### Portfolio — 6 images

**5. `fashion-line-commerce`** — persona "พี่นิดแฟชั่น"
subject: Thai female boutique owner, late 20s–30s, in her small online
fashion boutique — racks of neutral-tone clothing, warm pendant light.
Wrapping an order at the counter, phone showing a LINE chat. Overlay:
subtle cart/order UI panel floating, cyan glow.

**6. `thai-restaurant-booking`** — persona "ครัวคุณยาย"
subject: Thai male restaurant manager, 30s, in warm wood + stone Thai-contemporary
restaurant. Checking reservation tablet at hostess stand. Overlay: calendar /
booking slots UI floating subtle, warm tungsten + cyan accent.

**7. `derma-clinic-admin`** — persona "Derma Clinic BKK"
subject: Thai female nurse/admin, 30s, at beauty clinic counter — cream/mocha
interior, stainless-steel aesthetic equipment. iPad in hand, soft professional
smile. Natural window light. Overlay: clean patient-record card floating, soft teal glow.

**8. `it-gadget-shop`** — persona "BKK Gadgets"
subject: Thai male shop owner, 30s, behind a clean counter of gadgets —
keyboards / earbuds / accessories displayed on a wood table. Scanning an
order on a tablet. Overlay: mini inventory/SKU UI card floating, cyan glow.

**9. `wellness-spa-booking`** — persona "Pure Wellness"
subject: Thai female spa receptionist, 30s, at a serene wooden spa counter
with a small orchid arrangement. Warm candle-tone lighting. Confirming a
booking on tablet. Overlay: soft calendar UI card + faint grid, warm + cyan.

**10. `specialty-coffee-upsell`** — persona "Brew & Co"
subject: Thai male barista-owner, 30s, at a specialty coffee bar — brass
espresso machine backdrop, warm timber counter. Placing a latte on the
counter while glancing at phone. Overlay: small order/upsell UI card
floating by the phone, cyan+violet glow.

---

## Workflow

1. Paste each prompt (one at a time) into Gemini 3.1 Pro at `gemini.google.com/u/1/app`.
2. Wait ~90s per image.
3. Click **"ดาวน์โหลดรูปภาพขนาดเต็ม"** → save as `{slug}.jpg`.
4. Drop files into `site/public/assets/img/`.
5. Update the `img` field for each persona/service in `portfolio.ts` /
   `services.ts` from the Unsplash URL to `/assets/img/{slug}.jpg`.
6. `npm run build` → commit + push → VPS auto-pull picks up in ~1 min.

Alternate: I can batch all 10 prompts one after another and let Gemini
queue them — but Pro model takes ~90s each, so 10 images = ~15 min total.
