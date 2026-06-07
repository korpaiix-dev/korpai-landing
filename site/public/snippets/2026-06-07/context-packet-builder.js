// context-packet-builder.js
// The #1 fix for failed handoffs: hand the agent a full context packet
// so the customer NEVER has to repeat themselves.
// Produces both a structured object and a ready-to-paste internal note.
// KORP AI — https://korpai.co/blog/ai-chatbot-human-handoff-ส่งต่อเจ้าหน้าที่-sme-ไทย-2026

/**
 * @param {object} conv
 * @param {Array<{role:'user'|'bot', text:string, ts:string|number}>} conv.messages full verbatim history
 * @param {object} conv.entities  { name, phone, orderId, product, ... } collected fields
 * @param {string} conv.reason    which trigger fired (e.g. 'customer_requested', 'refund')
 * @param {string[]} conv.botDid  actions the bot already took (avoid duplicate work)
 */
function buildContextPacket(conv) {
  const { messages = [], entities = {}, reason = 'unknown', botDid = [] } = conv;

  const packet = {
    handoff_reason: reason,
    customer: entities,
    bot_already_did: botDid,
    transcript: messages.map((m) => ({
      who: m.role === 'user' ? 'ลูกค้า' : 'บอต',
      text: m.text,
      at: new Date(m.ts).toISOString(),
    })),
    suggested_greeting: greeting(entities, reason),
  };

  // internal note an agent reads in 5 seconds
  const lines = [
    `🔔 ส่งต่อเพราะ: ${reason}`,
    entities.name ? `👤 ${entities.name}` : null,
    entities.phone ? `📞 ${entities.phone}` : null,
    entities.orderId ? `📦 ออเดอร์ #${entities.orderId}` : null,
    botDid.length ? `🤖 บอตทำแล้ว: ${botDid.join(', ')}` : null,
    '— ประวัติแชต —',
    ...messages.map((m) => `${m.role === 'user' ? 'ลูกค้า' : 'บอต'}: ${m.text}`),
  ].filter(Boolean);

  return { packet, note: lines.join('\n') };
}

function greeting(e = {}, reason = '') {
  const name = e.name ? `คุณ${e.name} ` : '';
  if (/refund|คืนเงิน/i.test(reason) && e.orderId)
    return `สวัสดีค่ะ${name}เรื่องคืนเงินออเดอร์ #${e.orderId} เดี๋ยวแอดมินช่วยดูให้นะคะ`;
  return `สวัสดีค่ะ${name}แอดมินรับเรื่องต่อจากนี้เองนะคะ ไม่ต้องเล่าใหม่ค่ะ`;
}

if (require.main === module) {
  const out = buildContextPacket({
    reason: 'refund',
    entities: { name: 'เอ', phone: '08x', orderId: '1234' },
    botDid: ['เช็คสถานะออเดอร์', 'ยืนยันของส่งแล้ว'],
    messages: [
      { role: 'user', text: 'ของยังไม่ถึง ขอคืนเงิน', ts: Date.now() },
      { role: 'bot', text: 'ขอเลขออเดอร์ด้วยค่ะ', ts: Date.now() },
      { role: 'user', text: '1234', ts: Date.now() },
    ],
  });
  console.log(out.note);
}

module.exports = { buildContextPacket };
