"""
KORP AI Chat Backend — FastAPI app.

Endpoints:
    GET  /api/chat/health
    POST /api/chat/session        → creates a session, returns greeting + sid
    POST /api/chat/message        → streams nothing fancy; returns {reply, handoff}
    POST /api/chat/handoff        → logs handoff click, optionally notifies webhook
    POST /api/chat/feedback       → thumbs up/down

Run locally:
    cd chat-backend
    cp .env.example .env
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8100
"""

from __future__ import annotations

import logging
import os
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import Cookie, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent import (
    GREETING,
    SYSTEM_PROMPT,
    classify_intent,
    extract_handoff,
    sanitize_user_input,
    should_use_deep_model,
)
from openrouter import OpenRouterError, chat_complete
from session_store import RateLimiter, SessionStore

# ---------------------------------------------------------------------------
# Boot
# ---------------------------------------------------------------------------
load_dotenv()

LOG = logging.getLogger("korpai.chat")
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

COOKIE_NAME = os.environ.get("CHAT_COOKIE_NAME", "korpai_chat_sid")
COOKIE_SECURE = os.environ.get("CHAT_COOKIE_SECURE", "true").lower() == "true"
SESSION_TTL = int(os.environ.get("CHAT_SESSION_TTL_MIN", "60"))
SESSION_MAX_TURNS = int(os.environ.get("CHAT_SESSION_MAX_TURNS", "30"))

MODEL_FAST = os.environ.get("OPENROUTER_MODEL_FAST", "anthropic/claude-haiku-4.5")
MODEL_DEEP = os.environ.get("OPENROUTER_MODEL_DEEP", "anthropic/claude-sonnet-4.6")

LINE_URL = os.environ.get("HANDOFF_LINE_URL", "https://lin.ee/Qt6Vri4")
FB_URL = os.environ.get("HANDOFF_FB_URL", "https://www.facebook.com/korpaiix")
HANDOFF_WEBHOOK = os.environ.get("HANDOFF_WEBHOOK_URL", "").strip()

sessions = SessionStore(ttl_minutes=SESSION_TTL, max_turns=SESSION_MAX_TURNS)
limiter = RateLimiter(
    per_minute=int(os.environ.get("CHAT_RL_MAX_PER_MIN", "20")),
    per_hour=int(os.environ.get("CHAT_RL_MAX_PER_HOUR", "120")),
)

origins = [
    o.strip()
    for o in os.environ.get("CHAT_CORS_ORIGINS", "https://korpai.co").split(",")
    if o.strip()
]

