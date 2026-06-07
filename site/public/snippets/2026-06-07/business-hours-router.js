// business-hours-router.js
// Handle handoff OUTSIDE working hours the right way: tell the customer a clear
// callback time and queue the conversation instead of going silent.
// Asia/Bangkok aware, no external deps. Node 18+.
// KORP AI — https://korpai.co/blog/ai-chatbot-human-handoff-ส่งต่อเจ้าหน้าที่-sme-ไทย-2026

const TZ = 'Asia/Bangkok';

function bangkokNow(date = new Date()) {
  // formatToParts is locale-stable, unlike string-splitting toLocaleString output
  const parts = new Intl.DateTimeFormat('en-US', {
    timeZone: TZ, weekday: 'short', hour: '2-digit', minute: '2-digit', hour12: false,
  }).formatToParts(date);
  const get = (t) => parts.find((p) => p.type === t)?.value;
  let hour = parseInt(get('hour'), 10);
  if (hour === 24) hour = 0; // some runtimes emit "24" for midnight
  return { weekday: get('weekday'), hour, minute: parseInt(get('minute'), 10) };
}

/**
 * @param {object} hours { open:9, close:18, days:['Mon'..'Sat'] }
 * @returns {{open:boolean, message:string}}
 */
function routeByHours(hours = { open: 9, close: 18, days: ['Mon','Tue','Wed','Thu','Fri','Sat'] }, now = new Date()) {
  const { weekday, hour } = bangkokNow(now);
  const isWorkday = hours.days.includes(weekday);
  const open = isWorkday && hour >= hours.open && hour < hours.close;

  if (open) {
    return { open: true, message: 'กำลังโอนสายให้เจ้าหน้าที่นะคะ รอสักครู่ค่ะ 🙏' };
  }
  return {
    open: false,
    message: `ตอนนี้นอกเวลาทำการค่ะ (เปิด ${hours.open}:00–${hours.close}:00) ` +
      `ทีมงานจะติดต่อกลับในเวลาทำการถัดไปนะคะ ` +
      `รบกวนฝากเบอร์ + ช่วงเวลาที่สะดวก เดี๋ยวเก็บเรื่องไว้ให้เรียบร้อยค่ะ 📝`,
  };
}

if (require.main === module) {
  console.log(bangkokNow(new Date('2026-06-07T02:00:00+07:00')));
  console.log('Sun 02:00 ->', routeByHours(undefined, new Date('2026-06-07T02:00:00+07:00')).open);
  console.log('Mon 10:00 ->', routeByHours(undefined, new Date('2026-06-08T10:00:00+07:00')).open);
}

module.exports = { routeByHours, bangkokNow };
