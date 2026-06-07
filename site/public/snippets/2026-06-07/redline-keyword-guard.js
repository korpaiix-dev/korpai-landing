// redline-keyword-guard.js
// Handoff trigger #4: topics the bot must NEVER decide on its own ->
// route straight to a human (money, health, legal, complaints).
// Regex-first guard you run before the LLM ever sees the message.
// KORP AI — https://korpai.co/blog/ai-chatbot-human-handoff-ส่งต่อเจ้าหน้าที่-sme-ไทย-2026

const REDLINES = {
  money:     /คืนเงิน|รีฟันด์|refund|เคลม|claim|ค่าเสียหาย|ขอส่วนลดพิเศษ/i,
  health:    /แพ้ยา|ยา.{0,4}แพ้|แพ้.{0,4}ยา|ผลข้างเคียง|อาการแพ้|ฉุกเฉิน|emergency|หายใจไม่ออก|เลือดออก/i,
  legal:     /ฟ้อง|ทนาย|กฎหมาย|สัญญา|ผิดสัญญา|lawsuit|legal/i,
  complaint: /ร้องเรียน|complaint|จะแฉ|รีวิวด่า|เพจดัง|สคบ|พังมาก/i,
};

/**
 * @param {string} text
 * @returns {{redline:boolean, category:string|null}}
 */
function checkRedline(text) {
  if (!text) return { redline: false, category: null };
  for (const [category, re] of Object.entries(REDLINES)) {
    if (re.test(text)) return { redline: true, category };
  }
  return { redline: false, category: null };
}

const ROUTING = {
  money: 'ทีมการเงิน/หัวหน้าทีม',
  health: 'เจ้าหน้าที่/ผู้เชี่ยวชาญ (ห้ามบอตวินิจฉัย)',
  legal: 'ผู้จัดการ',
  complaint: 'หัวหน้าทีม support',
};

if (require.main === module) {
  ['ขอคืนเงินด้วยค่ะ', 'กินยาแล้วแพ้', 'ราคาเท่าไหร่', 'จะร้องเรียน สคบ']
    .forEach((m) => {
      const r = checkRedline(m);
      console.log(`${r.redline ? 'HUMAN -> ' + ROUTING[r.category] : 'bot-ok'} | ${m}`);
    });
}

module.exports = { checkRedline, REDLINES, ROUTING };
