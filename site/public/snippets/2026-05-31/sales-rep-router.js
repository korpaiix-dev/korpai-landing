// sales-rep-router.js  (ES module)
// Route a wholesale customer to their OWNING sales rep instead of letting the
// bot answer everything. The rep<->customer relationship is a distributor's
// core asset; the bot handles small/repeat work and frees reps for big accounts.
// MIT licensed.

/**
 * @param {Object} customer  { tier, province, accountValue, ownerRepId }
 * @param {Object} reps      { repId: { name, provinces:[], online:bool } }
 * @param {Object} [opt]     { bigAccountTHB: 50000 }
 * @returns {Object} routing decision
 */
export function routeToRep(customer, reps, opt = {}) {
  const bigAccount = opt.bigAccountTHB ?? 50000;

  // 1) explicit account owner always wins
  if (customer.ownerRepId && reps[customer.ownerRepId]) {
    return { mode: "assigned_owner", repId: customer.ownerRepId,
             handoff: true, name: reps[customer.ownerRepId].name };
  }
  // 2) big account or DEALER/AGENT tier -> hand to a human in their province
  const wantsHuman = customer.accountValue >= bigAccount ||
                     ["DEALER", "AGENT"].includes((customer.tier || "").toUpperCase());
  if (wantsHuman) {
    const inProvince = Object.entries(reps)
      .filter(([, r]) => (r.provinces || []).includes(customer.province));
    const online = inProvince.find(([, r]) => r.online) || inProvince[0];
    if (online) return { mode: "territory", repId: online[0], handoff: true, name: online[1].name };
  }
  // 3) otherwise the bot handles it (price/stock/reorder)
  return { mode: "bot_self_serve", handoff: false };
}

// Example:
//   const reps = { r1: { name: "ฝน", provinces: ["ชลบุรี"], online: true } };
//   routeToRep({ tier: "DEALER", province: "ชลบุรี", accountValue: 120000 }, reps);
