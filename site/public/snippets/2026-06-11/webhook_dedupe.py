#!/usr/bin/env python3
"""Webhook redelivery dedupe (LINE / Meta) — stop paying twice for the same message.

Free/DIY stacks often answer duplicates: LINE & Meta both re-deliver webhooks on
slow ACK (timeout ~= a few seconds), and every duplicate = another LLM call you
pay for + a confusing double reply to the customer.

Strategy: ACK fast, dedupe on a stable event id with a TTL cache, process async.

  from webhook_dedupe import seen_before
  # LINE: use event["webhookEventId"]   Meta: use entry["id"] + message mid
  if seen_before(event_id):  return "OK", 200       # swallow duplicate
  queue_for_processing(event); return "OK", 200     # ACK fast (<2s)

Stdlib only, thread-safe, no Redis needed below ~50k events/day.
Companion to: https://korpai.co/blog/ai-chatbot-ฟรี-2026-ต้นทุนแฝง-sme
MIT — KORP AI (korpai.co)
"""
import threading, time

_TTL = 15 * 60            # 15 min: longer than any platform retry window
_lock = threading.Lock()
_seen: dict[str, float] = {}

def seen_before(event_id: str, ttl: int = _TTL) -> bool:
    """True if this event id was already handled within `ttl` seconds."""
    if not event_id:
        return False                      # never swallow events without an id
    now = time.time()
    with _lock:
        # opportunistic purge (keeps memory bounded without a timer thread)
        if len(_seen) > 10_000:
            for k, exp in list(_seen.items()):
                if exp < now:
                    _seen.pop(k, None)
        if _seen.get(event_id, 0) > now:
            return True
        _seen[event_id] = now + ttl
        return False

if __name__ == "__main__":
    assert seen_before("evt-1") is False
    assert seen_before("evt-1") is True      # duplicate caught
    assert seen_before("evt-2") is False
    assert seen_before("") is False
    print("dedupe OK — wire it before your LLM call, not after")
