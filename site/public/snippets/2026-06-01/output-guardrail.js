// output-guardrail.js  (ES module) — KORP AI
// Regex-first guardrail that screens an LLM reply BEFORE it reaches the customer.
// Layer 5 of the 7-layer anti-hallucination stack. Deterministic, no LLM call,
// runs in <1ms so it never adds latency or API cost.
//
// Usage:
//   import { screenReply } from "./output-guardrail.js";
//   const { verdict, reasons, safeReply } = screenReply(reply, { vertical: "clinic" });
//   if (verdict === "BLOCK") routeToHuman();   // never send a risky promise
//
// MIT licensed. Adapt the rule tables to your business.

// Promises a bot must NEVER make on its own (create legal/financial liability).
export const FORBIDDEN_PROMISES = [
  /คืนเงิน(ได้)?ทุกกรณี/, /รับประกัน\s*100\s*%/, /การันตี(ผล)?\s*100\s*%/,
  /ส่งฟรี(ทุก|ไม่มีขั้นต่ำ)/, /ถูกที่สุดใน(ไทย|ตลาด)/,
  /\bguarantee[d]?\s*100\s*%/i, /\bfull\s*refund\s*any\s*reason\b/i,
];

// Claims that are regulated for health/beauty/finance verticals (อย./OIC style).
export const REGULATED_CLAIMS = {
  clinic:  [/หายขาด/, /ปลอดภัย\s*100\s*%/, /ไม่มีผลข้างเคียง/, /เห็นผล(ทันที|ครั้งเดียว)/],
  finance: [/ผลตอบแทน(การันตี|แน่นอน)/, /กำไรชัวร์/, /ไม่มีความเสี่ยง/],
};

// A price must be a real bounded number — not a vague LLM "range guess".
const VAGUE_PRICE = /(ราคา|price).{0,12}(ประมาณ|around|ราว ?ๆ|น่าจะ).{0,12}\d/i;

export function screenReply(reply, opts = {}) {
  const reasons = [];
  for (const re of FORBIDDEN_PROMISES)
    if (re.test(reply)) reasons.push(`forbidden_promise:${re}`);

  for (const re of (REGULATED_CLAIMS[opts.vertical] || []))
    if (re.test(reply)) reasons.push(`regulated_claim:${re}`);

  if (VAGUE_PRICE.test(reply)) reasons.push("vague_price_guess");

  const verdict = reasons.length ? "BLOCK" : "PASS";
  // On BLOCK, substitute a safe deferral instead of leaking a risky line.
  const safeReply = verdict === "BLOCK"
    ? "ขออนุญาตให้ทีมงานยืนยันข้อมูลส่วนนี้ให้แน่ใจก่อนนะคะ เดี๋ยวรีบติดต่อกลับค่ะ 🙏"
    : reply;

  return { verdict, reasons, safeReply };
}

// --- self-test: `node output-guardrail.js` ---
if (import.meta.url === `file://${process.argv[1]}`) {
  const cases = [
    "ราคาน่าจะประมาณ 300-500 บาทค่ะ",
    "ทรีตเมนต์นี้เห็นผลครั้งเดียว การันตี 100%",
    "เมนูชาเขียวมะลิ 35 บาทค่ะ สั่งก่อน 11 โมงแถม 1 แก้ว",
  ];
  for (const c of cases) console.log(screenReply(c, { vertical: "clinic" }));
}
