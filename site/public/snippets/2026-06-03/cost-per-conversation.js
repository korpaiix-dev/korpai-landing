// cost-per-conversation.js  (ES module) — KORP AI (https://korpai.co)
// ประเมิน "ต้นทุนต่อ 1 บทสนทนา" ของ AI chatbot แบบรวมทุกส่วน (ไม่ใช่แค่ค่า token)
// เทียบกับต้นทุนต่อบทสนทนาของคน เพื่อดูว่าคุ้มกี่เท่า

/**
 * @param {object} p
 * @param {number} p.monthlyPlatform   ค่าแพลตฟอร์ม/โฮสต์/ดูแล รวมต่อเดือน (บาท)
 * @param {number} p.tokenCostPerConv  ค่า token เฉลี่ยต่อบทสนทนา (บาท) เช่น 0.1..4
 * @param {number} p.conversations     จำนวนบทสนทนาที่บอตจบได้/เดือน
 * @param {number} [p.humanMinutes=4]  นาทีที่คนใช้ต่อบทสนทนา
 * @param {number} [p.humanCostPerHour=250] ค่าแรงคน/ชม. (บาท)
 */
export function costPerConversation(p) {
  const conv = Math.max(p.conversations, 1);
  const fixedPerConv = p.monthlyPlatform / conv;
  const botCost = fixedPerConv + (p.tokenCostPerConv || 0);
  const humanCost = ((p.humanMinutes ?? 4) / 60) * (p.humanCostPerHour ?? 250);
  return {
    botCostPerConversation: +botCost.toFixed(2),
    humanCostPerConversation: +humanCost.toFixed(2),
    cheaperBy: +(humanCost / botCost).toFixed(1) + "x",
    breakdown: {
      fixedPerConv: +fixedPerConv.toFixed(2),
      tokenPerConv: +(p.tokenCostPerConv || 0).toFixed(2),
    },
  };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  console.log(costPerConversation({
    monthlyPlatform: 5500, tokenCostPerConv: 1.0, conversations: 975,
  }));
}
