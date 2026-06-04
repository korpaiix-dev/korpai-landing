"""tracking-aggregator.py — normalize parcel status from multiple Thai carriers
into one shape, so the bot answers 'พัสดุถึงไหนแล้ว' the same way every time."""
from datetime import datetime, timezone

UNIFIED = ["created", "picked_up", "in_transit", "out_for_delivery",
           "delivered", "failed", "returned"]

CARRIER_MAP = {
    "flash":    {"RECEIVED": "picked_up", "TRANSPORT": "in_transit",
                 "DELIVERING": "out_for_delivery", "DELIVERED": "delivered", "RETURN": "returned"},
    "jt":       {"100": "picked_up", "200": "in_transit", "300": "out_for_delivery",
                 "400": "delivered", "500": "failed"},
    "thaipost": {"รับฝาก": "picked_up", "นำจ่าย": "out_for_delivery",
                 "นำจ่ายสำเร็จ": "delivered"},
}

def normalize(carrier, raw_status, ts=None):
    carrier = (carrier or "").lower()
    status = CARRIER_MAP.get(carrier, {}).get(str(raw_status), "in_transit")
    return {
        "carrier": carrier,
        "status": status,                     # always one of UNIFIED
        "is_final": status in ("delivered", "returned"),
        "ts": ts or datetime.now(timezone.utc).isoformat(),
    }