app = FastAPI(title="KORP AI Chat Backend", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class SessionResponse(BaseModel):
    sid: str
    greeting: str
    line_url: str
    fb_url: str


class MessageIn(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)


class MessageOut(BaseModel):
    reply: str
    handoff: bool
    intent: str
    model: str


class HandoffIn(BaseModel):
    channel: str = Field(..., pattern="^(line|fb|email)$")
    note: Optional[str] = None


class FeedbackIn(BaseModel):
    rating: int = Field(..., ge=-1, le=1)
    note: Optional[str] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _client_ip(request: Request) -> str:
    # Nginx sets X-Forwarded-For; fall back to client host.
    xff = request.headers.get("x-forwarded-for", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else ""


def _set_cookie(response: Response, sid: str) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=sid,
        max_age=SESSION_TTL * 60,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        path="/api/chat",
    )


async def _notify_handoff(channel: str, summary: str) -> None:
    """Fire-and-forget webhook. Never raises."""
    if not HANDOFF_WEBHOOK:
        return
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(
                HANDOFF_WEBHOOK,
                json={
                    "text": f"🔔 *KORP AI chat → handoff ({channel})*\n```{summary}```",
                },
            )
    except Exception as exc:  # noqa: BLE001
        LOG.warning("handoff webhook failed: %s", exc)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/api/chat/health")
async def health() -> dict:
    return {"ok": True, "sessions": await sessions.count()}


@app.post("/api/chat/session", response_model=SessionResponse)
async def create_session(request: Request, response: Response) -> SessionResponse:
    ip = _client_ip(request)
    if not await limiter.allow(f"sess:{ip}"):
        raise HTTPException(status_code=429, detail="Too many sessions. Try again later.")
    ua = request.headers.get("user-agent", "")[:256]
    sess = await sessions.create(client_ip=ip, user_agent=ua)
    _set_cookie(response, sess.sid)
    return SessionResponse(
        sid=sess.sid,
        greeting=GREETING,
        line_url=LINE_URL,
        fb_url=FB_URL,
    )


@app.post("/api/chat/message", response_model=MessageOut)
async def post_message(
    payload: MessageIn,
    request: Request,
    response: Response,
    sid: Optional[str] = Cookie(default=None, alias=COOKIE_NAME),
) -> MessageOut:
    ip = _client_ip(request)
    if not await limiter.allow(f"msg:{ip}"):
        raise HTTPException(status_code=429, detail="ข้อความถี่เกินไป รอแป๊บนึงครับ")

    # Auto-create session if the cookie is missing (first message case)
    sess = await sessions.get(sid) if sid else None
    if sess is None:
        sess = await sessions.create(
            client_ip=ip,
            user_agent=request.headers.get("user-agent", "")[:256],
        )
        _set_cookie(response, sess.sid)

    user_text = sanitize_user_input(payload.message)
    if not user_text:
        raise HTTPException(status_code=400, detail="Empty message")

    intent = classify_intent(user_text)
    model = MODEL_DEEP if should_use_deep_model(intent, sess.turn_count) else MODEL_FAST

    await sessions.append(sess, "user", user_text)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + sess.messages

    try:
        reply_raw = await chat_complete(
            messages=messages,
            model=model,
            temperature=0.5,
            max_tokens=600,
        )
    except OpenRouterError as exc:
        LOG.error("openrouter failure: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="ขออภัยครับ ระบบขัดข้องชั่วคราว ลองใหม่อีกครั้งนะครับ",
        ) from exc

    reply_text, handoff = extract_handoff(reply_raw)
    if handoff:
        await sessions.mark_handoff(sess)
    await sessions.append(sess, "assistant", reply_text)

    return MessageOut(
        reply=reply_text,
        handoff=handoff,
        intent=intent,
        model=model,
    )


@app.post("/api/chat/handoff")
async def handoff(
    payload: HandoffIn,
    request: Request,
    sid: Optional[str] = Cookie(default=None, alias=COOKIE_NAME),
) -> dict:
    sess = await sessions.get(sid) if sid else None
    if sess is None:
        # Still acknowledge — user may have clicked from a restored widget
        return {"ok": True, "url": LINE_URL if payload.channel == "line" else FB_URL}

    await sessions.mark_handoff(sess)

    last_user = next(
        (m["content"] for m in reversed(sess.messages) if m["role"] == "user"),
        "(no message)",
    )
    summary = (
        f"channel: {payload.channel}\n"
        f"sid: {sess.sid}\n"
        f"turns: {sess.turn_count}\n"
        f"ip: {sess.client_ip}\n"
        f"last_user: {last_user[:300]}\n"
        f"note: {payload.note or ''}"
    )
    await _notify_handoff(payload.channel, summary)

    url = LINE_URL if payload.channel == "line" else FB_URL
    return {"ok": True, "url": url}


@app.post("/api/chat/feedback")
async def feedback(
    payload: FeedbackIn,
    sid: Optional[str] = Cookie(default=None, alias=COOKIE_NAME),
) -> dict:
    LOG.info("feedback sid=%s rating=%s note=%s", sid, payload.rating, payload.note)
    return {"ok": True}


# ---------------------------------------------------------------------------
# Background housekeeping
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def _startup() -> None:
    import asyncio

    async def _gc() -> None:
        while True:
            await asyncio.sleep(300)
            try:
                evicted = await sessions.prune_expired()
                if evicted:
                    LOG.info("pruned %d expired sessions", evicted)
            except Exception as exc:  # noqa: BLE001
                LOG.warning("gc failed: %s", exc)

    asyncio.create_task(_gc())
