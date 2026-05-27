/**
 * Parallel loan pre-qualification across 6 Thai banks.
 *
 * Strategy:
 *   - Call all 6 bank sandbox APIs concurrently (Promise.allSettled)
 *   - 8-second per-bank timeout (no single slow bank can block reply)
 *   - Return ranked list, best (lowest effective rate among pre_qualified=true) first
 *
 * Drop into a Node/n8n Code node. Implements the loan pre-qual flow
 * described in: https://korpai.co/blog/ai-chatbot-เต็นท์รถมือสอง-ตัวแทนจำหน่ายรถ-car-dealer-sme-2026
 */

const BANKS = [
  { id: "kbank",    name: "KBank",      endpoint: process.env.KBANK_PREQUAL_URL,    timeoutMs: 8000 },
  { id: "scb",      name: "SCB",        endpoint: process.env.SCB_PREQUAL_URL,      timeoutMs: 8000 },
  { id: "krungsri", name: "Krungsri",   endpoint: process.env.KRUNGSRI_PREQUAL_URL, timeoutMs: 8000 },
  { id: "bay",      name: "Bangkok",    endpoint: process.env.BAY_PREQUAL_URL,      timeoutMs: 8000 },
  { id: "ttb",      name: "TTB",        endpoint: process.env.TTB_PREQUAL_URL,      timeoutMs: 8000 },
  { id: "tbank",    name: "TBank",      endpoint: process.env.TBANK_PREQUAL_URL,    timeoutMs: 8000 },
];

async function callBank(bank, payload) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), bank.timeoutMs);
  try {
    const res = await fetch(bank.endpoint, {
      method: "POST",
      headers: { "content-type": "application/json", "x-dealer-id": process.env.DEALER_ID },
      body: JSON.stringify(payload),
      signal: ctrl.signal,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const body = await res.json();
    return {
      bank: bank.id, name: bank.name,
      pre_qualified: !!body.pre_qualified,
      effective_rate: body.effective_rate ?? null,
      max_term_months: body.max_term_months ?? null,
      monthly_pay_estimate: body.monthly_pay_estimate ?? null,
      raw: body,
    };
  } catch (err) {
    return { bank: bank.id, name: bank.name, pre_qualified: false, error: String(err) };
  } finally {
    clearTimeout(timer);
  }
}

export async function prequalAllBanks(payload) {
  if (!payload.pdpa_consent_version) {
    throw new Error("PDPA consent required before pre-qualification");
  }
  const results = await Promise.all(BANKS.map((b) => callBank(b, payload)));
  const ranked = results
    .filter((r) => r.pre_qualified)
    .sort((a, b) => (a.effective_rate ?? 99) - (b.effective_rate ?? 99));
  return {
    pre_qualified_count: ranked.length,
    best: ranked[0] ?? null,
    all: results,
    summary_th: ranked.length === 0
      ? "ยังไม่ผ่าน pre-qual กับ 6 ธนาคาร — sales จะติดต่อขอข้อมูลเพิ่มเติม"
      : `Pre-qual ผ่าน ${ranked.length} ธนาคาร — แนะนำ ${ranked[0].name} ดอกเบี้ย ${ranked[0].effective_rate}%`,
  };
}
