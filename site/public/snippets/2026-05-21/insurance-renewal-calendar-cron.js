// Insurance renewal 5-step calendar — n8n Function node
// Trigger: cron 08:00 daily
// Input: Google Sheet "policies" with columns: name, line_user_id, plate, insurer, expiry_date
// Output: array of items to push via Line Messaging API

// Author: KORP AI · 2026-05-21
// License: MIT — use freely, attribution appreciated: korpai.co

const DAYS_BEFORE = [45, 30, 15, 7, 1];

function daysBetween(from, to) {
  const ms = to.getTime() - from.getTime();
  return Math.round(ms / 86400000);
}

function buildMessage(policy, daysLeft) {
  const expiry = new Date(policy.expiry_date).toLocaleDateString('th-TH', {
    year: 'numeric', month: 'long', day: 'numeric'
  });
  const urgency = daysLeft <= 1 ? '⚠️ ' : '';
  const tone = daysLeft >= 30
    ? 'ปีนี้อยากต่อแบบเดิม หรืออยากให้พี่หนึ่งเสนอแบบใหม่ที่อาจประหยัดกว่า?'
    : daysLeft >= 7
    ? 'ใกล้ครบรอบแล้ว สะดวกให้พี่หนึ่งโทรกลับช่วงไหนคะ?'
    : 'จะหมดอายุพรุ่งนี้แล้ว ขอเสนอเบี้ยปีนี้ภายใน 2 ชม. นะคะ';

  return {
    to: policy.line_user_id,
    type: 'flex',
    altText: `${urgency}ประกันรถ ${policy.plate} หมดอายุ ${expiry}`,
    flex: {
      type: 'bubble',
      body: {
        type: 'box', layout: 'vertical', contents: [
          { type: 'text', text: `${urgency}แจ้งเตือนกรมธรรม์`, weight: 'bold', size: 'lg' },
          { type: 'text', text: `คุณ${policy.name}`, margin: 'md', size: 'sm' },
          { type: 'text', text: `รถทะเบียน ${policy.plate}`, size: 'sm' },
          { type: 'text', text: `บริษัท ${policy.insurer}`, size: 'sm' },
          { type: 'text', text: `หมดอายุ ${expiry} (อีก ${daysLeft} วัน)`, size: 'sm', color: '#d32f2f' },
          { type: 'text', text: tone, margin: 'md', wrap: true, size: 'sm' }
        ]
      },
      footer: {
        type: 'box', layout: 'horizontal', spacing: 'sm', contents: [
          { type: 'button', style: 'primary', action: { type: 'postback', label: 'ต่อแบบเดิม', data: `renew=keep&p=${policy.plate}` } },
          { type: 'button', style: 'secondary', action: { type: 'postback', label: 'เสนอแบบใหม่', data: `renew=quote&p=${policy.plate}` } }
        ]
      }
    }
  };
}

// Main
const today = new Date(); today.setHours(0,0,0,0);
const out = [];

for (const item of $input.all()) {
  const policy = item.json;
  if (!policy.expiry_date || !policy.line_user_id) continue;
  const expiry = new Date(policy.expiry_date); expiry.setHours(0,0,0,0);
  const daysLeft = daysBetween(today, expiry);

  if (DAYS_BEFORE.includes(daysLeft)) {
    out.push({ json: buildMessage(policy, daysLeft) });
  }
}

return out;
