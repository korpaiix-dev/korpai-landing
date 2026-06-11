// Free-tier LLM fallback router — survive rate limits on a 0-THB stack.
// Order: Gemini free tier -> Groq free tier -> (optional) paid key as last resort.
// Handles 429/503 with per-provider cooldown so one throttled provider
// doesn't take your whole bot down.
//
//   GEMINI_API_KEY=... GROQ_API_KEY=... node free_llm_fallback.js "สวัสดี ร้านเปิดไหม"
//
// NOTE: free tiers have low rate limits and data-use terms you must read before
// sending real customer chats. For production, see the cost math at
// https://korpai.co/blog/ai-chatbot-ฟรี-2026-ต้นทุนแฝง-sme
// MIT — KORP AI (korpai.co)

const COOLDOWN_MS = 60_000;
const state = new Map(); // provider -> retryAt epoch ms

const providers = [
  {
    name: "gemini-free",
    key: () => process.env.GEMINI_API_KEY,
    call: async (key, prompt) => {
      const r = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${key}`,
        { method: "POST", headers: { "content-type": "application/json" },
          body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }] }) });
      if (!r.ok) throw Object.assign(new Error(`gemini ${r.status}`), { status: r.status });
      return (await r.json()).candidates?.[0]?.content?.parts?.[0]?.text ?? "";
    },
  },
  {
    name: "groq-free",
    key: () => process.env.GROQ_API_KEY,
    call: async (key, prompt) => {
      const r = await fetch("https://api.groq.com/openai/v1/chat/completions", {
        method: "POST",
        headers: { "content-type": "application/json", authorization: `Bearer ${key}` },
        body: JSON.stringify({ model: "llama-3.3-70b-versatile",
          messages: [{ role: "user", content: prompt }] }) });
      if (!r.ok) throw Object.assign(new Error(`groq ${r.status}`), { status: r.status });
      return (await r.json()).choices?.[0]?.message?.content ?? "";
    },
  },
];

async function ask(prompt) {
  const errors = [];
  for (const p of providers) {
    const key = p.key();
    if (!key) { errors.push(`${p.name}: no key`); continue; }
    if ((state.get(p.name) ?? 0) > Date.now()) { errors.push(`${p.name}: cooling down`); continue; }
    try {
      return { provider: p.name, text: await p.call(key, prompt) };
    } catch (e) {
      if (e.status === 429 || e.status === 503) state.set(p.name, Date.now() + COOLDOWN_MS);
      errors.push(`${p.name}: ${e.message}`);
    }
  }
  throw new Error("all providers failed -> queue for human. " + errors.join(" | "));
}
if (typeof module !== "undefined") module.exports = { ask };

if (process.argv[1] && process.argv[1].endsWith("free_llm_fallback.js"))
  ask(process.argv.slice(2).join(" ") || "ตอบสั้นๆ: สวัสดี")
    .then(r => console.log(`[${r.provider}]`, r.text))
    .catch(e => { console.error(e.message); process.exit(1); });
