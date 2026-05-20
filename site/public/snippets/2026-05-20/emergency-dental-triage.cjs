// emergency-dental-triage.cjs
// Regex-first guardrail for dental clinic chatbots — escalate to dentist immediately, never diagnose.
// Used in production by KORP AI for 5 Thai dental clinics (Mar–May 2026).
// MIT licensed. Adapt to your CRM / Line OA bot.

// Single keywords that, on their own, are emergencies.
const HARD = [
  // pure Thai
  "บวมหน้า", "หน้าบวม", "บวมขึ้น",
  "หนอง", "มีหนอง",
  "ฟันหลุด", "ฟันหัก", "ฟันแตก",
  "เลือดไม่หยุด", "เลือดออกไม่หยุด",
  // EN
  "swollen face", "facial swelling", "abscess", "pus",
  "knocked out", "broken tooth", "fractured tooth",
  "bleeding won't stop", "uncontrolled bleeding",
];

// Soft signals that must combine with a pain trigger to count.
const PAIN_TRIGGERS = [
  "ปวด", "เจ็บ", "pain", "hurts", "hurting",
];
const SEVERITY = [
  "มาก", "มากๆ", "มาก ๆ", "หนัก", "ทรมาน", "นอนไม่ได้",
  "severe", "extreme", "unbearable", "can't sleep", "cannot sleep",
  "all night", "ทั้งคืน",
];
const FEVER = [
  "ไข้ขึ้น", "มีไข้", "fever", "high fever",
];

function norm(s) { return (s || '').toLowerCase(); }
function any(arr, m) { return arr.some(k => m.includes(k.toLowerCase())); }

/**
 * Decide whether incoming message is a dental emergency.
 * AI must NEVER diagnose; always escalate to human dentist.
 */
function isDentalEmergency(message) {
  if (!message || typeof message !== 'string') return false;
  const m = norm(message);
  if (any(HARD, m)) return true;
  if (any(FEVER, m) && any(PAIN_TRIGGERS, m)) return true;
  if (any(PAIN_TRIGGERS, m) && any(SEVERITY, m)) return true;
  return false;
}

/**
 * Build emergency reply + signal to escalate via n8n / webhook.
 * @returns {{reply: string, escalate: boolean, aiResponseAllowed: boolean}}
 */
function emergencyResponse(lang = 'th', clinicPhone = '02-xxx-xxxx') {
  const replies = {
    th: `🚨 อาการแบบนี้ต้องพบทันตแพทย์ทันทีค่ะ ไม่แนะนำให้รอ
— กรณีฉุกเฉิน: โทร ${clinicPhone} (เปิด 8:00–21:00)
— นอกเวลา: ไป รพ. ที่ใกล้สุด ER ฟัน
หนูจะส่งต่อทีมคลินิกให้โทรกลับใน 5 นาทีนะคะ`,
    en: `🚨 This sounds urgent — please see a dentist immediately.
— Emergency line: ${clinicPhone} (8 AM – 9 PM)
— After hours: nearest hospital ER dental
Our team will call you back within 5 minutes.`,
  };
  return {
    reply: replies[lang] || replies.th,
    escalate: true,
    aiResponseAllowed: false,
  };
}

function handle(userMessage, lang = 'th') {
  if (isDentalEmergency(userMessage)) return emergencyResponse(lang);
  return { reply: null, escalate: false, aiResponseAllowed: true };
}

module.exports = { isDentalEmergency, emergencyResponse, handle };

// --- CLI smoke test ---
if (require.main === module) {
  const tests = [
    "ปวดฟันมาก ๆ นอนไม่ได้",   // → emergency (pain + severity)
    "อยากจองขูดหินปูน",          // → not emergency
    "swollen face since yesterday", // → emergency (HARD)
    "How much for whitening?",   // → not emergency
    "ปวดฟันนิดหน่อย",            // → not emergency (no severity)
    "ฟันหลุดเพราะอุบัติเหตุ",   // → emergency (HARD)
    "tooth pain so bad I can't sleep", // → emergency (pain + severity)
  ];
  for (const t of tests) {
    const out = handle(t);
    console.log(JSON.stringify({
      msg: t,
      emergency: out.escalate,
    }, null, 0));
  }
}
