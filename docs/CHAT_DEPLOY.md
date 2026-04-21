# Chat Backend — VPS Deployment Runbook

Target VPS: `139.59.123.146` (Ubuntu 22.04)
Backend path: `/opt/korpai-chat/`
Service name: `korpai-chat.service`
Listens on: `127.0.0.1:8100` (nginx proxies `/api/chat/*` → here)

---

## Prereqs (one-time)

1. Get an OpenRouter API key at https://openrouter.ai/keys — needs a loaded balance.
2. Decide on a handoff webhook (optional — Slack incoming webhook works).

## One-shot install

Run these from your laptop:

```bash
# 1. Sync code up
rsync -a --delete \
  --exclude '.venv' --exclude '.env' --exclude '__pycache__' \
  chat-backend/ root@139.59.123.146:/opt/korpai-chat/

# 2. Create venv + install deps (remote)
ssh root@139.59.123.146 '
  set -e
  cd /opt/korpai-chat
  python3 -m venv .venv
  .venv/bin/pip install --upgrade pip
  .venv/bin/pip install -r requirements.txt
'

# 3. Upload .env secrets (locally edit first, DO NOT commit)
cp chat-backend/.env.example /tmp/korpai-chat.env
# → fill in OPENROUTER_API_KEY etc.
scp /tmp/korpai-chat.env root@139.59.123.146:/opt/korpai-chat/.env
ssh root@139.59.123.146 'chmod 600 /opt/korpai-chat/.env'

# 4. Install systemd unit + start
scp chat-backend/deploy/korpai-chat.service \
    root@139.59.123.146:/etc/systemd/system/korpai-chat.service
ssh root@139.59.123.146 '
  systemctl daemon-reload
  systemctl enable --now korpai-chat
  sleep 2
  systemctl status korpai-chat --no-pager
  curl -s http://127.0.0.1:8100/api/chat/health
'

# 5. Wire nginx proxy
scp chat-backend/deploy/nginx-chat.conf \
    root@139.59.123.146:/etc/nginx/snippets/korpai-chat.conf

# 6. Add `include snippets/korpai-chat.conf;` inside the HTTPS server block of
#    /etc/nginx/sites-enabled/korpai (same file the static site uses)
#    Then test + reload:
ssh root@139.59.123.146 'nginx -t && systemctl reload nginx'

# 7. Smoke test from laptop
curl -s https://korpai.co/api/chat/health | jq
```

Expected health response:

```json
{"ok": true, "sessions": 0}
```

## Smoke test the full flow

```bash
curl -s -c /tmp/k.cookies -X POST https://korpai.co/api/chat/session | jq
curl -s -b /tmp/k.cookies -X POST https://korpai.co/api/chat/message \
  -H 'content-type: application/json' \
  -d '{"message":"ร้านกาแฟอยากได้ chatbot LINE ตอบออเดอร์อัตโนมัติ"}' | jq
```

Expect `{reply: "<Thai text>", handoff: false, intent: "faq", model: "anthropic/claude-haiku-4.5"}`.

## Logs

```bash
ssh root@139.59.123.146 'journalctl -u korpai-chat -f --no-pager'
```

## Rollback

```bash
ssh root@139.59.123.146 'systemctl stop korpai-chat && systemctl disable korpai-chat'
# Then remove `include snippets/korpai-chat.conf;` from /etc/nginx/sites-enabled/korpai
# and `nginx -t && systemctl reload nginx`.
```

The widget degrades gracefully — when `/api/chat/*` returns an error or
404, it still shows the greeting and hands off to LINE/FB.

## When to scale

Single `uvicorn` worker is fine until we see:

- sustained >5 req/s on the message endpoint, OR
- p95 response latency > 3s from nginx logs, OR
- chat sessions getting dropped because the process restarted

Next steps if any of those hit:

1. Add Redis (DB 5) + swap `session_store.py` for a Redis-backed impl
2. Run `uvicorn --workers 2` (or gunicorn with uvicorn workers)
3. Optionally front with `nginx` rate-limit zone on `/api/chat/message`

## Cost envelope

Haiku 4.5 ≈ $0.25 / 1M input tokens, $1.25 / 1M output (Apr 2026).
Sonnet 4.6 ≈ $3 / 1M input, $15 / 1M output.

Average chat turn:

- user: ~100 tokens
- history: ~1,500 tokens by turn 5
- system prompt: ~800 tokens
- reply: ~300 tokens out

Worst-case Sonnet turn = ~$0.012. 500 Sonnet-routed turns/month ≈ $6.
Most turns stay on Haiku (~$0.002 each). Budget $20/month is comfortable
for the first few hundred leads.
