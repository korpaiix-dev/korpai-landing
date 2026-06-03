// chatbot-roi-calculator.js  (ES module)
// คำนวณ ROI ของ AI chatbot สำหรับ SME — KORP AI (https://korpai.co)
// ROI = (ผลประโยชน์/เดือน - ต้นทุนบอต/เดือน) / ต้นทุนบอต/เดือน
// ตัวเลขเป็น "วิธีคิด" ประกอบการตัดสินใจ ไม่ใช่การการันตีผล.

/**
 * @param {object} p
 * @param {number} p.conversationsPerMonth  จำนวนบทสนทนาทั้งหมด/เดือน
 * @param {number} p.containmentRate         อัตราที่บอตจบเอง 0..1 (เช่น 0.65)
 * @param {number} p.minutesPerConvByHuman   นาทีที่คนเคยใช้ตอบ/บทสนทนา
 * @param {number} p.staffCostPerHour        ค่าแรงรวม/ชม. (บาท)
 * @param {number} p.extraRevenuePerMonth    รายได้เพิ่ม (ลีดนอกเวลา/upsell) บาท/เดือน
 * @param {number} p.setupCost               ค่าทำครั้งแรก (บาท) — amortize 12 เดือน
 * @param {number} p.monthlyCare             ค่าดูแลรายเดือน (บาท)
 * @param {number} p.tokenCostPerMonth       ค่า token/API รวม/เดือน (บาท)
 * @param {number} [p.amortizeMonths=12]
 * @returns {object} สรุปผล ROI
 */
export function chatbotROI(p) {
  const a = p.amortizeMonths || 12;
  const contained = p.conversationsPerMonth * p.containmentRate;
  const hoursSaved = (contained * p.minutesPerConvByHuman) / 60;
  const laborSaved = hoursSaved * p.staffCostPerHour;
  const benefit = laborSaved + (p.extraRevenuePerMonth || 0);
  const botCost = p.setupCost / a + p.monthlyCare + (p.tokenCostPerMonth || 0);
  const net = benefit - botCost;
  const roiPct = botCost > 0 ? (net / botCost) * 100 : 0;
  // payback แบบ cash: หาร setupCost ด้วยกระแสเงินสุทธิ/เดือน (ไม่รวม amortization)
  const monthlyCash = benefit - p.monthlyCare - (p.tokenCostPerMonth || 0);
  const payback = monthlyCash > 0 ? p.setupCost / monthlyCash : Infinity;
  return {
    containedConversations: Math.round(contained),
    hoursSaved: +hoursSaved.toFixed(1),
    laborSaved: Math.round(laborSaved),
    benefitPerMonth: Math.round(benefit),
    botCostPerMonth: Math.round(botCost),
    netPerMonth: Math.round(net),
    roiPercent: +roiPct.toFixed(1),
    paybackMonths: isFinite(payback) ? +payback.toFixed(1) : null,
  };
}

// --- demo: รันตรงด้วย `node chatbot-roi-calculator.js` ---
if (import.meta.url === `file://${process.argv[1]}`) {
  console.log(chatbotROI({
    conversationsPerMonth: 1500, containmentRate: 0.65,
    minutesPerConvByHuman: 4, staffCostPerHour: 250,
    extraRevenuePerMonth: 8000, setupCost: 60000,
    monthlyCare: 4000, tokenCostPerMonth: 1500,
  }));
}
