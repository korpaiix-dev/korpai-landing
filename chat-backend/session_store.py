"""
In-memory session + rate-limit store.

Good enough for MVP (single-process uvicorn). When we outgrow this — or want
restarts to preserve sessions — swap the backing dict for Redis and keep the
interface identical.
"""

from __future__ import annotations

import asyncio
import secrets
import time
from dataclasses import dataclass, field
from typing import Deque, Dict, List
from collections import deque


@dataclass
class ChatSession:
    sid: str
    created_at: float
    last_active: float
    # OpenAI-style messages (no system prompt — that's prepended at request time)
    messages: List[Dict[str, str]] = field(default_factory=list)
    turn_count: int = 0
    handoff_triggered: bool = False
    client_ip: str = ""
    user_agent: str = ""


class SessionStore:
    """Thread-safe-ish session store using an asyncio lock."""

    def __init__(self, *, ttl_minutes: int = 60, max_turns: int = 30):
        self._sessions: Dict[str, ChatSession] = {}
        self._lock = asyncio.Lock()
        self._ttl = ttl_minutes * 60
        self._max_turns = max_turns

    async def create(self, *, client_ip: str = "", user_agent: str = "") -> ChatSession:
        sid = secrets.token_urlsafe(24)
        now = time.time()
        sess = ChatSession(
            sid=sid,
            created_at=now,
            last_active=now,
            client_ip=client_ip,
            user_agent=user_agent,
        )
        async with self._lock:
            self._sessions[sid] = sess
        return sess

    async def get(self, sid: str) -> ChatSession | None:
        if not sid:
            return None
        async with self._lock:
            sess = self._sessions.get(sid)
            if not sess:
                return None
            if time.time() - sess.last_active > self._ttl:
                # Expired — evict
                self._sessions.pop(sid, None)
                return None
            return sess

    async def touch(self, sess: ChatSession) -> None:
        async with self._lock:
            sess.last_active = time.time()

    async def append(
        self, sess: ChatSession, role: str, content: str
    ) -> None:
        async with self._lock:
            sess.messages.append({"role": role, "content": content})
            if role == "user":
                sess.turn_count += 1
            sess.last_active = time.time()
            # Keep memory bounded
            if len(sess.messages) > self._max_turns * 2:
                # Drop oldest pair
                sess.messages = sess.messages[-(self._max_turns * 2):]

    async def mark_handoff(self, sess: ChatSession) -> None:
        async with self._lock:
            sess.handoff_triggered = True

    async def prune_expired(self) -> int:
        """Periodic housekeeping; returns number evicted."""
        cutoff = time.time() - self._ttl
        async with self._lock:
            dead = [s for s, v in self._sessions.items() if v.last_active < cutoff]
            for sid in dead:
                self._sessions.pop(sid, None)
            return len(dead)

    async def count(self) -> int:
        async with self._lock:
            return len(self._sessions)


class RateLimiter:
    """Token-bucket-ish per-key limiter. Key is usually IP."""

    def __init__(self, *, per_minute: int = 20, per_hour: int = 120):
        self._per_minute = per_minute
        self._per_hour = per_hour
        self._buckets_min: Dict[str, Deque[float]] = {}
        self._buckets_hour: Dict[str, Deque[float]] = {}
        self._lock = asyncio.Lock()

    async def allow(self, key: str) -> bool:
        if not key:
            return True
        now = time.time()
        async with self._lock:
            mb = self._buckets_min.setdefault(key, deque())
            hb = self._buckets_hour.setdefault(key, deque())
            # Evict old entries
            while mb and now - mb[0] > 60:
                mb.popleft()
            while hb and now - hb[0] > 3600:
                hb.popleft()
            if len(mb) >= self._per_minute or len(hb) >= self._per_hour:
                return False
            mb.append(now)
            hb.append(now)
            return True
