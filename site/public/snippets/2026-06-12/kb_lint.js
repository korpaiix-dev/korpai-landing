#!/usr/bin/env node
/**
 * kb_lint.js — lint a FAQ CSV against the "1-1-1 rule" before feeding it to a chatbot.
 *
 * Checks (each row): self-contained answer (no "ดูด้านบน"/"see above"/"ข้อ 3"),
 * price-ish questions must contain digits in the answer, answer length cap,
 * duplicate questions, zero-width/BOM junk, promo rows must have expires_at.
 *
 * Usage: node kb_lint.js faq.csv          (exit 1 if errors → CI-friendly)
 * CSV columns: category,question,answer,synonyms,updated_at,expires_at
 * Companion to: https://korpai.co/blog/knowledge-base-ai-chatbot-เตรียมข้อมูล-sme-ไทย-2026
 * MIT license — KORP AI (korpai.co)
 */
const fs = require("fs");

const DANGLING = ["ดูด้านบน", "ตามตารางด้านบน", "ดังกล่าวข้างต้น", "ดูข้อ ", "see above", "as above"];
const PRICEY = ["ราคา", "กี่บาท", "เท่าไหร่", "เท่าไร", "ค่าส่ง", "ค่าบริการ", "แพงไหม", "price", "cost"];

// minimal CSV parser (handles quoted fields + embedded commas/newlines)
function parseCSV(text) {
  const rows = []; let row = [], cur = "", inQ = false;
  text = text.replace(/^﻿/, "");
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (inQ) {
      if (c === '"' && text[i + 1] === '"') { cur += '"'; i++; }
      else if (c === '"') inQ = false;
      else cur += c;
    } else if (c === '"') inQ = true;
    else if (c === ",") { row.push(cur); cur = ""; }
    else if (c === "\n" || c === "\r") {
      if (c === "\r" && text[i + 1] === "\n") i++;
      row.push(cur); cur = "";
      if (row.some(f => f !== "")) rows.push(row);
      row = [];
    } else cur += c;
  }
  if (cur !== "" || row.length) { row.push(cur); if (row.some(f => f !== "")) rows.push(row); }
  return rows;
}

const file = process.argv[2];
if (!file) { console.error("usage: node kb_lint.js faq.csv"); process.exit(2); }
const rows = parseCSV(fs.readFileSync(file, "utf8"));
const header = rows.shift().map(h => h.trim().toLowerCase());
const col = name => header.indexOf(name);
const [qi, ai, ci, ei] = [col("question"), col("answer"), col("category"), col("expires_at")];
if (qi < 0 || ai < 0) { console.error("CSV must have 'question' and 'answer' columns"); process.exit(2); }

let errors = 0, warns = 0;
const seen = new Map();
const norm = s => (s || "").normalize("NFC").toLowerCase().replace(/[^\wก-๙]+/g, "");
rows.forEach((r, idx) => {
  const line = idx + 2, q = (r[qi] || "").trim(), a = (r[ai] || "").trim();
  const err = m => { console.log(`ERROR line ${line}: ${m}`); errors++; };
  const warn = m => { console.log(`warn  line ${line}: ${m}`); warns++; };
  if (!q || !a) return err("empty question or answer");
  if (/[​‌﻿]/.test(q + a)) warn("zero-width/BOM character — clean before ingest");
  const key = norm(q);
  if (seen.has(key)) err(`duplicate of line ${seen.get(key)}: "${q.slice(0, 40)}"`); else seen.set(key, line);
  DANGLING.forEach(d => { if (a.includes(d)) err(`dangling reference "${d}" — answer must be self-contained (1-1-1 rule)`); });
  if (PRICEY.some(p => q.toLowerCase().includes(p)) && !/\d/.test(a))
    warn(`price-ish question but no digits in answer: "${q.slice(0, 40)}"`);
  if (a.length > 1200) warn(`answer ${a.length} chars — likely multi-topic, split the row`);
  const cat = ci >= 0 ? (r[ci] || "") : "";
  if (/โปร|promotion|ส่วนลด/i.test(cat + q) && ei >= 0 && !(r[ei] || "").trim())
    warn("promo row without expires_at — stale-promo risk");
});
console.log(`\n${rows.length} rows → ${errors} errors, ${warns} warnings`);
process.exit(errors ? 1 : 0);
