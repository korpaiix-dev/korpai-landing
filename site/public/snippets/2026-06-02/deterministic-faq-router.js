// deterministic-faq-router.js — answer the most common questions for 0 tokens.
// Companion to: /blog/ai-chatbot-ต้นทุน-token-ต่อข้อความ-sme-2026
// MIT licensed.
//
// The cheapest LLM call is the one you never make. Hours/address/phone/price-list
// questions repeat constantly and have a single correct answer — serve them from a
// rule table BEFORE invoking the model. Falls through to the LLM only on a miss.

const SHOP = {
  hours: "เปิดทุกวัน 10:00–20:00 น. ค่ะ",
  address: "ร้านอยู่ที่ 123 ถ.สุขุมวิท กรุงเทพฯ (ติด BTS อโศก) ค่ะ",
  phone: "โทร 02-123-4567 หรือทักไลน์ @korpai ได้เลยค่ะ",
  parking: "มีที่จอดรถฟรีหน้าร้าน 5 คัน และลานจอดข้างร้านค่ะ",
};

// each rule: [regex, answerKey]. Thai-aware, case-insensitive for latin.
const RULES = [
  [/เปิด.*กี่โมง|กี่โมง.*เปิด|เวลาทำการ|เปิดปิด|open.*time|what time/i, "hours"],
  [/ที่อยู่|อยู่ตรงไหน|แผนที่|location|address|ไปยังไง/i, "address"],
  [/เบอร์|โทร|ติดต่อ|phone|call/i, "phone"],
  [/จอดรถ|ที่จอด|parking/i, "parking"],
];

/**
 * @returns {{handled:true, answer:string, source:string} | {handled:false}}
 */
function routeFAQ(message) {
  for (const [re, key] of RULES) {
    if (re.test(message)) return { handled: true, answer: SHOP[key], source: `rule:${key}` };
  }
  return { handled: false };           // caller should fall through to the LLM
}

if (typeof require !== "undefined" && require.main === module) {
  const tests = ["ร้านเปิดกี่โมงคะ", "มีที่จอดรถไหม", "ขอราคาติดตั้งบอทหน่อย"];
  for (const t of tests) {
    const r = routeFAQ(t);
    console.log(r.handled ? `[0-token ${r.source}] ${r.answer}` : `[-> LLM] ${t}`);
  }
}

module.exports = { routeFAQ, RULES, SHOP };
