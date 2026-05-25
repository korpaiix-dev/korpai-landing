-- audit-log-schema.sql — Immutable audit log for accounting AI chatbot
-- KORP AI · 2026 · MIT
-- Satisfies PDPA s.30 (reproduce on demand) + TFAC CPA audit requirements.

CREATE TABLE IF NOT EXISTS audit_log (
    id BIGSERIAL PRIMARY KEY,
    ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actor TEXT NOT NULL,                -- "bot:claude-sonnet-4.6" / "user:line_uid_xxx" / "staff:cpa_001"
    client_tin VARCHAR(13) NOT NULL,
    action TEXT NOT NULL,               -- "doc.upload" / "doc.read" / "rag.query" / "advisory.answer" / "consent.granted"
    resource_id TEXT,
    resource_hash CHAR(64),             -- sha256 of payload
    pii_present BOOLEAN NOT NULL DEFAULT FALSE,
    purpose TEXT,                       -- PDPA s.24 — declared purpose at access time
    legal_basis TEXT NOT NULL,          -- "consent" / "contract" / "legal_obligation" / "legitimate_interest"
    ip_addr INET,
    user_agent TEXT,
    confidence NUMERIC(4,3),
    flagged BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_audit_client_ts ON audit_log (client_tin, ts DESC);
CREATE INDEX IF NOT EXISTS idx_audit_actor_ts  ON audit_log (actor, ts DESC);
CREATE INDEX IF NOT EXISTS idx_audit_flagged   ON audit_log (flagged) WHERE flagged = TRUE;

-- Append-only enforcement
REVOKE UPDATE, DELETE ON audit_log FROM PUBLIC;
-- Grant insert-only role
DO $$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'bot_service') THEN
    CREATE ROLE bot_service NOLOGIN;
  END IF;
END $$;
GRANT INSERT, SELECT ON audit_log TO bot_service;
GRANT USAGE, SELECT ON SEQUENCE audit_log_id_seq TO bot_service;

-- Daily snapshot to S3 object-lock bucket (cron):
--   pg_dump --table=audit_log --where="ts::date = CURRENT_DATE - 1" \
--     | gzip | aws s3 cp - s3://acc-vault/audit-snapshots/$(date -d 'yesterday' +%F).sql.gz \
--     --object-lock-mode COMPLIANCE \
--     --object-lock-retain-until-date "$(date -d '+7 years' --iso-8601=seconds)Z"
