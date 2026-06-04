// deterministic-price-guard.js — prices/stock come from the system, never the LLM.
// resolvePrice() is the ONLY source of truth; guardOutput() blocks a draft reply
// if the model slipped in a baht amount that no tool actually returned.
export function resolvePrice(priceTable, sku) {
  const p = priceTable[sku];
  return typeof p === 'number' ? p : null;   // null => bot must say "ขอเช็คให้" + hand off
}

const BAHT = /(\d[\d,]*(?:\.\d+)?)\s*(?:บาท|฿|thb)/gi;

// approvedNumbers = numbers that genuinely came from tool results this turn.
export function guardOutput(draft, approvedNumbers = []) {
  const approved = new Set(approvedNumbers.map((n) => String(n)));
  const found = [...draft.matchAll(BAHT)].map((m) => m[1].replace(/,/g, ''));
  const invented = found.filter((n) => !approved.has(n));
  return { ok: invented.length === 0, invented };  // ok:false => regenerate or escalate
}
