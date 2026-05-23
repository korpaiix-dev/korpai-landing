"""
Group-booking PDPA consent batch flow for Thai travel agencies.

When a group leader books for 10+ travelers, the bot must NOT accept passport
copies forwarded by the leader. PDPA Section 19 requires consent direct from the
data subject. This module generates per-passenger consent links and tracks status.

Source: KORP AI - https://korpai.co/snippets/2026-05-23/group-booking-pdpa-consent.py
License: MIT
"""
from __future__ import annotations
import secrets
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Literal


@dataclass
class Passenger:
    full_name: str
    contact: str  # email or phone
    consent_token: str = ""
    consent_given_at: datetime | None = None
    passport_uploaded_at: datetime | None = None
    status: Literal["pending", "consented", "uploaded", "expired"] = "pending"


@dataclass
class GroupBooking:
    booking_id: str
    leader_contact: str
    trip_destination: str
    departure_date: datetime
    passengers: list[Passenger] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    consent_ttl_hours: int = 72

    def add_passenger(self, name: str, contact: str) -> Passenger:
        # Per-passenger unguessable token; never shared with leader
        token = secrets.token_urlsafe(32)
        p = Passenger(full_name=name, contact=contact, consent_token=token)
        self.passengers.append(p)
        return p

    def consent_link(self, p: Passenger, base_url: str) -> str:
        return f"{base_url}/consent/{self.booking_id}/{p.consent_token}"

    def expire_stale_consents(self) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self.consent_ttl_hours)
        count = 0
        for p in self.passengers:
            if p.status == "pending" and self.created_at < cutoff:
                p.status = "expired"
                count += 1
        return count

    def progress(self) -> dict:
        n = len(self.passengers)
        if n == 0:
            return {"total": 0, "consented": 0, "uploaded": 0, "complete": False}
        consented = sum(1 for p in self.passengers if p.status in ("consented", "uploaded"))
        uploaded = sum(1 for p in self.passengers if p.status == "uploaded")
        return {
            "total": n,
            "consented": consented,
            "uploaded": uploaded,
            "complete": uploaded == n,
        }

    def retention_purge_after_trip(self) -> None:
        """Per PDPA retention: delete passport scans 90 days after trip end."""
        # Implementation note: in production, run a daily job that drops the encrypted
        # blob from object storage and logs the deletion event for the audit trail.
        pass


def audit_hash(token: str) -> str:
    """Store hashed token in audit logs - never the raw token."""
    return hashlib.sha256(token.encode()).hexdigest()[:16]


if __name__ == "__main__":
    g = GroupBooking(
        booking_id="BK-2026-05-23-001",
        leader_contact="leader@example.com",
        trip_destination="Seoul-Busan 5D4N",
        departure_date=datetime(2026, 7, 15, tzinfo=timezone.utc),
    )
    for i in range(1, 19):
        g.add_passenger(f"Traveler {i}", f"trav{i}@example.com")
    print(f"Group of {len(g.passengers)} - consent links generated")
    print("Progress:", g.progress())
    # Sample consent link (each passenger gets a unique one):
    p = g.passengers[0]
    print("Link:", g.consent_link(p, "https://korpai.co"))
    print("Audit-safe token hash:", audit_hash(p.consent_token))
