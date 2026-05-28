"""
KORP AI — PDPA Blueprint Vault Access Guardrail (Thai contractor SME).

Wraps every access to a customer blueprint / site-address / ID-card record in
4-layer enforcement:
  1) encrypted at rest (assumed elsewhere — AES-256 via KMS)
  2) RBAC — owner, foreman, subcontractor with project-and-scope binding
  3) audit log (PDPA ม.30 retention 1y)
  4) anomaly alert (off-hours, mass-export, scope mismatch)

Mount this guard in front of any read/download of blueprint files. If denied,
the function returns (False, reason) so the caller can render a Thai error msg
to the user — never expose raw 403 to the chatbot UI.
"""
from __future__ import annotations
import datetime as dt
import logging
from dataclasses import dataclass

log = logging.getLogger("korpai.pdpa.vault")

@dataclass(frozen=True)
class Subject:
    user_id: str
    role: str               # 'owner' | 'foreman' | 'subcontractor' | 'pe' | 'admin'
    assigned_project_ids: tuple[str, ...]
    assigned_scopes:       tuple[str, ...]   # ('electrical',), ('plumbing',), ...

@dataclass(frozen=True)
class Resource:
    project_id: str
    file_kind: str          # 'blueprint_full' | 'blueprint_electrical' | 'site_address' | 'idcard'
    customer_consent_expires_at: dt.datetime | None

SCOPE_BY_FILE = {
    "blueprint_electrical": "electrical",
    "blueprint_plumbing":   "plumbing",
    "blueprint_structural": "structural",
}

def is_offhours(now: dt.datetime) -> bool:
    # Bangkok working hours 08:00 – 19:00, Mon–Sat
    if now.weekday() >= 6: return True
    return now.hour < 8 or now.hour >= 19

def authorize(subject: Subject, resource: Resource, now: dt.datetime | None = None) -> tuple[bool, str]:
    now = now or dt.datetime.now(dt.timezone.utc)

    # 1. consent / retention check
    if resource.customer_consent_expires_at and resource.customer_consent_expires_at < now:
        return False, "PDPA: customer consent expired — file must be hard-deleted per retention policy"

    # 2. role
    if subject.role == "admin":
        log.warning("admin_access", extra={"sub": subject.user_id, "res": resource.file_kind, "proj": resource.project_id})
        return True, "ok-admin"

    if resource.project_id not in subject.assigned_project_ids:
        return False, "PDPA: project scope mismatch"

    if subject.role == "subcontractor":
        required = SCOPE_BY_FILE.get(resource.file_kind)
        if required is None:
            return False, "PDPA: subcontractor cannot access full blueprint or PII"
        if required not in subject.assigned_scopes:
            return False, f"PDPA: subcontractor scope mismatch (needs {required})"

    if subject.role == "foreman" and resource.file_kind == "idcard":
        return False, "PDPA: foreman cannot access customer ID card"

    # 3. anomaly — off-hours access to sensitive file
    if is_offhours(now) and resource.file_kind in {"blueprint_full", "site_address", "idcard"}:
        log.warning("anomaly_offhours", extra={"sub": subject.user_id, "res": resource.file_kind})
        # do NOT block, but require post-hoc review

    return True, "ok"

def access_with_audit(subject: Subject, resource: Resource, audit_writer) -> tuple[bool, str]:
    ok, reason = authorize(subject, resource)
    audit_writer.write({
        "ts": dt.datetime.now(dt.timezone.utc).isoformat(),
        "user_id": subject.user_id, "role": subject.role,
        "project_id": resource.project_id, "file_kind": resource.file_kind,
        "result": "allow" if ok else "deny", "reason": reason,
    })
    return ok, reason
