/**
 * driver-coord-pdpa-safe.js
 * 1:1 LINE coordination with drivers — avoid LINE Group so customer PII
 * (name, phone, address) does NOT leak to other drivers / staff.
 *
 * Pattern:
 *   - Each driver has its own LINE userId bound to their employee record
 *   - Bot pushes assigned pickups (only that driver's) to them privately
 *   - Driver opens a personal "route map" via tokenized link (8h expiry)
 *   - POD upload is per-order + encrypted at rest with 90-day retention
 *
 * Companion to: https://korpai.co/blog/ai-chatbot-ขนส่ง-โลจิสติกส์-logistics-sme-2026
 * MIT — KORP AI Automation.
 */

const crypto = require('crypto');

const ROUTE_TOKEN_TTL_MS = 8 * 60 * 60 * 1000; // 8h
const POD_RETENTION_DAYS = 90;

function makeRouteToken(driverId, secret) {
  const exp = Date.now() + ROUTE_TOKEN_TTL_MS;
  const payload = `${driverId}.${exp}`;
  const sig = crypto.createHmac('sha256', secret).update(payload).digest('hex');
  return `${Buffer.from(payload).toString('base64url')}.${sig}`;
}

function verifyRouteToken(token, secret) {
  const [b64, sig] = token.split('.');
  if (!b64 || !sig) return null;
  const payload = Buffer.from(b64, 'base64url').toString();
  const expect = crypto.createHmac('sha256', secret).update(payload).digest('hex');
  if (!crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(expect))) return null;
  const [driverId, expStr] = payload.split('.');
  const exp = parseInt(expStr, 10);
  if (Date.now() > exp) return null;
  return { driverId, exp };
}

/**
 * Push pickup list to a specific driver via LINE push API.
 * pickups: [{ id, recipient, phone, address1, postal, scheduled_at }]
 *
 * Notice: phone is masked (last 4 only) in the LINE message itself.
 * Full info is only accessible through the route map link.
 */
async function pushPickupsToDriver({ lineClient, driverLineId, driverId, secret, pickups }) {
  if (!pickups.length) return;
  const token = makeRouteToken(driverId, secret);
  const url = `https://app.korpai.co/route/${token}`;

  const lines = pickups.slice(0, 10).map((p, i) => {
    const masked = (p.phone || '').replace(/.(?=.{4})/g, '*');
    return `${i + 1}. ${p.id} • ***${p.recipient.slice(-2)} • ${masked}`;
  });

  await lineClient.pushMessage(driverLineId, [
    { type: 'text',
      text: `📦 รับงานวันนี้ (${pickups.length} จุด)\n\n${lines.join('\n')}\n\nดูที่อยู่ + map: ${url}\n(ลิงก์ใช้ได้ 8 ชม.)` },
  ]);
}

/**
 * Audit-log every customer-data access by a driver.
 * Required for PDPA accountability principle.
 */
async function logDriverAccess({ db, driverId, orderId, action, ip }) {
  await db.collection('driver_access_log').insertOne({
    driverId, orderId, action, ip, at: new Date(),
  });
}

function podRetentionDate(uploadedAt) {
  const d = new Date(uploadedAt);
  d.setDate(d.getDate() + POD_RETENTION_DAYS);
  return d;
}

module.exports = { makeRouteToken, verifyRouteToken, pushPickupsToDriver,
                   logDriverAccess, podRetentionDate, POD_RETENTION_DAYS };
