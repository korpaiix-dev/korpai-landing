// token-cost-calculator.js — estimate LLM chatbot cost per conversation & per month (THB)
// Companion to: /blog/ai-chatbot-ต้นทุน-token-ต่อข้อความ-sme-2026
// MIT licensed. Prices below are illustrative 2026 ballparks — replace with live vendor pricing.

const USD_TO_THB = 35;

// price = USD per 1,000,000 tokens {in, out}
const TIERS = {
  budget:  { in: 0.10, out: 0.40 },  // e.g. Gemini Flash-Lite / GPT-5 Nano class
  mid:     { in: 1.00, out: 5.00 },  // e.g. Claude Haiku / GPT-5 Mini / Gemini Flash class
  premium: { in: 3.00, out: 15.0 },  // e.g. Claude Sonnet / GPT-5.4 / Gemini Pro class
};

/**
 * Cost of ONE llm call (one turn), in THB.
 * Thai text inflates token counts ~2-3x vs English — pass already-inflated counts.
 */
function costPerTurnTHB({ tier = "mid", inputTokens = 2500, outputTokens = 250 } = {}) {
  const p = TIERS[tier];
  if (!p) throw new Error(`unknown tier: ${tier}`);
  const usd = (inputTokens / 1e6) * p.in + (outputTokens / 1e6) * p.out;
  return usd * USD_TO_THB;
}

/**
 * Cost of a full conversation. History grows each turn, so input tokens compound.
 * We model input growth linearly: turn k carries base + (k-1)*historyGrowth tokens.
 */
function costPerConversationTHB({
  tier = "mid", turns = 6, baseInput = 2500, outputTokens = 250, historyGrowth = 400,
} = {}) {
  let thb = 0;
  for (let k = 0; k < turns; k++) {
    thb += costPerTurnTHB({ tier, inputTokens: baseInput + k * historyGrowth, outputTokens });
  }
  return thb;
}

function monthlyTHB({ conversationsPerMonth = 1000, ...opts } = {}) {
  return costPerConversationTHB(opts) * conversationsPerMonth;
}

// --- demo ---
if (typeof require !== "undefined" && require.main === module) {
  for (const tier of ["budget", "mid", "premium"]) {
    const perConv = costPerConversationTHB({ tier });
    console.log(
      `${tier.padEnd(8)} | /conversation ฿${perConv.toFixed(3)} | ` +
      `1k/mo ฿${monthlyTHB({ tier, conversationsPerMonth: 1000 }).toFixed(0)} | ` +
      `5k/mo ฿${monthlyTHB({ tier, conversationsPerMonth: 5000 }).toFixed(0)} | ` +
      `20k/mo ฿${monthlyTHB({ tier, conversationsPerMonth: 20000 }).toFixed(0)}`
    );
  }
}

module.exports = { costPerTurnTHB, costPerConversationTHB, monthlyTHB, TIERS, USD_TO_THB };
