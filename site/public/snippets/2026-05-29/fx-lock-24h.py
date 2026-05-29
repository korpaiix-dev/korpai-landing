"""
KORP AI — Medical-tourism FX lock 24h
2026-05-29 — MIT
For aesthetic clinic chatbots serving inbound CN/KR/EN/JP patients.

Why: customers in CN/KR ask for quotes 3 weeks before flying.
THB volatility 2-5% in 3 weeks → if not locked, clinic must either
absorb the loss or rejection-cancel → Trustpilot damage.

Strategy: lock a (currency, rate, expires_at_unix) tuple per deposit_invoice.
After 24h without payment, regenerate quote. After payment, quote is fixed
for entire engagement (deposit + balance-on-arrival).

Source rate: Bank of Thailand mid-rate + 0.5% buffer for clinic margin.
"""
import time
import hmac, hashlib
from dataclasses import dataclass
from typing import Optional

# In production, refresh from https://www.bot.or.th/en/statistics/exchange-rate.html every 30 min
BOT_RATE_CACHE = {
    # currency -> THB per 1 unit of foreign currency
    "USD": 36.42,
    "CNY": 5.04,
    "KRW": 0.0263,
    "JPY": 0.2305,
    "EUR": 39.18,
}

BUFFER_PCT = 0.5  # 0.5% margin

@dataclass
class FxQuote:
    quote_id: str
    base_thb: int
    currency: str
    foreign_amount: float
    rate_at_lock: float          # THB per 1 unit of foreign currency
    locked_at_unix: int
    expires_at_unix: int          # locked_at + 86400

def lock_quote(base_thb: int, currency: str, secret_key: bytes) -> FxQuote:
    raw_rate = BOT_RATE_CACHE[currency]
    rate = raw_rate * (1 - BUFFER_PCT / 100)  # clinic receives slightly less THB to be safe
    foreign = round(base_thb / rate, 2)
    now = int(time.time())
    sig = hmac.new(secret_key,
                   f"{base_thb}|{currency}|{rate}|{now}".encode(),
                   hashlib.sha256).hexdigest()[:12]
    return FxQuote(
        quote_id=f"FX-{currency}-{now}-{sig}",
        base_thb=base_thb,
        currency=currency,
        foreign_amount=foreign,
        rate_at_lock=rate,
        locked_at_unix=now,
        expires_at_unix=now + 86400,
    )

def is_quote_still_valid(q: FxQuote, now_unix: Optional[int] = None) -> bool:
    now = now_unix or int(time.time())
    return now <= q.expires_at_unix

def thb_to_charge_at_balance(q: FxQuote, foreign_paid_now: float) -> int:
    """If patient paid `foreign_paid_now` as deposit at lock rate, return the
    THB equivalent already locked. Balance at clinic uses same lock rate."""
    return int(round(foreign_paid_now * q.rate_at_lock))

if __name__ == "__main__":
    q = lock_quote(120000, "CNY", b"clinic-secret-2026")
    print("CN patient quote:", q)
    print("Valid now?", is_quote_still_valid(q))
    print("Patient paid 8000 CNY → THB locked:", thb_to_charge_at_balance(q, 8000))
