#!/usr/bin/env bash
# auto-pull.sh — VPS-side auto-deploy for korpai.co landing
# Run every minute via cron. If origin/main has new commits, pull + rebuild + rsync.
# Lock prevents overlapping runs. All output appended to /var/log/korpai-auto-pull.log.

set -euo pipefail

REPO=/root/korpai-landing
SERVE=/var/www/korpai
LOCK=/var/lock/korpai-auto-pull.lock
LOG=/var/log/korpai-auto-pull.log

# Non-blocking lock: if a previous build is still running, just exit
exec 9>"$LOCK"
flock -n 9 || exit 0

cd "$REPO"

BEFORE=$(git rev-parse HEAD)
git fetch origin main --quiet
AFTER=$(git rev-parse origin/main)

# Nothing new — bail quietly
if [ "$BEFORE" = "$AFTER" ]; then
  exit 0
fi

{
  echo
  echo "=== $(date -Is) deploy $BEFORE -> $AFTER ==="

  git reset --hard origin/main

  cd site
  # Skip npm ci if lockfile + node_modules are already in sync (fast path)
  if [ -f package-lock.json ] && [ -d node_modules ]; then
    npm install --prefer-offline --no-audit --silent
  else
    npm ci --silent
  fi

  npm run build --silent

  rsync -a --delete dist/ "$SERVE/"

  echo "=== done $(git rev-parse HEAD) at $(date -Is) ==="
} >> "$LOG" 2>&1

# Post-deploy SEO pings — runs in background, won't block next cron tick
if [ -x "$REPO/scripts/post-deploy-seo.sh" ]; then
  ( bash "$REPO/scripts/post-deploy-seo.sh" >> "$LOG" 2>&1 ) &
fi
