#!/usr/bin/env bash
# etda-schema-sync.sh — Sync ETDA e-Tax Invoice XML schema every 6 hours.
# If a new version drops, block submit pipeline + page on-call to retest.
# KORP AI · 2026 · MIT
set -euo pipefail
SCHEMA_DIR="${SCHEMA_DIR:-/var/lib/korpai/etda-schema}"
STATE_FILE="${SCHEMA_DIR}/.version"
ETDA_INDEX="${ETDA_INDEX:-https://api.etda.or.th/etax/schema/index.json}"

mkdir -p "$SCHEMA_DIR"
prev=$(cat "$STATE_FILE" 2>/dev/null || echo "none")
curl -fsSL "$ETDA_INDEX" -o "$SCHEMA_DIR/index.json.new"
cur=$(jq -r '.latest.version' "$SCHEMA_DIR/index.json.new")

if [ "$cur" != "$prev" ]; then
  echo "[etda-schema-sync] new version detected: $prev -> $cur"
  # 1) Pull new XSD
  url=$(jq -r '.latest.xsd_url' "$SCHEMA_DIR/index.json.new")
  curl -fsSL "$url" -o "$SCHEMA_DIR/etax-${cur}.xsd"
  # 2) Block submit pipeline (file flag picked up by validator)
  touch "$SCHEMA_DIR/.BLOCKED"
  echo "schema_version_changed $prev -> $cur" > "$SCHEMA_DIR/.BLOCKED"
  # 3) Page on-call (assumes opsgenie/pagerduty webhook in env)
  if [ -n "${ONCALL_WEBHOOK:-}" ]; then
    curl -fsS -X POST "$ONCALL_WEBHOOK" \
      -H 'content-type: application/json' \
      -d "{\"alert\":\"etda-schema-bump\",\"prev\":\"$prev\",\"cur\":\"$cur\"}" || true
  fi
fi

mv "$SCHEMA_DIR/index.json.new" "$SCHEMA_DIR/index.json"
echo "$cur" > "$STATE_FILE"
