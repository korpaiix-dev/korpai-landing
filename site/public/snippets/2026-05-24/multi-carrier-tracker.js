/**
 * multi-carrier-tracker.js
 * Aggregate parcel tracking across 5 Thai carriers (Flash, J&T, Kerry, SCG, ThaiPost)
 * in a single API call. Returns the first carrier that recognizes the tracking number.
 *
 * Usage:
 *   const r = await trackAcross('TH123456789');
 *   // [{ carrier: 'flash', ok: true, data: { status: 'in_transit', ... } }, ...]
 *
 * Released by KORP AI Automation (https://korpai.co) under MIT.
 * Companion to: https://korpai.co/blog/ai-chatbot-ขนส่ง-โลจิสติกส์-logistics-sme-2026
 */

const CARRIERS = [
  { name: 'flash',    base: 'https://open-api.flashexpress.com/open',
    path: '/v3/orders/{TN}/routes', auth: 'apiKey' },
  { name: 'jt',       base: 'https://openapi.jtexpress.co.th/webopenplatformapi',
    path: '/api/order/getLogistics', auth: 'sign' },
  { name: 'kerry',    base: 'https://kerryexpress.com/api/v2',
    path: '/track/{TN}', auth: 'bearer' },
  { name: 'scg',      base: 'https://api.scgexpress.co.th/v1',
    path: '/tracking/{TN}', auth: 'bearer' },
  { name: 'thaipost', base: 'https://trackapi.thailandpost.co.th/post/api/v1',
    path: '/track', auth: 'bearer' },
];

const CACHE_TTL_MS = 60 * 1000; // 60s — pickup/in-transit doesn't update faster than this
const cache = new Map();

function fromCache(key) {
  const hit = cache.get(key);
  if (!hit) return null;
  if (Date.now() - hit.at > CACHE_TTL_MS) { cache.delete(key); return null; }
  return hit.value;
}

function toCache(key, value) { cache.set(key, { at: Date.now(), value }); }

async function callCarrier(carrier, trackingNo, keys) {
  const url = carrier.base + carrier.path.replace('{TN}', encodeURIComponent(trackingNo));
  const headers = { 'Accept': 'application/json' };
  if (carrier.auth === 'apiKey')  headers['X-Api-Key']      = keys[carrier.name];
  if (carrier.auth === 'bearer')  headers['Authorization'] = `Bearer ${keys[carrier.name]}`;

  // ThaiPost POSTs with body; others GET
  const opts = carrier.name === 'thaipost'
    ? { method: 'POST', headers: { ...headers, 'Content-Type': 'application/json' },
        body: JSON.stringify({ barcode: [trackingNo] }) }
    : { method: 'GET', headers };

  const ctl = new AbortController();
  const t = setTimeout(() => ctl.abort(), 4500);
  try {
    const res = await fetch(url, { ...opts, signal: ctl.signal });
    if (!res.ok) return { ok: false, status: res.status };
    const data = await res.json();
    return { ok: true, data, found: looksFound(carrier.name, data) };
  } catch (e) {
    return { ok: false, error: e.message };
  } finally {
    clearTimeout(t);
  }
}

// Each carrier shapes its "found" differently; normalize here.
function looksFound(name, data) {
  if (!data) return false;
  if (name === 'flash')    return Array.isArray(data?.data?.routes) && data.data.routes.length > 0;
  if (name === 'jt')       return data?.code === '1' && Array.isArray(data?.data) && data.data.length > 0;
  if (name === 'kerry')    return data?.success === true && data?.shipment;
  if (name === 'scg')      return data?.status && data?.status !== 'NOT_FOUND';
  if (name === 'thaipost') return Array.isArray(data?.response?.items) && data.response.items.length > 0;
  return false;
}

/**
 * Track a parcel across all carriers. Returns array of { carrier, ok, data, found } —
 * caller should pick the first .found one (or show "not found" if none).
 */
async function trackAcross(trackingNo, keys = {}) {
  if (!trackingNo || trackingNo.length < 6) throw new Error('tracking number too short');
  const cached = fromCache(trackingNo);
  if (cached) return cached;

  const results = await Promise.allSettled(
    CARRIERS.map(c => callCarrier(c, trackingNo, keys))
  );
  const normalized = results.map((r, i) => ({
    carrier: CARRIERS[i].name,
    ok:    r.status === 'fulfilled' && r.value.ok,
    found: r.status === 'fulfilled' && r.value.found,
    data:  r.status === 'fulfilled' ? r.value.data : null,
    error: r.status === 'rejected' ? r.reason?.message : (r.value?.error || null),
  }));
  toCache(trackingNo, normalized);
  return normalized;
}

// Returns just the carrier that recognized the tracking number (or null)
function bestMatch(results) {
  return results.find(r => r.found) || null;
}

module.exports = { trackAcross, bestMatch, CARRIERS };
