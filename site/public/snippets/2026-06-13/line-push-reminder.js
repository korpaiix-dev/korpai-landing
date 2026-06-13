// line-push-reminder.js
// ส่งข้อความเตือนนัดผ่าน LINE Messaging API พร้อมปุ่ม ยืนยัน/เลื่อน/ยกเลิก
// ต้องมี LINE_CHANNEL_ACCESS_TOKEN (ตั้งเป็น env, อย่า hardcode)
// Node 18+ (ใช้ global fetch). MIT — KORP AI Automation (https://korpai.co)

async function sendReminder(userId, { name, service, when, bookingId }) {
  const token = process.env.LINE_CHANNEL_ACCESS_TOKEN;
  if (!token) throw new Error('missing LINE_CHANNEL_ACCESS_TOKEN');

  const body = {
    to: userId,
    messages: [{
      type: 'flex',
      altText: `เตือนนัด: ${service} ${when}`,
      contents: {
        type: 'bubble',
        body: {
          type: 'box', layout: 'vertical', spacing: 'sm',
          contents: [
            { type: 'text', text: 'เตือนนัดหมาย', weight: 'bold', size: 'lg' },
            { type: 'text', text: `คุณ${name}`, size: 'sm', color: '#555555' },
            { type: 'text', text: `บริการ: ${service}`, wrap: true },
            { type: 'text', text: `เวลา: ${when}`, wrap: true },
          ],
        },
        footer: {
          type: 'box', layout: 'vertical', spacing: 'sm',
          contents: [
            btn('ยืนยันนัด', `confirm:${bookingId}`, 'primary'),
            btn('ขอเลื่อนนัด', `reschedule:${bookingId}`, 'secondary'),
            btn('ยกเลิกนัด', `cancel:${bookingId}`, 'secondary'),
          ],
        },
      },
    }],
  };

  const res = await fetch('https://api.line.me/v2/bot/message/push', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`LINE push failed: ${res.status} ${await res.text()}`);
  return true;
}

function btn(label, data, style) {
  return { type: 'button', style, height: 'sm',
           action: { type: 'postback', label, data, displayText: label } };
}

export { sendReminder };
