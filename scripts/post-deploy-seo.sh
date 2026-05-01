#!/usr/bin/env bash
# post-deploy-seo.sh — call after auto-pull build succeeds
# Pings IndexNow (Bing/Yandex), Google sitemap ping, Wayback archive of newest blog post
#
# Usage: bash scripts/post-deploy-seo.sh [optional-new-post-slug]
# Called automatically by auto-pull.sh after rsync succeeds.

set +e

KEY="78a0f971884cfdbfd5730a0ae7abd17f"
SITE="https://korpai.co"
LOG=/var/log/korpai-seo-pings.log

{
echo ""
echo "=== $(date -Is) post-deploy SEO pings ==="

# 1. Build URL list — sitemap-index + 5 newest blog posts
URLS=("$SITE/" "$SITE/blog" "$SITE/sitemap-index.xml" "$SITE/llms.txt" "$SITE/rss.xml")
# Add 5 newest posts (sorted by file mtime since we don't parse frontmatter)
NEWEST=$(ls -t /var/www/korpai/blog/*.html 2>/dev/null | head -5)
for f in $NEWEST; do
  SLUG=$(basename "$f" .html)
  URLS+=("$SITE/blog/$SLUG")
done

# Optional: include explicit slug from arg
if [ -n "$1" ]; then
  URLS+=("$SITE/blog/$1")
fi

echo "URLs to submit: ${#URLS[@]}"

# 2. IndexNow batch submit (Bing + Yandex)
URL_LIST_JSON=$(printf '%s\n' "${URLS[@]}" | python3 -c "import sys,json; print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))")
PAYLOAD=$(python3 -c "
import json
print(json.dumps({
    'host': 'korpai.co',
    'key': '$KEY',
    'keyLocation': '$SITE/$KEY.txt',
    'urlList': $URL_LIST_JSON
}))
")
INDEXNOW=$(curl -s -X POST -H "Content-Type: application/json" \
  --data "$PAYLOAD" -w "\nHTTP %{http_code}\n" \
  "https://api.indexnow.org/IndexNow")
echo "IndexNow:"
echo "$INDEXNOW"

# 3. Google sitemap ping
curl -s -o /dev/null -w "Google sitemap ping: %{http_code}\n" \
  "https://www.google.com/ping?sitemap=https%3A%2F%2Fkorpai.co%2Fsitemap-index.xml"

# 4. Bing sitemap ping (legacy, IndexNow is primary now)
curl -s -o /dev/null -w "Bing sitemap ping: %{http_code}\n" \
  "https://www.bing.com/ping?sitemap=https%3A%2F%2Fkorpai.co%2Fsitemap-index.xml"

# 5. Wayback Machine — archive newest 3 URLs (rate limit friendly)
for url in "${URLS[@]:0:3}"; do
  CODE=$(curl -s -A "korpai-archive-bot/1.0" -o /dev/null -w "%{http_code}" \
    "https://web.archive.org/save/$url")
  echo "Wayback $CODE  $url"
  sleep 2
done

echo "=== done $(date -Is) ==="
} | tee -a "$LOG"
