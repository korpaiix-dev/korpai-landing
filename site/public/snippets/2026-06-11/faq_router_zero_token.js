// Zero-token FAQ router — answer the top repeated questions BEFORE touching the LLM.
// On a free stack this is the single biggest cost saver: 60-80% of Thai SME chats
// are the same 10 questions (hours, price, location, how to order).
//
//   const { route } = require("./faq_router_zero_token");
//   const hit = route(userText);            // -> { answer, rule } | null
//   if (hit) reply(hit.answer); else callLLM(userText);   // LLM only as fallback
//
// Companion to: https://korpai.co/blog/ai-chatbot-ฟรี-2026-ต้นทุนแฝง-sme
// MIT — KORP AI (korpai.co)

const RULES = [
  { rule: "hours",    test: /(เปิด|ปิด)(กี่โมง|เวลา)|เวลาทำการ|opening hours/i,
    answer: "ร้านเปิดทุกวัน 9:00–18:00 น. ครับ/ค่ะ" },
  { rule: "price",    test: /ราคา|กี่บาท|เท่า ?ไหร่|how much/i,
    answer: "ดูราคาทั้งหมดได้ที่เมนู 'ราคา' หรือพิมพ์ชื่อสินค้าที่สนใจได้เลยครับ/ค่ะ" },
  { rule: "location", test: /อยู่ที่ไหน|ที่อยู่|พิกัด|เดินทาง|map|location/i,
    answer: "ร้านอยู่ที่ [ที่อยู่] แผนที่: [ลิงก์ Google Maps]" },
  { rule: "order",    test: /สั่ง(ซื้อ|ยังไง)|วิธีสั่ง|order/i,
    answer: "สั่งได้เลยในแชตนี้ แจ้งสินค้า+จำนวน เดี๋ยวสรุปยอดให้ทันทีครับ/ค่ะ" },
  { rule: "human",    test: /คุยกับ(คน|พนักงาน|แอดมิน)|human|staff/i,
    answer: "เรียกแอดมินให้แล้ว รอสักครู่ครับ/ค่ะ", handoff: true },
];

function normalize(s) {
  return (s || "").normalize("NFC").replace(/[​-‍﻿]/g, "").trim();
}
function route(text) {
  const t = normalize(text);
  if (!t) return null;
  for (const r of RULES) if (r.test.test(t)) return { answer: r.answer, rule: r.rule, handoff: !!r.handoff };
  return null; // fall through to LLM
}
if (typeof module !== "undefined") module.exports = { route, RULES, normalize };

if (process.argv[1] && process.argv[1].endsWith("faq_router_zero_token.js")) {
  for (const q of ["ร้านเปิดกี่โมงครับ", "ขอคุยกับคนหน่อย", "มีโปรอะไรบ้าง"])
    console.log(q, "->", route(q) ?? "(LLM fallback)");
}
