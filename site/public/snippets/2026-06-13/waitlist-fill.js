// waitlist-fill.js
// เมื่อมีคนยกเลิกนัด → หาคนใน waitlist ที่เหมาะกับ slot ว่างที่สุด
// เปลี่ยนคิวว่างให้กลับมาเป็นรายได้ภายในไม่กี่นาที
// MIT — KORP AI Automation (https://korpai.co)

/**
 * @param {{start:string,end:string,service:string}} openSlot - slot ที่ว่างจากการยกเลิก
 * @param {Array} waitlist - [{userId, service, earliest, latest, joinedAt}]
 * @returns ลูกค้าที่ควรเสนอ slot ให้ (เรียงตามความเหมาะสม)
 */
function pickWaitlistCandidates(openSlot, waitlist) {
  const slotStart = new Date(openSlot.start).getTime();
  const slotEnd = new Date(openSlot.end).getTime();

  return waitlist
    .filter(w => w.service === openSlot.service)               // บริการตรงกัน
    .filter(w => new Date(w.earliest).getTime() <= slotStart)  // เริ่มได้ทัน
    .filter(w => new Date(w.latest).getTime() >= slotEnd)      // ไม่เลยกรอบที่รับได้
    .sort((a, b) => new Date(a.joinedAt) - new Date(b.joinedAt)); // มาก่อนได้ก่อน
}

// ตัวอย่าง
const slot = { start: '2026-06-15T14:00:00+07:00', end: '2026-06-15T15:00:00+07:00', service: 'นวดอโรมา' };
const wl = [
  { userId: 'U1', service: 'นวดอโรมา', earliest: '2026-06-15T10:00:00+07:00', latest: '2026-06-15T18:00:00+07:00', joinedAt: '2026-06-13T08:00:00+07:00' },
  { userId: 'U2', service: 'ทำเล็บ',   earliest: '2026-06-15T09:00:00+07:00', latest: '2026-06-15T20:00:00+07:00', joinedAt: '2026-06-12T08:00:00+07:00' },
];
console.log(pickWaitlistCandidates(slot, wl).map(c => c.userId)); // → ['U1']

export { pickWaitlistCandidates };
