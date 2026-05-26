/**
 * court-date-reminder.js
 *
 * n8n-compatible (or any Node cron) reminder generator for Thai e-Filing
 * court dates. Emits a list of LINE pushMessage payloads at T-7 / T-3 / T-1
 * for each upcoming hearing. Ship to LINE Messaging API.
 *
 * Input  : array of { matterId, clientLineUserId, hearingType, when }
 *          where `when` is an ISO8601 string in Asia/Bangkok.
 * Output : array of { to, messages } LINE push payloads.
 *
 * Author: KORP AI — https://korpai.co
 * License: MIT
 */
const OFFSET_DAYS = [7, 3, 1];

const HEARING_LABEL = {
  preliminary: 'นัดพร้อม',
  evidence: 'นัดสืบพยาน',
  judgment: 'นัดฟังคำพิพากษา',
  mediation: 'นัดไกล่เกลี่ย',
};

function daysBetween(a, b) {
  return Math.floor((b - a) / (1000 * 60 * 60 * 24));
}

function buildReminders(matters, now = new Date()) {
  const out = [];
  for (const m of matters) {
    const hearing = new Date(m.when);
    const diff = daysBetween(now, hearing);
    if (!OFFSET_DAYS.includes(diff)) continue;

    const label = HEARING_LABEL[m.hearingType] || m.hearingType;
    out.push({
      to: m.clientLineUserId,
      messages: [
        {
          type: 'text',
          text:
            `แจ้งเตือน: ${label} คดี ${m.matterId} ในอีก ${diff} วัน ` +
            `(${hearing.toLocaleString('th-TH', { timeZone: 'Asia/Bangkok' })}).\n` +
            `กรุณายืนยันการมาศาลตอบกลับข้อความนี้ภายใน 24 ชม.`,
        },
      ],
    });
  }
  return out;
}

module.exports = { buildReminders, HEARING_LABEL };
