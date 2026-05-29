// KORP AI — อย./MoPH cosmetic procedure ad-claim guardrail (regex-first, LLM-never)
// 2026-05-29 — Public domain (MIT)
// Use: filter every chatbot response BEFORE sending to user in Thai aesthetic-clinic chatbots.
// Reference: ประกาศ อย. การโฆษณาสถานพยาบาล พ.ศ. 2563 + พรบ.สถานพยาบาล ม.38
//
// Strategy:
//   1. Hard-block 142 forbidden tokens/phrases (Thai + English)
//   2. If blocked → DO NOT send to LLM rewrite; return template fallback
//   3. Log every block to audit table (clinic legal/MD weekly review)

const FORBIDDEN_PATTERNS = [
  // Absolute guarantees
  /รับประกันผล/i,
  /รับประกัน\s*100/i,
  /ปลอดภัย\s*100\s*%/i,
  /ไม่มีผลข้างเคียง/i,
  /ไม่มี\s*side\s*effect/i,
  /no\s+side\s+effects?/i,
  /guarantee(d)?\s+result/i,
  // Superlatives forbidden by MoPH
  /ดีที่สุด(ในโลก|ในไทย|ในเอเชีย)?/i,
  /อันดับ\s*1/i,
  /best\s+(in|of)\s+the\s+world/i,
  /หมอ.{0,10}เก่งที่สุด|แพทย์.{0,10}เก่งที่สุด/i,
  /แพทย์ผู้เชี่ยวชาญ(ที่สุด|อันดับหนึ่ง)/i,
  /world['']?s\s+leading/i,
  // % loss / kg loss claims
  /ลด\s*\d+\s*%.{0,40}(รับประกัน|แน่นอน)/i,
  /ลด\s*\d+\s*(กิโล|kg).{0,40}(สัปดาห์|เดือน)/i,
  /lose\s+\d+\s*(kg|kilo).{0,40}(week|month)/i,
  // Before/After explicit claim
  /before\s*[\/\-\s]*after.{0,30}(garantee|รับประกัน|แน่นอน|100)/i,
  /ภาพ.{0,20}จริง.{0,20}ไม่ได้แต่ง/i,
  // FDA-forbidden device claims
  /เครื่อง.{0,15}อันดับ\s*1/i,
  /technology.{0,15}only\s+(in|at)/i,
  // Medical guarantees that breach พรบ.สถานพยาบาล ม.38
  /หาย(ขาด)?\s*100\s*%/i,
  /(cure|fix)\s+(100|completely)/i,
  // Treatment timing absolutes
  /เห็นผลทันที.{0,15}100/i,
  /immediate\s+result.{0,15}guarantee/i,
  // Forbidden promotional pressure
  /โปรโมชั่นวันสุดท้าย.{0,30}ราคาถูกที่สุด/i,
  /last\s+day.{0,30}cheapest/i,
];

// (List trimmed to ~30 for brevity — full prod list has 142, sourced from อย. notice + 5 MoPH PDFs.
//  Boss can request the full list from KORP AI.)

const TEMPLATE_FALLBACK =
  "ขออภัยค่ะ ในเรื่องนี้ทีมเราขอให้แพทย์/admin ตอบคุณโดยตรงเพื่อความถูกต้องนะคะ 🙏 " +
  "ทีมจะตอบกลับภายใน 30 นาที (เวลาเปิด 10:00-20:00) — หรือพิมพ์ 'หมอ' เพื่อ escalate ทันที.";

/**
 * Filter LLM-generated text before sending to user. Returns either the original text
 * (if clean) or the template fallback (if any forbidden pattern matches).
 *
 * @param {string} llmText - the candidate response from LLM
 * @param {function} auditLog - callback(conversation_id, pattern_idx, text) for review queue
 * @param {string} conversationId
 * @returns {{ ok: boolean, text: string, blocked_pattern?: number }}
 */
function adClaimGuardrail(llmText, auditLog, conversationId) {
  for (let i = 0; i < FORBIDDEN_PATTERNS.length; i++) {
    if (FORBIDDEN_PATTERNS[i].test(llmText)) {
      auditLog?.(conversationId, i, llmText);
      return { ok: false, text: TEMPLATE_FALLBACK, blocked_pattern: i };
    }
  }
  return { ok: true, text: llmText };
}

// Quick self-test
// Self-test (run with: node --input-type=commonjs aesthetic-ad-claim-guardrail.js)
const SELF_TEST = (typeof process !== "undefined" && process.argv && process.argv[1] && process.argv[1].endsWith("aesthetic-ad-claim-guardrail.js"));
if (SELF_TEST) {
  const tests = [
    ["filler ของเรารับประกันผล 100%", false],
    ["ลด 5 กิโลใน 1 สัปดาห์", false],
    ["หมอของเราเก่งที่สุดในไทย", false],
    ["หัตถการนี้ใช้เวลา 30 นาที downtime 1-2 วัน", true],
    ["ราคาเริ่มต้น 8,000 บาท สอบถามได้ทักคุยหมอ", true],
  ];
  let pass = 0;
  for (const [text, expectOk] of tests) {
    const r = adClaimGuardrail(text, null, "test");
    if (r.ok === expectOk) { pass++; console.log("PASS", text); }
    else console.log("FAIL", text, "got ok=", r.ok);
  }
  console.log(`${pass}/${tests.length} passed`);
}

export { adClaimGuardrail, FORBIDDEN_PATTERNS, TEMPLATE_FALLBACK };
