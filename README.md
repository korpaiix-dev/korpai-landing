# KORP AI Landing — korpai.co

Modern landing page for **KORP AI AUTOMATION** — Thai AI Agency for SMEs.

## Stack
- Astro 4.x (static-first, SEO/GEO optimized)
- Tailwind CSS + Framer Motion + Lucide Icons
- Prompt font (Thai-optimized)
- AI Sales Agent chat widget (FastAPI backend, OpenRouter)

## Theme
Light & airy — white + soft blue + soft green. Easy to read, easy to contact.

## Status
See [PROGRESS.md](./PROGRESS.md) — updated every session.

## Local dev
```bash
npm install
npm run dev
```

## Deploy
```bash
npm run build
sudo cp -r dist/* /var/www/korpai/
sudo systemctl reload nginx
```

## Repo policy
- **Always read PROGRESS.md before starting work**
- **Commit + push before AND after every session**
- Portfolio must NOT use real client names
- Pricing = "ปรึกษาฟรี" only (no price tags)
