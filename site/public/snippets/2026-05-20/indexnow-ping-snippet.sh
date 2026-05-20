#!/usr/bin/env bash
# indexnow-ping-snippet.sh
# Tiny demo: ping IndexNow with a list of new/updated URLs after deploy.
# Used in production by korpai.co (every commit triggers this via post-deploy-seo.sh).
#
# Usage:
#   INDEXNOW_KEY=78a0f971884cfdbfd5730a0ae7abd17f \
#   HOST=korpai.co \
#   ./indexnow-ping-snippet.sh "https://korpai.co/blog/foo" "https://korpai.co/blog/bar"

set -euo pipefail
KEY="${INDEXNOW_KEY:?missing INDEXNOW_KEY}"
HOST="${HOST:?missing HOST}"
KEY_LOCATION="https://${HOST}/${KEY}.txt"

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <url1> [url2 ...]" >&2
  exit 2
fi

URLS_JSON=$(printf '"%s",' "$@" | sed 's/,$//')
PAYLOAD=$(cat <<EOF
{"host":"${HOST}","key":"${KEY}","keyLocation":"${KEY_LOCATION}","urlList":[${URLS_JSON}]}
EOF
)

curl -fsSL -X POST 'https://api.indexnow.org/IndexNow' \
  -H 'Content-Type: application/json; charset=utf-8' \
  --data "$PAYLOAD"

echo "submitted: $#"
