// tool-call-allowlist.js
// Layer 6 of the KORP AI 8-layer chatbot security stack — "least privilege" for AI agents.
// The LLM may REQUEST a tool; this gate decides if it may RUN. Anything not on the allowlist is denied.
// Write/financial actions require verified identity or human approval (never auto-run on bot say-so).
// Maps to OWASP LLM06:2025 (Excessive Agency).

const ALLOWLIST = {
  get_menu:        { mode: 'read',  auth: 'none' },
  get_store_hours: { mode: 'read',  auth: 'none' },
  check_stock:     { mode: 'read',  auth: 'none' },
  get_my_orders:   { mode: 'read',  auth: 'identity' },   // bound to requester (see layer 5)
  create_order:    { mode: 'write', auth: 'identity' },
  cancel_order:    { mode: 'write', auth: 'human' },       // money-affecting -> human approval
  issue_coupon:    { mode: 'write', auth: 'human' },
  update_price:    { mode: 'write', auth: 'forbidden' },   // bot must NEVER do this
};

function authorizeToolCall(name, ctx) {
  const rule = ALLOWLIST[name];
  if (!rule) return { allow: false, reason: 'not_in_allowlist' };
  if (rule.auth === 'forbidden') return { allow: false, reason: 'forbidden_for_bot' };
  if (rule.auth === 'identity' && !ctx.identityVerified) return { allow: false, reason: 'needs_identity' };
  if (rule.auth === 'human') {
    return ctx.humanApproved
      ? { allow: true, reason: 'human_approved' }
      : { allow: false, reason: 'needs_human_approval', escalate: true };
  }
  return { allow: true, reason: 'ok' };
}

// Optional: clamp arguments too (e.g. discount can't exceed policy max even if the LLM asks).
function clampArgs(name, args) {
  if (name === 'create_order' && args.discount_pct != null) {
    args.discount_pct = Math.max(0, Math.min(args.discount_pct, 15)); // hard ceiling
  }
  return args;
}

module.exports = { authorizeToolCall, clampArgs, ALLOWLIST };

if (require.main === module) {
  const ctx = { identityVerified: true, humanApproved: false };
  ['get_menu', 'get_my_orders', 'cancel_order', 'update_price', 'delete_db']
    .forEach(t => console.log(t, '->', authorizeToolCall(t, ctx)));
}
