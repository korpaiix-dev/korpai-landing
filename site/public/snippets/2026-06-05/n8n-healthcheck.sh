#!/usr/bin/env bash
# KORP AI — ตรวจสุขภาพ n8n self-host: HTTP up? disk/RAM เหลือพอ? แจ้งเตือนผ่าน webhook
# ตั้ง cron ทุก 5 นาที: */5 * * * * /opt/n8n/n8n-healthcheck.sh
set -uo pipefail

URL="${N8N_URL:-https://n8n.yourcompany.com/healthz}"
ALERT_WEBHOOK="${ALERT_WEBHOOK:-}"   # Line Notify / Slack / Discord incoming webhook
DISK_WARN="${DISK_WARN:-85}"         # % ใช้แล้วเกินนี้ = เตือน
MEM_WARN="${MEM_WARN:-90}"

problems=()

code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "$URL" || echo 000)"
[[ "$code" =~ ^2 ]] || problems+=("n8n ไม่ตอบ (HTTP $code) ที่ $URL")

disk=$(df -P / | awk 'NR==2{gsub("%","",$5); print $5}')
(( disk >= DISK_WARN )) && problems+=("ดิสก์ใช้ไปแล้ว ${disk}% (เกิน ${DISK_WARN}%)")

mem=$(free | awk '/Mem:/{printf "%d", $3/$2*100}')
(( mem >= MEM_WARN )) && problems+=("RAM ใช้ไปแล้ว ${mem}% (เกิน ${MEM_WARN}%) — n8n กิน RAM เป็นหลัก")

if (( ${#problems[@]} > 0 )); then
  msg="🚨 n8n health: $(IFS='; '; echo "${problems[*]}")"
  echo "$msg"
  [[ -n "$ALERT_WEBHOOK" ]] && curl -s -X POST -H 'Content-Type: application/json' \
    -d "{\"text\":\"$msg\"}" "$ALERT_WEBHOOK" >/dev/null || true
  exit 1
fi
echo "✅ n8n healthy (HTTP $code, disk ${disk}%, mem ${mem}%)"
