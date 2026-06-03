// csat-logger.js  (ES module) — KORP AI (https://korpai.co)
// เก็บและสรุปคะแนน CSAT จากปุ่มท้ายบทสนทนา (👍/👎 หรือดาว 1-5)
// in-memory store ตัวอย่าง — production ให้เปลี่ยน save() เป็น DB/Sheet/Logflare

export class CSATLogger {
  constructor() { this.entries = []; }

  /** rating: 1..5 (หรือ map 👍=5,👎=1) ; meta: { channel, topic, escalated } */
  log(conversationId, rating, meta = {}) {
    if (rating < 1 || rating > 5) throw new RangeError("rating must be 1..5");
    const entry = { conversationId, rating, ts: Date.now(), ...meta };
    this.entries.push(entry);
    this.save(entry);          // override นี้เพื่อเขียนลง DB จริง
    return entry;
  }

  save(_entry) { /* no-op default; override in production */ }

  summary() {
    const n = this.entries.length;
    if (!n) return { responses: 0 };
    const avg = this.entries.reduce((s, e) => s + e.rating, 0) / n;
    // CSAT% มาตรฐาน = สัดส่วนที่ให้ 4-5 ดาว
    const satisfied = this.entries.filter(e => e.rating >= 4).length;
    return {
      responses: n,
      avgRating: +avg.toFixed(2),
      csatPercent: +(100 * satisfied / n).toFixed(1),
      target: "ตั้งเป้า 80–85%+ สำหรับบทสนทนากับบอต",
    };
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const l = new CSATLogger();
  [5,5,4,5,3,4,5,2,5,4].forEach((r,i)=>l.log("c"+i, r, {channel:"line"}));
  console.log(l.summary());
}
