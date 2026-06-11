#!/usr/bin/env node
// True-cost calculator: "free" chatbot vs self-host vs platform vs agency (THB/month).
// The hidden costs most SME owners forget: your own hours + Thai token tax (2-3x).
//
//   node true_cost_calculator.js --chats 200 --msgs 6 --hours 3 --wage 400 --model standard
//
// Companion to: https://korpai.co/blog/ai-chatbot-ฟรี-2026-ต้นทุนแฝง-sme
// Interactive version: https://korpai.co/utility/chatbot-true-cost-calculator/
// MIT — KORP AI (korpai.co)

const arg = (k, d) => {
  const i = process.argv.indexOf("--" + k);
  return i > -1 ? process.argv[i + 1] : d;
};
const PER_MSG_THB = { budget: 0.10, standard: 0.35, flagship: 0.90 }; // incl. Thai 2-3x token tax

const chats = +arg("chats", 200), msgs = +arg("msgs", 6);
const hours = +arg("hours", 3), wage = +arg("wage", 400);
const per = PER_MSG_THB[arg("model", "standard")] ?? 0.35;

const tokens = chats * msgs * per;        // LLM cost
const timeFull = hours * 4.33 * wage;     // your time, monthly

const paths = [
  ["FREE tier + DIY", tokens + timeFull, "token + full self-maintenance, no guardrails"],
  ["Self-host (n8n/Dify on VPS)", 350 + tokens + timeFull * 0.7, "VPS 350 THB + token + 70% of your time"],
  ["Paid platform", 1500 + tokens * 0.5 + timeFull * 0.3, "~1,500 THB plan, AI partly subsidized"],
  ["Agency-managed", 3500 + 0.5 * 4.33 * wage, "monthly fee incl. API, ~0.5 h/wk of your time"],
];
const best = Math.min(...paths.map(p => p[1]));
console.log(`\nTrue monthly cost @ ${chats} chats x ${msgs} AI msgs (THB):\n`);
for (const [name, cost, why] of paths)
  console.log(`${cost === best ? "->" : "  "} ${name.padEnd(28)} ${Math.round(cost).toLocaleString().padStart(8)}  (${why})`);
console.log("\nRule: when FREE row > any paid row, 'free' is your most expensive option.\n");
