-- KORP AI — Aesthetic clinic PDPA before/after photo consent schema
-- 2026-05-29 — MIT
-- Maps to PDPA หมวด 3 ม.26 "ข้อมูลส่วนบุคคลที่อ่อนไหว" (sensitive data — health + body photos)
-- Source: MoPH retention guideline 2024, PDPA Act 2562

CREATE TABLE patient (
  id            BIGSERIAL PRIMARY KEY,
  line_user_id  TEXT UNIQUE NOT NULL,
  cid_hash      TEXT,              -- SHA-256 of citizen ID (do NOT store plaintext)
  display_name  TEXT NOT NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 3-tier consent: (a) internal only, (b) medical record, (c) marketing-allowed
CREATE TYPE consent_scope AS ENUM ('internal_only', 'medical_record', 'marketing_allowed');

CREATE TABLE photo_consent (
  id              BIGSERIAL PRIMARY KEY,
  patient_id      BIGINT NOT NULL REFERENCES patient(id),
  scope           consent_scope NOT NULL,
  signed_at       TIMESTAMPTZ NOT NULL,
  signed_ip       INET NOT NULL,
  signed_userid   TEXT NOT NULL,    -- Line user id at signing time
  signature_b64   TEXT NOT NULL,    -- digital signature from LIFF canvas
  -- Marketing scope requires explicit face-blur condition acknowledged
  face_blur_acknowledged BOOLEAN DEFAULT FALSE,
  revoke_at       TIMESTAMPTZ,      -- patient may revoke
  auto_delete_at  TIMESTAMPTZ NOT NULL  -- = signed_at + interval '2 years' (MoPH)
);

CREATE TABLE clinical_photo (
  id              BIGSERIAL PRIMARY KEY,
  patient_id      BIGINT NOT NULL REFERENCES patient(id),
  consent_id      BIGINT NOT NULL REFERENCES photo_consent(id),
  s3_bucket       TEXT NOT NULL,    -- private bucket only
  s3_key          TEXT NOT NULL,
  kms_key_id      TEXT NOT NULL,    -- AES-256 via KMS (clinic-owned)
  taken_at        TIMESTAMPTZ NOT NULL,
  procedure       TEXT NOT NULL,
  stage           TEXT NOT NULL CHECK (stage IN ('pre', 'd0', 'd1', 'd7', 'd14', 'd30', 'd90', 'd180', 'd365')),
  deleted_at      TIMESTAMPTZ
);

-- Every access (view, download, marketing-export) is logged ม.30
CREATE TABLE photo_access_audit (
  id              BIGSERIAL PRIMARY KEY,
  photo_id        BIGINT NOT NULL REFERENCES clinical_photo(id),
  actor_user_id   TEXT NOT NULL,         -- staff line/email
  actor_role      TEXT NOT NULL CHECK (actor_role IN ('md','nurse','admin','marketing')),
  action          TEXT NOT NULL CHECK (action IN ('view','download','marketing_export','delete')),
  reason          TEXT,                   -- required for marketing_export & download
  occurred_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  source_ip       INET NOT NULL
);

-- Enforce: marketing_export action requires consent.scope = 'marketing_allowed'
-- and face_blur_acknowledged = TRUE. (Application-side guard + this constraint trigger.)
CREATE OR REPLACE FUNCTION enforce_marketing_consent()
RETURNS TRIGGER AS $$
DECLARE
  s consent_scope;
  blur_ack BOOLEAN;
BEGIN
  IF NEW.action = 'marketing_export' THEN
    SELECT pc.scope, pc.face_blur_acknowledged
      INTO s, blur_ack
      FROM clinical_photo cp
      JOIN photo_consent pc ON pc.id = cp.consent_id
     WHERE cp.id = NEW.photo_id;
    IF s != 'marketing_allowed' OR NOT blur_ack THEN
      RAISE EXCEPTION 'PDPA violation: cannot marketing_export photo without consent.scope=marketing_allowed AND face_blur_acknowledged=TRUE';
    END IF;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_enforce_marketing_consent
BEFORE INSERT ON photo_access_audit
FOR EACH ROW EXECUTE FUNCTION enforce_marketing_consent();

-- Daily cron: delete photos where auto_delete_at < now() AND deleted_at IS NULL
-- UPDATE clinical_photo SET deleted_at = now() WHERE id IN (
--   SELECT cp.id FROM clinical_photo cp
--   JOIN photo_consent pc ON pc.id = cp.consent_id
--   WHERE pc.auto_delete_at < now() AND cp.deleted_at IS NULL
-- );
