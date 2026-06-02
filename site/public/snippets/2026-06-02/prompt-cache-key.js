// prompt-cache-key.js — build stable prefixes so prompt caching actually hits.
// Companion to: /blog/ai-chatbot-ต้นทุน-token-ต่อข้อความ-sme-2026
// MIT licensed.
//
// Prompt caching (Claude/OpenAI/Gemini, 2026) discounts repeated input tokens 50-90%
// — but ONLY when the cached prefix is byte-identical across calls. The usual mistake
// is to interpolate per-user data (name, date, cart) INTO the system prompt, which
// busts the cache every turn. Fix: keep the big static block first & immutable, and
// push volatile data into a later message.

const crypto = require("crypto");

/**
 * Split a prompt into a stable, cacheable prefix and a volatile suffix.
 * @param {string} systemPrompt   large static instructions + persona + policies
 * @param {string} knowledgeBlock large static retrieved/whitelisted knowledge
 * @param {object} volatile       per-request data (NEVER put this in the prefix)
 */
function buildCacheablePrompt(systemPrompt, knowledgeBlock, volatile = {}) {
  const prefix = `${systemPrompt}\n\n# KNOWLEDGE\n${knowledgeBlock}`.trim();
  const cacheKey = crypto.createHash("sha256").update(prefix).digest("hex").slice(0, 16);
  return {
    cacheKey,                       // identical across calls => cache hit
    blocks: [
      // mark the static prefix as a cache breakpoint (Anthropic-style example)
      { type: "text", text: prefix, cache_control: { type: "ephemeral" } },
      // volatile data lives AFTER the breakpoint, so it never busts the cache
      { type: "text", text: `# REQUEST\n${JSON.stringify(volatile)}` },
    ],
  };
}

if (typeof require !== "undefined" && require.main === module) {
  const a = buildCacheablePrompt("You are KORP AI ...", "ราคา/นโยบาย ...", { user: "A", cart: 2 });
  const b = buildCacheablePrompt("You are KORP AI ...", "ราคา/นโยบาย ...", { user: "B", cart: 9 });
  console.log("same cacheKey (good, prefix is stable):", a.cacheKey === b.cacheKey, a.cacheKey);
}

module.exports = { buildCacheablePrompt };
