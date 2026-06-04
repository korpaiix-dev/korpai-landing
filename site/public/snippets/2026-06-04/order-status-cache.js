// order-status-cache.js — marketplace order status (Shopee/Lazada/TikTok) with a
// cache + token-bucket rate guard so the bot never trips platform API limits.
const ORDER_TTL_MS = 120_000;      // statuses change slowly; 2 min is safe
const orderCache = new Map();
let tokens = 8, lastRefill = Date.now();
const RATE = { capacity: 8, refillPerSec: 2 };   // burst 8, steady 2/s

function take() {
  const now = Date.now();
  tokens = Math.min(RATE.capacity, tokens + ((now - lastRefill) / 1000) * RATE.refillPerSec);
  lastRefill = now;
  if (tokens < 1) return false;
  tokens -= 1;
  return true;
}

// fetchFn(orderId) => your platform API call returning { orderId, status, tracking? }
export async function getOrderStatus(orderId, fetchFn) {
  const hit = orderCache.get(orderId);
  if (hit && Date.now() - hit.at < ORDER_TTL_MS) return hit.data;
  if (!take()) return hit?.data ?? { orderId, status: 'unknown', note: 'rate-limited, retry shortly' };
  const data = await fetchFn(orderId);
  orderCache.set(orderId, { at: Date.now(), data });
  return data;
}
