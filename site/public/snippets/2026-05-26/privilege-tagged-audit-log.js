/**
 * privilege-tagged-audit-log.js
 *
 * Append-only audit log writer for a Thai law firm chatbot. Every entry is
 * tagged with a privilege classification so that, when a subpoena/discovery
 * request arrives, the firm can export ONLY discoverable rows and never
 * leak attorney-client privileged material.
 *
 * Tag values follow Thai practice mapping:
 *   - "privileged"     : attorney-client communication (ป.วิ.อ. ม.232)
 *   - "work-product"   : lawyer's mental impressions / strategy
 *   - "discoverable"   : neutral facts, exhibits already filed
 *   - "public"         : court orders, published rulings
 *
 * Author: KORP AI — https://korpai.co
 * License: MIT
 */

const VALID_TAGS = new Set(['privileged', 'work-product', 'discoverable', 'public']);

class PrivilegeAuditLog {
  /**
   * @param {{ append: (row: object) => Promise<void> }} store  append-only sink
   *   (Postgres logical replication, ClickHouse, S3 object-lock, etc.)
   */
  constructor(store) {
    this.store = store;
  }

  async record({
    matterId,
    userId,
    action,            // e.g. "query", "doc_view", "draft_export"
    payloadHash,       // sha256 of the actual content; never log raw content here
    privilegeTag,
    at = new Date(),
  }) {
    if (!matterId || !userId || !action || !payloadHash) {
      throw new Error('audit: missing required field');
    }
    if (!VALID_TAGS.has(privilegeTag)) {
      throw new Error(`audit: invalid privilege tag "${privilegeTag}"`);
    }
    await this.store.append({
      matter_id: matterId,
      user_id: userId,
      action,
      payload_sha256: payloadHash,
      privilege: privilegeTag,
      at: at.toISOString(),
    });
  }

  /** Export rows safe to disclose under subpoena. */
  async exportDiscoverable(rows) {
    return rows.filter(
      (r) => r.privilege === 'discoverable' || r.privilege === 'public'
    );
  }
}

module.exports = { PrivilegeAuditLog, VALID_TAGS };
