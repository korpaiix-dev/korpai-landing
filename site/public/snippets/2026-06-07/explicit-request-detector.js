// explicit-request-detector.js
// Detect when a customer explicitly asks for a human agent (Thai + English).
// Handoff trigger #1 — the one you must never miss. Regex-first, zero LLM cost.
// KORP AI — https://korpai.co/blog/ai-chatbot-human-handoff-ส่งต่อเจ้าหน้าที่-sme-ไทย-2026

const HUMAN_REQUEST_PATTERNS = [
  // Thai
  /คุยกับ(คน|เจ้าหน้าที่|แอดมิน|พนักงาน)/i,
  /(ขอ|อยาก|ต้องการ).*(คน|เจ้าหน้าที่|แอดมิน)/i,
  /แอดมินอยู่ไหม/i,
  /มีคนไหม/i,
  /ติดต่อเจ้าหน้าที่/i,
  /ไม่อยากคุยกับบอท/i,
  // English
  /\b(real|live|human)\s+(person|agent|admin|operator)\b/i,
  /\btalk\s+to\s+(a\s+)?(human|agent|someone|person)\b/i,
  /\bspeak\s+to\s+(a\s+)?(human|agent|representative)\b/i,
  /\bcustomer\s+(service|support)\s+agent\b/i,
];

/**
 * @param {string} text raw customer message
 * @returns {boolean} true if the customer is explicitly asking for a human
 */
function wantsHuman(text) {
  if (!text) return false;
  const t = String(text).trim();
  return HUMAN_REQUEST_PATTERNS.some((re) => re.test(t));
}

// --- demo ---
if (require.main === module) {
  ['ขอคุยกับเจ้าหน้าที่หน่อยค่ะ', 'แอดมินอยู่ไหมคะ', 'ราคาเท่าไหร่',
   'I want to talk to a human', 'do you have stock?'].forEach((m) =>
    console.log(`${wantsHuman(m) ? 'HANDOFF' : 'bot-ok '} | ${m}`)
  );
}

module.exports = { wantsHuman, HUMAN_REQUEST_PATTERNS };
