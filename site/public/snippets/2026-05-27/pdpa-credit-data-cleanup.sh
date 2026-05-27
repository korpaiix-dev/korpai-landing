#!/usr/bin/env bash
# PDPA credit-data lifecycle cleanup for car-dealer / property chatbot.
#
# What this does:
#   Finds customer records older than 90 days with no closed deal,
#   purges PII columns (income, slip, statement, ID card image),
#   keeps anonymized chat log for analytics.
#
# Why: Thailand PDPA + พ.ร.บ.การประกอบธุรกิจข้อมูลเครดิต — financial
# personal data must be deleted when retention purpose ends.
#
# Run nightly via cron:
#   0 3 * * *  /opt/korpai/cron/pdpa-credit-data-cleanup.sh >> /var/log/pdpa.log 2>&1
set -euo pipefail

DB_HOST="${DB_HOST:-localhost}"
DB_NAME="${DB_NAME:-dealer_chatbot}"
DB_USER="${DB_USER:-postgres}"
DRY_RUN="${DRY_RUN:-0}"

PSQL="psql -h $DB_HOST -U $DB_USER -d $DB_NAME -v ON_ERROR_STOP=1"

echo "[$(date -Iseconds)] PDPA cleanup start (dry_run=$DRY_RUN)"

# 1) Find candidates
CANDIDATES_SQL="
  SELECT COUNT(*) FROM customer_intake
  WHERE deal_closed = FALSE
    AND last_activity_at < NOW() - INTERVAL '90 days'
    AND pii_purged_at IS NULL;
"
count=$($PSQL -t -A -c "$CANDIDATES_SQL")
echo "Candidates to purge: $count"

if [[ "$count" == "0" ]]; then exit 0; fi
if [[ "$DRY_RUN" == "1" ]]; then
  echo "DRY_RUN=1, skipping mutations"
  exit 0
fi

# 2) Purge PII columns (keep chat_log_anon for analytics)
PURGE_SQL="
  BEGIN;
  UPDATE customer_intake
  SET monthly_income      = NULL,
      existing_debt       = NULL,
      employer_name       = NULL,
      payslip_object_key  = NULL,
      statement_object_key= NULL,
      id_card_object_key  = NULL,
      phone               = encode(sha256(phone::bytea), 'hex'),  -- one-way hash
      pii_purged_at       = NOW()
  WHERE deal_closed = FALSE
    AND last_activity_at < NOW() - INTERVAL '90 days'
    AND pii_purged_at IS NULL;
  -- Delete the actual S3 objects via a separate worker reading pii_purged_at IS NOT NULL
  COMMIT;
"
$PSQL -c "$PURGE_SQL"

# 3) Emit audit event
$PSQL -c "INSERT INTO pdpa_audit (event, count, run_at) VALUES ('credit_data_purge_90d', $count, NOW());"

echo "[$(date -Iseconds)] Purged $count records"
