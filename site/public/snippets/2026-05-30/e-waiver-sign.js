/**
 * Build a Thai-PDPA + พรบ.ธุรกรรมอิเล็กทรอนิกส์ ม.9-compliant typed e-signature payload.
 * Bundles signer-provided fields with server context (IP, UA, GPS, timestamp), hashes,
 * and emits a JSON receipt ready for KMS-encrypted vault storage.
 *
 * KORP AI Automation, 2026-05-30. MIT.
 */
const crypto = require('crypto');

function sha256(buf) {
  return crypto.createHash('sha256').update(buf).digest('hex');
}

/**
 * @param {object} input
 *   - waiver_id (string)         waiver document version id
 *   - signer_name (string)       typed name
 *   - signer_id_ref (string)     last 4 of passport/ID (PDPA minimization)
 *   - waiver_text (string)       full text the signer agreed to
 *   - ctx: { ip, ua, geo: {lat,lng}, channel: 'line'|'whatsapp'|'web' }
 */
function buildSignaturePayload(input) {
  const ts = new Date().toISOString();
  const body = {
    waiver_id: input.waiver_id,
    waiver_hash: sha256(input.waiver_text),
    signer_name: input.signer_name,
    signer_id_ref: input.signer_id_ref,
    signed_at: ts,
    ctx: {
      ip: input.ctx.ip,
      ua: input.ctx.ua,
      geo: input.ctx.geo || null,
      channel: input.ctx.channel,
    },
  };
  body.receipt_hash = sha256(JSON.stringify(body));
  return body;
}

if (require.main === module) {
  const out = buildSignaturePayload({
    waiver_id: 'mt-waiver-v3.2',
    signer_name: 'Jean Dupont',
    signer_id_ref: '8421',
    waiver_text: 'I acknowledge the risks of Muay Thai training including head injury, concussion, fractures, and death...',
    ctx: { ip: '49.230.12.4', ua: 'Line/13.18 iOS', geo: { lat: 7.8943, lng: 98.296 }, channel: 'line' },
  });
  console.log(JSON.stringify(out, null, 2));
}

module.exports = { buildSignaturePayload };
