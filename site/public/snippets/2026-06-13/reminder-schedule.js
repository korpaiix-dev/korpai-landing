// reminder-schedule.js
// สร้างตารางเตือนนัด 3 จังหวะ (ทันที / 24 ชม.ก่อน / 2-3 ชม.ก่อน)
// คืน array ของเวลาส่ง เพื่อนำไป enqueue ใน n8n / cron / job queue
// MIT — KORP AI Automation (https://korpai.co)

/**
 * @param {Date|string} appointmentAt - เวลานัด (ISO string หรือ Date)
 * @param {Date|string} bookedAt - เวลาที่ลูกค้าจอง (default = now)
 * @param {number} sameDayHoursBefore - เตือนวันนัดกี่ ชม. ก่อน (default 3)
 */
function buildReminderSchedule(appointmentAt, bookedAt = new Date(), sameDayHoursBefore = 3) {
  const appt = new Date(appointmentAt);
  const booked = new Date(bookedAt);
  const H = 3600 * 1000;

  const reminders = [
    { type: 'confirm',      sendAt: booked,                              cta: ['เพิ่มลงปฏิทิน'] },
    { type: 'day_before',   sendAt: new Date(appt.getTime() - 24 * H),   cta: ['ยืนยัน', 'เลื่อน', 'ยกเลิก'] },
    { type: 'same_day',     sendAt: new Date(appt.getTime() - sameDayHoursBefore * H), cta: ['ดูแผนที่', 'ติดต่อร้าน'] },
  ];

  // ส่งเฉพาะจังหวะที่ยังไม่เลยเวลา (กันส่งย้อนหลังเมื่อจองกระชั้นชิด)
  const now = Date.now();
  return reminders
    .filter(r => r.sendAt.getTime() > now - 60 * 1000)
    .map(r => ({ ...r, sendAt: r.sendAt.toISOString() }));
}

// ตัวอย่าง
console.log(buildReminderSchedule('2026-06-20T10:00:00+07:00', '2026-06-13T09:00:00+07:00'));

export { buildReminderSchedule };
