# Deploy KORP AI Chat Backend to VPS — One-shot

> Run on the VPS (`139.59.123.146`) as `root`. Idempotent — safe to re-run any time.

## Prereqs (one-time)

1. SSH to VPS and make sure the auto-pull cron has already pulled the latest commit
   into `/root/korpai-landing` (cron runs every minute — see task #54).
2. Get an OpenRouter API key: <https://openrouter.ai/keys>

## Step 1 — Copy the install script and edit `.env`

```bash
# pull latest first
cd /root/korpai-landing && git pull

# run the installer once — first run will copy .env.example to .env and stop
bash chat-backend/deploy/install.sh
```

The first run **will fail on purpose** with a message like:

```
✗ Edit /opt/korpai-chat/.env and set OPENROUTER_API_KEY before continuing.
```

## Step 2 — Fill in the API key

```bash
nano /opt/korpai-chat/.env
```

Set `OPENROUTER_API_KEY=sk-or-v1-…` (your real key). Save & exit.

Optional but recommended:
- `HANDOFF_WEBHOOK_URL=` — Slack incoming webhook to get notified when a lead asks for handoff.

## Step 3 — Re-run the installer

```bash
bash /root/korpai-landing/chat-backend/deploy/install.sh
```

This time it will:

1. rsync source → `/opt/korpai-chat/`
2. create `.venv` if missing + `pip install -r requirements.txt`
3. install systemd unit + enable + start
4. install nginx snippet `/etc/nginx/snippets/korpai-chat.conf`
5. patch `/etc/nginx/sites-enabled/korpai` to `include snippets/korpai-chat.conf;`
6. `nginx -t && reload`
7. health-check `127.0.0.1:8100/api/chat/health` and `https://korpai.co/api/chat/health`

You should see:

```
✓ backend healthy on 127.0.0.1:8100
✓ backend reachable through https://korpai.co/api/chat/health
```

## Step 4 — Smoke test from your laptop

```bash
# health
curl -s https://korpai.co/api/chat/health | jq

# session + first message
curl -s -X POST https://korpai.co/api/chat/session -c /tmp/k.txt | jq
curl -s -X POST https://korpai.co/api/chat/message \
  -H 'content-type: application/json' \
  -b /tmp/k.txt \
  -d '{"message":"ร้านกาแฟอยากได้ chatbot LINE"}' | jq
```

## Step 5 — Tell Claude when it's live

After step 4 returns a real reply from the model, tell me ("backend live") and I'll
re-import `<ChatWidget />` into `Layout.astro`, build, push — site auto-deploys
and the floating chat appears for visitors.

## Daily ops

```bash
systemctl status korpai-chat       # status
journalctl -u korpai-chat -f       # live logs
systemctl restart korpai-chat      # bounce after .env changes
```

## Update flow

Whenever the backend code changes in the repo:

```bash
cd /root/korpai-landing && git pull
bash chat-backend/deploy/install.sh   # idempotent — only restarts if needed
```

## Rollback

```bash
systemctl stop korpai-chat
systemctl disable korpai-chat
# remove the include line from /etc/nginx/sites-enabled/korpai (or just leave it — the
# upstream is gone but nginx will return 502 on /api/chat/* which the widget handles).
nginx -t && systemctl reload nginx
```
