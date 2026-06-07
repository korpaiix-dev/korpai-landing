// frustration-sentiment-trigger.js
// Lightweight heuristic to detect an upset customer BEFORE it boils over.
// Handoff trigger #5 (sentiment). No model call — runs in microseconds.
// Returns a 0..1 score; escalate proactively above `threshold`.
// KORP AI — https://korpai.co/blog/ai-chatbot-human-handoff-ส่งต่อเจ้าหน้าที่-sme-ไทย-2026

const NEGATIVE_TH = [
  'แย่', 'ห่วย', 'โง่', 'ช้า', 'ไม่ได้เรื่อง', 'หงุดหงิด', 'โมโห',
  'เสียเวลา', 'ผิดหวัง', 'ไม่โอเค', 'รับไม่ได้', 'ปิดร้านเถอะ',
];
const NEGATIVE_EN = ['terrible', 'useless', 'stupid', 'awful', 'angry', 'worst', 'ridiculous'];
const STRONG = ['!!!', 'มาก!!', 'เลวร้าย', 'จะฟ้อง', 'จะร้องเรียน'];

function frustrationScore(text) {
  if (!text) return 0;
  const t = String(text);
  const lower = t.toLowerCase();
  let score = 0;

  for (const w of NEGATIVE_TH) if (t.includes(w)) score += 0.25;
  for (const w of NEGATIVE_EN) if (lower.includes(w)) score += 0.25;
  for (const w of STRONG) if (t.includes(w)) score += 0.4;

  // signals of shouting / agitation
  const exclam = (t.match(/!/g) || []).length;
  if (exclam >= 3) score += 0.2;
  const letters = t.replace(/[^a-zA-Z]/g, '');
  if (letters.length >= 4 && letters === letters.toUpperCase()) score += 0.2; // ALL CAPS

  return Math.min(1, score);
}

/** @returns {boolean} should the bot proactively offer a human? */
function shouldEscalateOnSentiment(text, threshold = 0.5) {
  return frustrationScore(text) >= threshold;
}

if (require.main === module) {
  ['ตอบช้ามาก แย่มาก!!!', 'ขอบคุณค่ะ', 'this is the WORST service',
   'รบกวนช่วยเช็คหน่อยครับ'].forEach((m) =>
    console.log(`${frustrationScore(m).toFixed(2)} | ${m}`));
}

module.exports = { frustrationScore, shouldEscalateOnSentiment };
