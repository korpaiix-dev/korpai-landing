// credit-term-guardrail.js  (ES module)
// Decide whether a B2B credit order may proceed. The bot calls this BEFORE
// confirming. It never hard-rejects rudely; it returns an action the bot can
// phrase nicely (pay-partial / cash / escalate-to-owner).
// MIT licensed.

const fmt = n => Number(n).toLocaleString("th-TH", { maximumFractionDigits: 2 });

/**
 * @param {Object} acct
 *   acct.creditDays      e.g. 30 | 60 | 90
 *   acct.creditLimit     total approved limit (THB)
 *   acct.openInvoices    [{ amount, dueDate(ISO) }]  unpaid invoices
 * @param {number} orderAmount  new order total incl VAT
 * @param {Date}   [now=new Date()]
 */
export function evaluateCreditOrder(acct, orderAmount, now = new Date()) {
  const open = acct.openInvoices || [];
  const outstanding = open.reduce((s, i) => s + i.amount, 0);
  const overdue = open.filter(i => new Date(i.dueDate) < now);
  const overdueAmt = overdue.reduce((s, i) => s + i.amount, 0);
  const available = acct.creditLimit - outstanding;

  if (overdue.length > 0) {
    return { decision: "HOLD", action: "request_payment", overdueAmount: overdueAmt,
      message: `มี invoice ค้างเกินกำหนด ${overdue.length} ใบ รวม ${fmt(overdueAmt)} บาท ` +
               `— ชำระบางส่วนเพื่อปลดวงเงิน หรือสั่งแบบเงินสดได้เลยครับ` };
  }
  if (orderAmount > available) {
    return { decision: "HOLD", action: "escalate_or_cash", available,
      message: `วงเงินคงเหลือ ${fmt(Math.max(available,0))} บาท ไม่พอออเดอร์ ${fmt(orderAmount)} บาท ` +
               `— ขออนุมัติเพิ่มวงเงิน (ส่งต่อเจ้าของ) หรือชำระเงินสดส่วนเกินครับ` };
  }
  return { decision: "APPROVE", action: "proceed",
    creditDays: acct.creditDays, remainingAfter: available - orderAmount };
}

// Example:
//   const acct = { creditDays: 30, creditLimit: 200000, openInvoices: [
//     { amount: 80000, dueDate: "2026-05-01" }, { amount: 40000, dueDate: "2026-06-20" } ] };
//   evaluateCreditOrder(acct, 60000, new Date("2026-05-31")); // -> HOLD (overdue)
