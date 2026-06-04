// tool-call-stock.js — read-only "get stock" tool for an AI chatbot.
// Principle: the LLM may CALL this tool, but must answer ONLY from what it
// returns — never invent stock/price. Short TTL cache spares the POS API.
const TTL_MS = 60_000;              // 60s: fresh enough, kind to rate limits
const cache = new Map();            // sku -> { at, data }

async function fetchStockFromPOS(sku) {
  // Swap for your POS / Open API (e.g. Loyverse). Return null when unknown.
  const r = await fetch(`${process.env.POS_BASE}/items/${encodeURIComponent(sku)}`, {
    headers: { Authorization: `Bearer ${process.env.POS_TOKEN}` },
  });
  if (!r.ok) return null;
  const j = await r.json();
  return { sku, name: j.name, qty: Number(j.in_stock), price: Number(j.price) };
}

export async function getStock(sku) {
  const hit = cache.get(sku);
  if (hit && Date.now() - hit.at < TTL_MS) return hit.data;
  const data = await fetchStockFromPOS(sku);   // may be null => bot must not guess
  cache.set(sku, { at: Date.now(), data });
  return data;
}

// Tool schema exposed to the model (Claude / GPT / Gemini tool-use):
export const getStockTool = {
  name: 'get_stock',
  description: 'ดึงจำนวนคงเหลือและราคาจริงของสินค้าตาม SKU. ได้ null = ไม่พบ ห้ามเดา ให้ส่งต่อคน',
  input_schema: { type: 'object', properties: { sku: { type: 'string' } }, required: ['sku'] },
};
