// rate-limit-guard.js
// Layer 7 of the KORP AI 8-layer chatbot security stack.
// Token-bucket rate limiter per user + simple abuse heuristics.
// Stops scraping/DoS, slows brute-force injection probing, and caps runaway LLM token spend.

class RateLimiter {
  // capacity = burst allowed; refillPerSec = sustained rate.
  constructor({ capacity = 8, refillPerSec = 0.5 } = {}) {
    this.capacity = capacity;
    this.refillPerSec = refillPerSec;
    this.buckets = new Map(); // userId -> { tokens, last }
  }
  allow(userId, cost = 1) {
    const now = Date.now() / 1000;
    let b = this.buckets.get(userId);
    if (!b) { b = { tokens: this.capacity, last: now }; this.buckets.set(userId, b); }
    b.tokens = Math.min(this.capacity, b.tokens + (now - b.last) * this.refillPerSec);
    b.last = now;
    if (b.tokens >= cost) { b.tokens -= cost; return { ok: true, remaining: Math.floor(b.tokens) }; }
    const waitSec = Math.ceil((cost - b.tokens) / this.refillPerSec);
    return { ok: false, retryAfter: waitSec };
  }
}

// Behavioural abuse score: many blocked-injection hits or repeated cross-user probes = throttle harder.
class AbuseTracker {
  constructor({ window = 300, threshold = 4 } = {}) { this.window = window; this.threshold = threshold; this.hits = new Map(); }
  flag(userId) {
    const now = Date.now() / 1000;
    const arr = (this.hits.get(userId) || []).filter(t => now - t < this.window);
    arr.push(now); this.hits.set(userId, arr);
    return { count: arr.length, throttle: arr.length >= this.threshold };
  }
}

module.exports = { RateLimiter, AbuseTracker };

if (require.main === module) {
  const rl = new RateLimiter({ capacity: 3, refillPerSec: 0.2 });
  for (let i = 0; i < 5; i++) console.log('msg', i + 1, rl.allow('U_test'));
}
