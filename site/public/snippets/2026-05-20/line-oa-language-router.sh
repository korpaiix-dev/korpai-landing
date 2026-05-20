#!/usr/bin/env bash
# line-oa-language-router.sh
# Tiny helper called from n8n Execute Node — detect Thai/EN/中文/日本語 from incoming
# Line OA text, echo a single token: th|en|zh|ja|unknown. Cheap regex first,
# fall back to LLM (Gemini Flash via OpenRouter) only if ambiguous.
#
# Usage: ./line-oa-language-router.sh "ปวดฟันมาก"
# Stdout: th

set -euo pipefail
msg="${1:-}"
if [[ -z "$msg" ]]; then echo "unknown"; exit 0; fi

# Thai (U+0E00–U+0E7F)
if echo "$msg" | grep -Pq '[\x{0E00}-\x{0E7F}]'; then echo "th"; exit 0; fi
# Japanese hiragana/katakana (U+3040–U+30FF)
if echo "$msg" | grep -Pq '[\x{3040}-\x{30FF}]'; then echo "ja"; exit 0; fi
# CJK Unified Ideographs (U+4E00–U+9FFF) — Chinese (no JP-only kana)
if echo "$msg" | grep -Pq '[\x{4E00}-\x{9FFF}]'; then echo "zh"; exit 0; fi
# ASCII heavy → EN
ascii_count=$(echo -n "$msg" | grep -oP '[A-Za-z]' | wc -l || true)
total=$(echo -n "$msg" | wc -m)
if (( total > 0 )) && (( ascii_count * 100 / total > 60 )); then echo "en"; exit 0; fi
echo "unknown"
