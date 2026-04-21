"""
Thin async OpenRouter client. Uses httpx directly so we can stay small.

OpenRouter speaks the OpenAI chat completion shape, so this is ~50 LOC.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

import httpx

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class OpenRouterError(RuntimeError):
    pass


async def chat_complete(
    messages: List[Dict[str, str]],
    *,
    model: str,
    temperature: float = 0.4,
    max_tokens: int = 512,
    timeout: float = 30.0,
) -> str:
    """Send messages to OpenRouter and return the assistant reply text."""
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise OpenRouterError("OPENROUTER_API_KEY not set in environment")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.environ.get("OPENROUTER_APP_URL", "https://korpai.co"),
        "X-Title": os.environ.get("OPENROUTER_APP_TITLE", "KORP AI"),
    }
    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(OPENROUTER_URL, headers=headers, json=payload)

    if resp.status_code >= 400:
        # Surface as much detail as OpenRouter gives us.
        body = resp.text[:500]
        raise OpenRouterError(
            f"OpenRouter {resp.status_code}: {body}"
        )

    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise OpenRouterError(f"Unexpected OpenRouter response shape: {data}") from exc
