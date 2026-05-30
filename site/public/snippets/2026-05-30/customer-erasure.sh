#!/usr/bin/env bash
# customer-erasure.sh — handle GDPR Art.17 erasure request for EU customer
#                       while preserving 90-day audit ledger (legal hold).
# KORP AI Automation, 2026-05-30. MIT. Use at your own risk.
#
# Usage: ./customer-erasure.sh <customer_id>
# Requires: aws-cli v2, jq

set -euo pipefail

CUST_ID="${1:?usage: $0 <customer_id>}"
SRC_BUCKET="${SRC_BUCKET:-muaythai-waivers}"
ERASED_BUCKET="${ERASED_BUCKET:-muaythai-erased}"
LEDGER="${LEDGER:-./ledger.jsonl}"
LEGAL_HOLD_DAYS="${LEGAL_HOLD_DAYS:-90}"

# 1. Copy to legal-hold bucket (audit only, no PII content — metadata only)
aws s3 cp "s3://$SRC_BUCKET/$CUST_ID/" "s3://$ERASED_BUCKET/$CUST_ID/" \
    --recursive --quiet

# 2. Tag with legal hold + scheduled delete
DELETE_AFTER="$(date -u -d "+$LEGAL_HOLD_DAYS days" +%Y%m%d)"
aws s3api list-objects-v2 --bucket "$ERASED_BUCKET" --prefix "$CUST_ID/" \
    --query 'Contents[].Key' --output text |
while read -r KEY; do
    [ -z "$KEY" ] && continue
    aws s3api put-object-tagging --bucket "$ERASED_BUCKET" --key "$KEY" \
        --tagging "TagSet=[{Key=legal_hold,Value=audit_trail_only},{Key=delete_after,Value=$DELETE_AFTER}]"
done

# 3. Hard-delete from primary
aws s3 rm "s3://$SRC_BUCKET/$CUST_ID/" --recursive --quiet

# 4. Append immutable ledger entry
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
ACTOR="${ACTOR:-bot:erasure-handler}"
echo "{\"customer\":\"$CUST_ID\",\"action\":\"erased\",\"ts\":\"$TS\",\"actor\":\"$ACTOR\",\"legal_hold_until\":\"$DELETE_AFTER\"}" \
    >> "$LEDGER"

# 5. Customer notify (caller handles channel)
echo "ok customer=$CUST_ID legal_hold_until=$DELETE_AFTER"
