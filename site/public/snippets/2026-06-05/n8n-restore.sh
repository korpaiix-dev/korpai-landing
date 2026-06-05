#!/usr/bin/env bash
# KORP AI — กู้คืน n8n จาก backup tarball ที่สร้างโดย n8n-backup.sh
# ใช้: ./n8n-restore.sh /path/to/n8n-YYYYMMDD-HHMMSS.tar.gz
set -euo pipefail

TARBALL="${1:?ระบุไฟล์ backup: ./n8n-restore.sh <tarball>}"
STACK_DIR="${STACK_DIR:-/opt/n8n}"
TMP="$(mktemp -d)"

echo "[1/4] verify checksum..."
if [[ -f "$TARBALL.sha256" ]]; then sha256sum -c "$TARBALL.sha256"; fi

echo "[2/4] extract..."
tar -xzf "$TARBALL" -C "$TMP"
SRC="$(find "$TMP" -maxdepth 1 -type d -name 'n8n-*' | head -1)"

echo "[3/4] restore config + key..."
cd "$STACK_DIR"
cp -a "$SRC/.env" .env
cp -a "$SRC/docker-compose.yml" "$SRC/Caddyfile" . 2>/dev/null || true
# shellcheck disable=SC1091
source .env
docker compose up -d postgres
sleep 8

echo "[4/4] load DB dump..."
gunzip -c "$SRC/n8n-db.sql.gz" | \
  docker compose exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
docker compose up -d
rm -rf "$TMP"
echo "✅ restore done — ตรวจว่า N8N_ENCRYPTION_KEY ตรงกับตอน backup ไม่งั้น credentials ถอดไม่ได้"
