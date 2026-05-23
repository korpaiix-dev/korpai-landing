#!/usr/bin/env bash
# MFA Thailand travel-advisory monitor for travel agency chatbots.
# Polls a list of MFA / advisory feeds and pings n8n / Line OA when a new
# advisory affecting one of the agency's destination clusters is published.
#
# Wire output to: n8n webhook -> filter bookings by destination -> notify
# affected customers + ops via Line OA.
#
# Source: KORP AI - https://korpai.co/snippets/2026-05-23/mfa-travel-advisory-monitor.sh
# License: MIT

set -euo pipefail

STATE_DIR="${STATE_DIR:-/var/lib/korpai/advisory}"
WEBHOOK_URL="${WEBHOOK_URL:-https://example.com/webhook/advisory}"
FEEDS=(
  # Add the feeds your agency cares about. Replace placeholders with real URLs.
  "https://www.mfa.go.th/feed/news.rss"
  "https://travel.state.gov/_res/rss/TAsTWs.xml"
)

mkdir -p "$STATE_DIR"

for feed in "${FEEDS[@]}"; do
  feed_id=$(echo -n "$feed" | sha1sum | cut -c1-12)
  state_file="$STATE_DIR/$feed_id.last"
  last_seen=""
  [ -f "$state_file" ] && last_seen=$(cat "$state_file")

  # Pull first item title + link (RSS or Atom)
  payload=$(curl -fsSL --max-time 15 "$feed" \
    | tr -d '\n' \
    | grep -oE '<item>.*</item>' \
    | head -c 4000) || continue

  title=$(echo "$payload" | grep -oE '<title>[^<]+</title>' | head -1 \
          | sed -E 's/<\/?title>//g')
  link=$(echo "$payload" | grep -oE '<link>[^<]+</link>' | head -1 \
          | sed -E 's/<\/?link>//g')

  [ -z "$title" ] && continue

  fingerprint=$(echo -n "$title$link" | sha1sum | cut -c1-12)
  if [ "$fingerprint" != "$last_seen" ]; then
    echo "[NEW] $feed: $title"
    curl -fsSL -X POST "$WEBHOOK_URL" \
      -H "Content-Type: application/json" \
      -d "$(printf '{"feed":"%s","title":%s,"link":%s}' \
            "$feed" \
            "$(printf '%s' "$title" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')" \
            "$(printf '%s' "$link"  | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')" )" \
      || echo "webhook delivery failed (not fatal)"
    echo "$fingerprint" > "$state_file"
  fi
done
