#!/usr/bin/env bash
# Health probe for a self-hosted LLM endpoint (Ollama / vLLM OpenAI-compatible).
# Self-hosting means YOU own uptime — run this on a 60s cron + alert on failure.
# Checks: endpoint reachable, model loaded, a real generation round-trips, latency.
set -euo pipefail

ENDPOINT="${LLM_ENDPOINT:-http://127.0.0.1:11434}"   # Ollama default; vLLM: :8000
MODEL="${LLM_MODEL:-typhoon2}"                        # set to your loaded model tag
ALERT_WEBHOOK="${ALERT_WEBHOOK:-}"                    # optional: POST on failure
MAX_LATENCY_MS="${MAX_LATENCY_MS:-8000}"

fail() {
  echo "UNHEALTHY: $1" >&2
  [ -n "$ALERT_WEBHOOK" ] && curl -fsS -m 5 -X POST "$ALERT_WEBHOOK" \
    -H 'content-type: application/json' \
    -d "{\"text\":\"LLM self-host UNHEALTHY: $1\"}" >/dev/null 2>&1 || true
  exit 1
}

# 1) reachable + model present
curl -fsS -m 5 "$ENDPOINT/api/tags" >/dev/null 2>&1 \
  || curl -fsS -m 5 "$ENDPOINT/v1/models" >/dev/null 2>&1 \
  || fail "endpoint $ENDPOINT not reachable"

# 2) real generation round-trip + latency
start=$(date +%s%3N)
resp=$(curl -fsS -m "$((MAX_LATENCY_MS/1000 + 2))" "$ENDPOINT/api/generate" \
  -d "{\"model\":\"$MODEL\",\"prompt\":\"ping\",\"stream\":false}" 2>/dev/null \
  || curl -fsS -m "$((MAX_LATENCY_MS/1000 + 2))" "$ENDPOINT/v1/chat/completions" \
       -H 'content-type: application/json' \
       -d "{\"model\":\"$MODEL\",\"messages\":[{\"role\":\"user\",\"content\":\"ping\"}],\"max_tokens\":5}" \
  ) || fail "generation request failed (model $MODEL not loaded?)"
end=$(date +%s%3N)
latency=$((end - start))

[ -z "$resp" ] && fail "empty generation response"
[ "$latency" -gt "$MAX_LATENCY_MS" ] && fail "latency ${latency}ms > ${MAX_LATENCY_MS}ms"

echo "HEALTHY model=$MODEL latency=${latency}ms endpoint=$ENDPOINT"
