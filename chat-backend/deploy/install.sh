#!/usr/bin/env bash
# ==========================================================================
# KORP AI Chat Backend — VPS install / update script
# ==========================================================================
# Idempotent. Run on the VPS as root.
#
#   curl -fsSL https://raw.githubusercontent.com/korpaiix-dev/korpai-landing/main/chat-backend/deploy/install.sh | bash
#   # OR after `git pull` in /root/korpai-landing:
#   bash /root/korpai-landing/chat-backend/deploy/install.sh
#
# What it does (safe to re-run):
#   1. rsync chat-backend/ → /opt/korpai-chat/   (preserves .env)
#   2. python3 -m venv .venv (if missing) and pip install -r requirements.txt
#   3. installs systemd unit korpai-chat.service (if changed)
#   4. installs nginx snippet snippets/korpai-chat.conf
#   5. patches the korpai server block to `include snippets/korpai-chat.conf;`
#   6. nginx -t && reload, systemctl restart korpai-chat
#   7. health check via curl http://127.0.0.1:8100/api/chat/health
# ==========================================================================
set -euo pipefail

REPO_DIR="${REPO_DIR:-/root/korpai-landing}"
APP_DIR="/opt/korpai-chat"
SRC_DIR="$REPO_DIR/chat-backend"
SVC_FILE="/etc/systemd/system/korpai-chat.service"
NGINX_SNIPPET="/etc/nginx/snippets/korpai-chat.conf"
NGINX_SITE="/etc/nginx/sites-enabled/korpai"

red()    { printf '\033[31m%s\033[0m\n' "$*"; }
green()  { printf '\033[32m%s\033[0m\n' "$*"; }
yellow() { printf '\033[33m%s\033[0m\n' "$*"; }

[[ $EUID -eq 0 ]] || { red "Run as root."; exit 1; }
[[ -d "$SRC_DIR" ]] || { red "Source $SRC_DIR not found. Did you git pull?"; exit 1; }

# ── 1. rsync source (preserve .env) ───────────────────────────────────────
yellow "→ syncing $SRC_DIR → $APP_DIR (preserving .env, .venv)"
mkdir -p "$APP_DIR"
rsync -a --delete \
  --exclude '.venv' \
  --exclude '.env' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  "$SRC_DIR/" "$APP_DIR/"

# ── 2. .env scaffold if missing ───────────────────────────────────────────
if [[ ! -f "$APP_DIR/.env" ]]; then
  yellow "→ no .env found — copying .env.example to .env (you MUST edit it)"
  cp "$APP_DIR/.env.example" "$APP_DIR/.env"
  chmod 600 "$APP_DIR/.env"
  red "  ✗ Edit $APP_DIR/.env and set OPENROUTER_API_KEY before continuing."
  red "    Then re-run this script."
  exit 1
fi

# Sanity check: API key was actually filled
if grep -qE 'OPENROUTER_API_KEY=sk-or-v1-xxxx' "$APP_DIR/.env"; then
  red "  ✗ $APP_DIR/.env still has placeholder OPENROUTER_API_KEY. Fill it in first."
  exit 1
fi

# ── 3. venv + pip install ─────────────────────────────────────────────────
if [[ ! -d "$APP_DIR/.venv" ]]; then
  yellow "→ creating venv"
  python3 -m venv "$APP_DIR/.venv"
fi
yellow "→ installing/updating Python deps"
"$APP_DIR/.venv/bin/pip" install --quiet --upgrade pip
"$APP_DIR/.venv/bin/pip" install --quiet -r "$APP_DIR/requirements.txt"

# ── 4. systemd unit ───────────────────────────────────────────────────────
if ! cmp -s "$SRC_DIR/deploy/korpai-chat.service" "$SVC_FILE"; then
  yellow "→ updating systemd unit"
  cp "$SRC_DIR/deploy/korpai-chat.service" "$SVC_FILE"
  systemctl daemon-reload
fi
systemctl enable --now korpai-chat >/dev/null 2>&1 || true

# ── 5. nginx snippet ──────────────────────────────────────────────────────
mkdir -p /etc/nginx/snippets
if ! cmp -s "$SRC_DIR/deploy/nginx-chat.conf" "$NGINX_SNIPPET"; then
  yellow "→ updating nginx snippet"
  cp "$SRC_DIR/deploy/nginx-chat.conf" "$NGINX_SNIPPET"
fi

# ── 6. patch site config to include snippet (idempotent) ──────────────────
if [[ -f "$NGINX_SITE" ]]; then
  if ! grep -q 'include snippets/korpai-chat.conf' "$NGINX_SITE"; then
    yellow "→ patching $NGINX_SITE to include korpai-chat snippet"
    # insert just before the last closing `}` of the HTTPS server block.
    # We assume there is exactly one server block listening on 443.
    awk '
      /listen[[:space:]]+443/ { in_https=1 }
      in_https && /^[[:space:]]*}[[:space:]]*$/ && !done {
        print "    include snippets/korpai-chat.conf;"
        done=1; in_https=0
      }
      { print }
    ' "$NGINX_SITE" > "$NGINX_SITE.new"
    mv "$NGINX_SITE.new" "$NGINX_SITE"
  fi
else
  red "  ✗ $NGINX_SITE not found — add 'include snippets/korpai-chat.conf;' manually"
fi

# ── 7. validate + reload + restart ────────────────────────────────────────
yellow "→ nginx -t"
nginx -t
yellow "→ reloading nginx"
systemctl reload nginx
yellow "→ restarting korpai-chat"
systemctl restart korpai-chat
sleep 2

# ── 8. health check ───────────────────────────────────────────────────────
yellow "→ health check"
if curl -fsS --max-time 5 http://127.0.0.1:8100/api/chat/health >/dev/null; then
  green "✓ backend healthy on 127.0.0.1:8100"
else
  red "✗ health check failed — see: journalctl -u korpai-chat -n 50 --no-pager"
  exit 1
fi

# Public-facing check (through nginx)
if curl -fsS --max-time 5 https://korpai.co/api/chat/health >/dev/null; then
  green "✓ backend reachable through https://korpai.co/api/chat/health"
else
  yellow "⚠ public check failed — DNS / nginx config / firewall may need attention"
fi

green ""
green "=========================================="
green "  KORP AI Chat Backend deployed."
green "  Status:  systemctl status korpai-chat"
green "  Logs:    journalctl -u korpai-chat -f"
green "  Endpoint: https://korpai.co/api/chat/*"
green "=========================================="
