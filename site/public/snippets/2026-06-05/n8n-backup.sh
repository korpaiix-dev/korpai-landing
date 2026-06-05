#!/usr/bin/env bash
# KORP AI — n8n self-host backup (กฎ 3-2-1) สำหรับ SME ไทย
# สำรอง: PostgreSQL dump + N8N_ENCRYPTION_KEY + docker-compose/.env แล้ว push offsite
# ใช้กับ stack docker-compose ของ KORP AI — ตั้งใน cron: 0 2 * * * /opt/n8n/n8n-backup.sh
set -euo pipefail

STACK_DIR="${STACK_DIR:-/opt/n8n}"          # โฟลเดอร์ที่มี docker-compose.yml + .env
BACKUP_DIR="${BACKUP_DIR:-/opt/n8n/backups}"
RCLONE_REMOTE="${RCLONE_REMOTE:-}"          # เช่น "gdrive:n8n-backups" หรือ "s3:bucket/n8n" (offsite)
RETENTION_DAYS="${RETENTION_DAYS:-14}"
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT="$BACKUP_DIR/n8n-$STAMP"

cd "$STACK_DIR"
# shellcheck disable=SC1091
source .env
mkdir -p "$OUT"

echo "[1/4] dumping PostgreSQL..."
docker compose exec -T postgres \
  pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner \
  | gzip > "$OUT/n8n-db.sql.gz"

echo "[2/4] copying config + encryption key (ห้ามหาย!)..."
cp -a docker-compose.yml Caddyfile .env "$OUT/" 2>/dev/null || true
# คีย์เข้ารหัสอยู่ใน .env แล้ว — แต่ย้ำสำเนาแยกไว้ให้ชัด
grep -E '^N8N_ENCRYPTION_KEY=' .env > "$OUT/ENCRYPTION_KEY.txt" || true

echo "[3/4] packing..."
TARBALL="$BACKUP_DIR/n8n-$STAMP.tar.gz"
tar -C "$BACKUP_DIR" -czf "$TARBALL" "n8n-$STAMP"
rm -rf "$OUT"
sha256sum "$TARBALL" > "$TARBALL.sha256"

echo "[4/4] offsite push + retention..."
if [[ -n "$RCLONE_REMOTE" ]]; then
  rclone copy "$TARBALL" "$RCLONE_REMOTE/" && rclone copy "$TARBALL.sha256" "$RCLONE_REMOTE/"
else
  echo "  (ข้าม offsite: ยังไม่ตั้ง RCLONE_REMOTE — แนะนำตั้งเพื่อให้ครบกฎ 3-2-1)"
fi
find "$BACKUP_DIR" -name 'n8n-*.tar.gz*' -mtime +"$RETENTION_DAYS" -delete

echo "✅ backup done: $TARBALL ($(du -h "$TARBALL" | cut -f1))"
echo "ℹ️  ทดสอบ restore จริงอย่างน้อยเดือนละครั้ง — backup ที่กู้ไม่ได้ = ไม่มี backup"
