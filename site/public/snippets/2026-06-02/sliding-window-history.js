// sliding-window-history.js — keep conversation history within a token budget.
// Companion to: /blog/ai-chatbot-ต้นทุน-token-ต่อข้อความ-sme-2026
// MIT licensed. Trims oldest turns first; optionally keeps a running summary turn.
//
// History is usually the #1 silent cost driver: every turn re-sends the whole
// transcript as input tokens. Cap it.

const roughTokens = (s) => {
  // ~1 token per Thai char, ~4 chars/token otherwise (quick heuristic).
  let th = 0, other = 0;
  for (const ch of s) (/[฀-๿]/.test(ch) ? th++ : other++);
  return Math.ceil(th / 1.6 + other / 4);
};

/**
 * @param {Array<{role:string, content:string}>} messages  full transcript (oldest first)
 * @param {object} opts
 * @param {number} opts.maxTokens   token budget for history (excl. system prompt)
 * @param {number} opts.keepLast    always keep at least this many most-recent messages
 * @param {{role:string,content:string}|null} opts.summary  optional summary of dropped turns
 * @returns {Array} trimmed messages that fit the budget
 */
function trimHistory(messages, { maxTokens = 1500, keepLast = 4, summary = null } = {}) {
  const kept = [];
  let total = 0;
  // walk newest -> oldest, accumulate until budget hit (but always keep `keepLast`)
  for (let i = messages.length - 1; i >= 0; i--) {
    const t = roughTokens(messages[i].content);
    const mustKeep = messages.length - 1 - i < keepLast;
    if (!mustKeep && total + t > maxTokens) break;
    kept.push(messages[i]);
    total += t;
  }
  kept.reverse();
  if (summary && kept.length < messages.length) kept.unshift(summary);
  return kept;
}

if (typeof require !== "undefined" && require.main === module) {
  const convo = Array.from({ length: 20 }, (_, i) => ({
    role: i % 2 ? "assistant" : "user",
    content: `ข้อความรอบที่ ${i + 1} เกี่ยวกับการสั่งซื้อสินค้าและสอบถามราคาส่ง`,
  }));
  const trimmed = trimHistory(convo, { maxTokens: 300, keepLast: 4 });
  console.log(`kept ${trimmed.length}/${convo.length} messages within budget`);
}

module.exports = { trimHistory, roughTokens };
