# KORP AI Chat Backend

FastAPI service that powers the floating chat widget on https://korpai.co

Small, single-process, no database. In-memory sessions (TTL 60 min), simple
per-IP rate limit, OpenRouter for model routing (Haiku for light traffic,
Sonnet when intent is pricing/technical/ready-to-buy).

## Layout

```
chat-backend/
├── main.py              # FastAPI app + routes
├── agent.py             # SYSTEM_PROMPT + intent classifier + handoff marker
├── openrouter.py        # async chat completion client
├── session_store.py     # in-memory session + rate limiter
├── requirements.txt
├── .env.example
└── deploy/
    ├── korpai-chat.service       # systemd unit
    └── nginx-chat.conf           # nginx snippet (proxy /api/chat/ → :8100)
```

## Run locally

```bash
cd chat-backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env → set OPENROUTER_API_KEY
uvicorn main:app --reload --port 8100
```

Smoke test:

```bash
curl -s http://127.0.0.1:8100/api/chat/health | jq
curl -s -X POST http://127.0.0.1:8100/api/chat/session -c cookies.txt | jq
curl -s -X POST http://127.0.0.1:8100/api/chat/message \
  -H 'content-type: application/json' \
  -b cookies.txt \
  -d '{"message":"ร้านกาแฟอยากได้ chatbot LINE"}' | jq
```

## Deploy to VPS

```bash
# 1. Copy files
rsync -a chat-backend/ root@139.59.123.146:/opt/korpai-chat/
ssh root@139.59.123.146 '
  cd /opt/korpai-chat &&
  python3 -m venv .venv &&
  .venv/bin/pip install -r requirements.txt
'

# 2. Secrets (edit on server, never commit)
ssh root@139.59.123.146 'nano /opt/korpai-chat/.env'

# 3. Systemd
scp deploy/korpai-chat.service root@139.59.123.146:/etc/systemd/system/
ssh root@139.59.123.146 '
  systemctl daemon-reload &&
  systemctl enable --now korpai-chat &&
  systemctl status korpai-chat --no-pager
'

# 4. Nginx
scp deploy/nginx-chat.conf root@139.59.123.146:/etc/nginx/snippets/korpai-chat.conf
# Add `include snippets/korpai-chat.conf;` inside the server block of
# /etc/nginx/sites-enabled/korpai (inside the https server block), then
ssh root@139.59.123.146 'nginx -t && systemctl reload nginx'
```

## Environment variables

See `.env.example`. Required: `OPENROUTER_API_KEY`. Everything else has sane
defaults.

## Model routing

`agent.should_use_deep_model` chooses between:

- `OPENROUTER_MODEL_FAST` — default `anthropic/claude-haiku-4.5`
- `OPENROUTER_MODEL_DEEP` — default `anthropic/claude-sonnet-4.6`

Sonnet triggers on:
- intent ∈ {pricing, technical, ready_to_buy}
- OR turn_count ≥ 4 (conversation is substantive)

## Handoff flow

The model is told to emit `[[HANDOFF]]` on its own line when the human is
ready for a real conversation. `agent.extract_handoff` strips that marker
and the response includes `{handoff: true}`, which the widget uses to swap
to the LINE / Facebook buttons.

Clicking a handoff button hits `POST /api/chat/handoff` with
`{channel: "line" | "fb"}`, which:

1. Marks the session as handed off
2. POSTs a summary to `HANDOFF_WEBHOOK_URL` if configured (Slack-compatible)
3. Returns the deep link to open (LINE OA / FB page)

## When to move to Redis

In-memory is fine while we have one uvicorn process. Swap `session_store.py`
for a Redis-backed implementation when any of:

- We need >1 uvicorn worker
- We want sessions to survive restarts
- We go multi-region
