# cross-user-firewall.py
# Layer 5 of the KORP AI 8-layer chatbot security stack.
# Stops the #1 real-world chatbot data leak of 2025: IDOR + prompt injection returning
# ANOTHER customer's records. Rule: the bot never chooses which record to read.
# The query is ALWAYS bound to the authenticated requester's identity, in code, not in the prompt.
# Maps to OWASP LLM02 (Sensitive Information Disclosure) + LLM06 (Excessive Agency).

from dataclasses import dataclass

class AccessDenied(Exception):
    pass

@dataclass
class Requester:
    # Identity proven by the channel (LINE userId / verified phone), NOT by what the user typed.
    line_user_id: str
    verified_phone: str | None = None
    role: str = "customer"  # customer | staff | admin

def get_order(requester: Requester, order_id: str, db) -> dict:
    """Fetch an order, but ONLY if it belongs to the requester (or staff/admin)."""
    order = db.find_order(order_id)
    if not order:
        raise AccessDenied("not_found")  # do not reveal existence to non-owners

    if requester.role in ("staff", "admin"):
        return order

    # Ownership must match the *channel-proven* identity, never a value from the chat text.
    if order.get("line_user_id") != requester.line_user_id:
        # Same generic error as not_found, so attackers can't enumerate IDs.
        raise AccessDenied("not_found")

    return order

def search_customer(requester: Requester, query: str, db) -> list[dict]:
    """Customers may only ever 'search' themselves. Staff may search within scope."""
    if requester.role == "customer":
        # Ignore the free-text query entirely; return only the requester's own profile.
        me = db.find_customer_by_line(requester.line_user_id)
        return [me] if me else []
    # staff/admin: allow query but log it (layer 8) and scope to their branch.
    results = db.search_customers(query, branch=getattr(requester, "branch", None))
    db.audit("customer_search", actor=requester.line_user_id, q=query, n=len(results))
    return results

# Golden rule, printed for reviewers:
GOLDEN_RULE = (
    "LLM proposes intent; CODE decides access. "
    "Never pass an LLM-chosen record id to the DB without an ownership check."
)

if __name__ == "__main__":
    class FakeDB:
        orders = {"1001": {"line_user_id": "U_alice", "total": 590},
                  "1002": {"line_user_id": "U_bob",   "total": 120}}
        def find_order(self, oid): return self.orders.get(oid)
        def find_customer_by_line(self, uid): return {"line_user_id": uid, "name": "me"}
        def search_customers(self, q, branch=None): return []
        def audit(self, *a, **k): pass

    db = FakeDB()
    alice = Requester(line_user_id="U_alice")
    print("Alice reads her order:", get_order(alice, "1001", db))
    try:
        get_order(alice, "1002", db)  # Bob's order -> blocked
    except AccessDenied as e:
        print("Alice reading Bob's order ->", e)
