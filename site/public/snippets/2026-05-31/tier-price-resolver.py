"""Resolve the correct wholesale price for a customer TIER + quantity ladder.

CRITICAL: an LLM must NEVER invent prices. The chatbot calls this deterministic
resolver and only lets the LLM phrase the answer. Quoting the wrong tier is the
quietest way a distributor loses a dealer to a competitor.

Price table shape (per SKU):
    {
      "RETAIL":   [(1, 25.0)],
      "WHOLESALE":[(1, 21.0), (24, 19.5), (240, 18.0)],   # (min_qty, unit_price)
      "DEALER":   [(24, 18.5), (240, 16.9), (1200, 15.5)],
      "AGENT":    [(240, 15.0), (1200, 14.0)],
    }
MIT licensed.
"""
from bisect import bisect_right

VALID_TIERS = ("RETAIL", "WHOLESALE", "DEALER", "AGENT")

def resolve_price(price_table: dict, tier: str, qty: int) -> dict:
    tier = (tier or "RETAIL").upper()
    if tier not in price_table:
        tier = "RETAIL"  # safe fallback for un-tiered / new customers
    ladder = sorted(price_table[tier])            # by min_qty asc
    mins = [m for m, _ in ladder]
    i = bisect_right(mins, qty) - 1
    if i < 0:
        return {"ok": False, "reason": f"ต่ำกว่าขั้นต่ำ {mins[0]} ชิ้น", "moq": mins[0]}
    unit = ladder[i][1]
    # proactive upsell: distance to next price break
    nxt = ladder[i + 1] if i + 1 < len(ladder) else None
    upsell = None
    if nxt:
        need = nxt[0] - qty
        save = (unit - nxt[1]) * nxt[0]
        upsell = {"add_qty": need, "next_unit": nxt[1], "approx_save": round(save, 2)}
    return {"ok": True, "tier": tier, "unit_price": unit,
            "line_total": round(unit * qty, 2), "upsell": upsell}


if __name__ == "__main__":
    table = {"RETAIL": [(1, 25.0)],
             "WHOLESALE": [(1, 21.0), (24, 19.5), (240, 18.0)],
             "DEALER": [(24, 18.5), (240, 16.9), (1200, 15.5)]}
    print(resolve_price(table, "WHOLESALE", 20))   # near 24-ladder -> upsell hint
    print(resolve_price(table, "DEALER", 12))      # below dealer MOQ
