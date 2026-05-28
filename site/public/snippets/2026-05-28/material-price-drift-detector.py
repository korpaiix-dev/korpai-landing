"""
KORP AI — Material Price Drift Detector for Thai contractor / renovation chatbots.

Re-checks every active outstanding quote (status: 'sent', age < 30 days)
against the latest weekly RAG price snapshot. If any SKU in the quote BOQ has
moved > 7% (configurable), it (a) flags the quote 'needs_revise', (b) drafts
a customer-facing notification message, (c) emits a webhook for the chatbot
to schedule a follow-up.

Run via cron weekly (every Monday 09:00 Bangkok).
"""
from __future__ import annotations
import json, datetime, dataclasses, typing as t

PRICE_DRIFT_THRESHOLD = 0.07   # 7%
QUOTE_TTL_DAYS = 30

@dataclasses.dataclass
class QuoteLine:
    sku: str
    qty: float
    unit_price_at_quote: float  # THB per unit at the moment quote was sent

@dataclasses.dataclass
class Quote:
    quote_id: str
    customer_line_userid: str
    sent_at: datetime.datetime
    lines: list[QuoteLine]
    total_baht: float
    status: str   # 'sent' | 'accepted' | 'revised' | 'expired'

def load_latest_prices(rag_snapshot_path: str) -> dict[str, float]:
    """Load latest weekly material price snapshot from RAG (sku → price THB)."""
    with open(rag_snapshot_path) as f:
        return json.load(f)["prices"]

def detect_drift(quote: Quote, latest_prices: dict[str, float]) -> dict:
    movements = []
    for line in quote.lines:
        latest = latest_prices.get(line.sku)
        if latest is None:
            continue
        pct = (latest - line.unit_price_at_quote) / line.unit_price_at_quote
        if abs(pct) >= PRICE_DRIFT_THRESHOLD:
            movements.append({
                "sku": line.sku,
                "qty": line.qty,
                "old_price": line.unit_price_at_quote,
                "new_price": latest,
                "pct_change": round(pct * 100, 1),
                "extra_cost_baht": round((latest - line.unit_price_at_quote) * line.qty),
            })
    if not movements:
        return {"needs_revise": False}
    extra = sum(m["extra_cost_baht"] for m in movements)
    return {
        "needs_revise": True,
        "movements": movements,
        "total_extra_baht": extra,
        "draft_customer_message_th": (
            f"เรียนลูกค้า — ราคาวัสดุบางรายการในใบเสนอราคา {quote.quote_id} ขยับ "
            f"เกิน {int(PRICE_DRIFT_THRESHOLD*100)}% ภายใน {QUOTE_TTL_DAYS} วัน "
            f"(โดยเฉลี่ยขยับ {round(sum(m['pct_change'] for m in movements)/len(movements), 1)}%). "
            f"ทีมงานจะส่ง Revise BOQ ให้พิจารณาภายในวันพรุ่งนี้ — รหัสอ้างอิงเดิมยังคงเดิมค่ะ"
        ),
    }

def process(active_quotes: t.Iterable[Quote], latest_prices: dict[str, float]) -> list[dict]:
    out = []
    now = datetime.datetime.now(datetime.timezone.utc)
    for q in active_quotes:
        if q.status != "sent":
            continue
        if (now - q.sent_at).days > QUOTE_TTL_DAYS:
            out.append({"quote_id": q.quote_id, "action": "expire"})
            continue
        result = detect_drift(q, latest_prices)
        if result["needs_revise"]:
            out.append({"quote_id": q.quote_id, "action": "revise", **result})
    return out
