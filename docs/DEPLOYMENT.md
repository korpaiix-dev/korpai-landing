# Deployment — KORP AI Landing

## 1. Environments

| Env | URL | VPS path | Branch |
|---|---|---|---|
| Production | https://korpai.co | `/var/www/korpai/` (static) + systemd chat-backend | `main` |
| Local dev | http://localhost:4321 | — | any |

## 2. Prerequisites (first-time only)

### 2.1 DNS
- `A    korpai.co       → 139.59.123.146`
- `A    www.korpai.co   → 139.59.123.146`
- TTL 300s

### 2.2 Nginx + SSL
```bash
# Install (done already on VPS)
sudo apt install -y nginx certbot python3-certbot-nginx

# SSL cert
sudo certbot --nginx -d korpai.co -d www.korpai.co

# Check cert auto-renew
sudo systemctl list-timers | grep certbot
```

### 2.3 Nginx config
`/etc/nginx/sites-enabled/korpai` (ต้องแก้ให้ตรงกับ architecture ใหม่):

```nginx
server {
    listen 80;
    server_name korpai.co www.korpai.co;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name korpai.co www.korpai.co;

    ssl_certificate     /etc/letsencrypt/live/korpai.co/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/korpai.co/privkey.pem;
    include             /etc/letsencrypt/options-ssl-nginx.conf;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Static root — Astro build output
    root /var/www/korpai;
    index index.html;

    # Rate limit zone
    limit_req_zone $binary_remote_addr zone=chat_api:10m rate=20r/m;

    # Chat API → FastAPI backend
    location /api/chat/ {
        limit_req zone=chat_api burst=10 nodelay;

        proxy_pass         http://127.0.0.1:8100/;
        proxy_http_version 1.1;
        proxy_set_header   Host               $host;
        proxy_set_header   X-Real-IP          $remote_addr;
        proxy_set_header   X-Forwarded-For    $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto  $scheme;
        proxy_read_timeout 30s;
    }

    # Static assets (cache 1y)
    location ~* \.(js|css|woff2|woff|ttf|eot|svg|png|jpg|jpeg|gif|webp|avif|ico)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        try_files $uri =404;
    }

    # HTML fallback (SPA-like but Astro MPA)
    location / {
        try_files $uri $uri/ $uri.html /404.html;
    }
}
```

Reload after edit:
```bash
sudo nginx -t && sudo systemctl reload nginx
```

## 3. Frontend deploy flow

### 3.1 Manual (first few runs — รู้ว่าเกิดอะไรขึ้นบ้าง)
```bash
cd /root/korpai-landing
git pull
cd site
npm ci                               # reproducible install
npm run build                        # → site/dist/
sudo rm -rf /var/www/korpai.bak
sudo mv /var/www/korpai /var/www/korpai.bak   # safety backup
sudo mkdir -p /var/www/korpai
sudo cp -r site/dist/* /var/www/korpai/
sudo chown -R www-data:www-data /var/www/korpai
sudo systemctl reload nginx
```

### 3.2 Automated (script — ใช้หลัง validate flow แล้ว)
`scripts/deploy.sh` (Day 5 สร้าง):
```bash
#!/usr/bin/env bash
set -euo pipefail

echo "==> git pull"
cd /root/korpai-landing && git pull

echo "==> npm ci + build"
cd site && npm ci && npm run build

echo "==> backup + swap"
TS=$(date +%Y%m%d-%H%M%S)
sudo mv /var/www/korpai /var/www/korpai.$TS
sudo mkdir -p /var/www/korpai
sudo cp -r dist/* /var/www/korpai/
sudo chown -R www-data:www-data /var/www/korpai

echo "==> nginx reload"
sudo nginx -t && sudo systemctl reload nginx

echo "==> cleanup old backups (keep 3 latest)"
ls -1dt /var/www/korpai.* 2>/dev/null | tail -n +4 | xargs -r sudo rm -rf

echo "==> done. Check: https://korpai.co"
```

## 4. Backend deploy (FastAPI chat service)

### 4.1 First-time setup
```bash
cd /root/korpai-landing/chat-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env   # แล้วกรอกค่าจริง
```

### 4.2 Systemd service
สร้าง `/etc/systemd/system/korpai-chat.service`:
```ini
[Unit]
Description=KORP AI Chat Backend (FastAPI)
After=network.target redis.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/korpai-landing/chat-backend
EnvironmentFile=/root/korpai-landing/.env
ExecStart=/root/korpai-landing/chat-backend/.venv/bin/uvicorn main:app \
          --host 127.0.0.1 --port 8100 --workers 2
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Enable + start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable korpai-chat
sudo systemctl start korpai-chat
sudo systemctl status korpai-chat
```

### 4.3 Update backend
```bash
cd /root/korpai-landing
git pull
cd chat-backend
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart korpai-chat
```

## 5. Rollback

```bash
# Frontend rollback — ใช้ backup ที่ script ทำไว้
sudo ls -1dt /var/www/korpai.*           # ดูรายการ backup
sudo rm -rf /var/www/korpai
sudo mv /var/www/korpai.<timestamp> /var/www/korpai
sudo systemctl reload nginx

# Backend rollback — ใช้ git
cd /root/korpai-landing
git log --oneline -10
git checkout <prev-commit>
sudo systemctl restart korpai-chat
```

## 6. Monitoring / Logs

```bash
# Nginx access/error
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Chat backend
sudo journalctl -u korpai-chat -f

# Certbot renewal
sudo certbot certificates
sudo certbot renew --dry-run
```

## 7. Smoke test checklist (หลัง deploy ทุกครั้ง)

- [ ] `curl -I https://korpai.co` → 200 + HSTS header
- [ ] `curl https://korpai.co/robots.txt` → OK
- [ ] `curl https://korpai.co/sitemap.xml` → OK
- [ ] เข้าเว็บจริง — Hero render ครบ, ไม่มี layout shift
- [ ] Chat widget เปิด → ส่งทัก "สวัสดี" → ได้ reply
- [ ] Click "ติดต่อ Line" → redirect ถูก
- [ ] Lighthouse score ≥ 95 (mobile + desktop)
- [ ] Check Sentry / Slack notification ว่าไม่มี error spike

## 8. Cost ops (ประมาณการ)

| Item | Cost/month |
|---|---|
| DigitalOcean Droplet (existing) | $0 แชร์ |
| Domain korpai.co | ฿500/ปี ≈ ฿42/เดือน |
| Let's Encrypt SSL | ฟรี |
| OpenRouter credit (1k lead-msg) | ~$5-15 |
| Slack / Telegram notify | ฟรี |
| **Total ~month** | **$10-20** |
