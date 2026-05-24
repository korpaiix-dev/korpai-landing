"""
sla-pre-alert.py
Pre-alert dispatcher + driver BEFORE a parcel breaches its delivery promise.
Goal: cut customer complaint from SLA breach by ~68% — say sorry before customer asks.

Schedule this every 5–10 minutes via cron / scheduler.
Companion to: https://korpai.co/blog/ai-chatbot-ขนส่ง-โลจิสติกส์-logistics-sme-2026
MIT — KORP AI Automation.
"""
from __future__ import annotations
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class Order:
    id: str
    status: str          # 'pending'|'pickup'|'in_transit'|'out_for_delivery'|'delivered'
    delivery_promise: datetime
    driver_id: str
    dispatcher_id: str
    customer_id: str
    carrier: str


PRE_ALERT_MINUTES = 90   # < 90 min left + not delivered → warn driver
WARN_MINUTES = 30        # < 30 min left → escalate dispatcher
ETA_BUMP_MINUTES = 60    # When breached, give the customer ETA = now + this


def check_sla(order: Order, notifier, now: datetime | None = None) -> str:
    """
    notifier interface:
      notifier.driver(driver_id, msg)
      notifier.dispatcher(dispatcher_id, severity, msg)
      notifier.customer(customer_id, msg)
    Returns action taken (string) for logging.
    """
    now = now or datetime.utcnow()
    if order.status == "delivered":
        return "skip:delivered"

    remaining_min = (order.delivery_promise - now).total_seconds() / 60

    # Already breached
    if remaining_min < 0 and order.status != "delivered":
        new_eta = (now + timedelta(minutes=ETA_BUMP_MINUTES)).strftime("%H:%M")
        notifier.customer(
            order.customer_id,
            f"ขอโทษค่ะ ออเดอร์ {order.id} มี delay เล็กน้อย "
            f"ETA ใหม่ประมาณ {new_eta} น. — เราจะแจ้งเตือนทันทีที่ของถึงค่ะ"
        )
        notifier.dispatcher(
            order.dispatcher_id, "critical",
            f"{order.id} BREACHED by {-remaining_min:.0f} min — auto-notified customer"
        )
        return "breach:notified_customer"

    # Soft warning
    if remaining_min < WARN_MINUTES and order.status in ("pickup", "in_transit"):
        notifier.dispatcher(
            order.dispatcher_id, "warning",
            f"{order.id} เหลือ {remaining_min:.0f} นาที / status={order.status}"
        )
        return "warn:dispatcher"

    # Pre-alert driver
    if remaining_min < PRE_ALERT_MINUTES and order.status in ("pickup", "in_transit"):
        notifier.driver(
            order.driver_id,
            f"⚠️ {order.id} เหลือ {remaining_min:.0f} นาที — เร่งหน่อยนะ"
        )
        return "prealert:driver"

    return "skip:within_sla"


def scan_orders(open_orders: list[Order], notifier):
    summary = {"prealert:driver": 0, "warn:dispatcher": 0,
               "breach:notified_customer": 0, "skip:within_sla": 0, "skip:delivered": 0}
    for o in open_orders:
        a = check_sla(o, notifier)
        summary[a] = summary.get(a, 0) + 1
    return summary
