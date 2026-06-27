"""Upstash Redis — REST API via httpx."""
from __future__ import annotations

import logging
import os

import httpx

logger = logging.getLogger(__name__)


def _rest_url() -> str:
    return os.getenv("UPSTASH_REDIS_REST_URL", "").strip().rstrip("/")


def _rest_token() -> str:
    return os.getenv("UPSTASH_REDIS_REST_TOKEN", "").strip()


def is_configured() -> bool:
    return bool(_rest_url() and _rest_token())


def _headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {_rest_token()}"}


def _command(*args: str) -> dict | None:
    if not is_configured():
        return None
    try:
        encoded = "/".join(args)
        url = f"{_rest_url()}/{encoded}"
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, headers=_headers())
            response.raise_for_status()
            return response.json()
    except Exception as exc:
        logger.debug("upstash command failed: %s", exc)
        return None


def ping() -> bool:
    result = _command("ping")
    if result is None:
        return False
    return result.get("result") == "PONG"


def check_rate_limit(identifier: str, limit: int, window_sec: int) -> dict[str, object]:
    """Sliding window rate limit via INCR + EXPIRE (Upstash REST)."""
    if not is_configured():
        return {"allowed": True, "remaining": None, "count": 0, "backend": "none"}

    key = f"gebo:ratelimit:{identifier}"
    incr = _command("incr", key)
    if incr is None:
        return {"allowed": True, "remaining": None, "count": 0, "backend": "error"}

    count = int(incr.get("result", 0))
    if count == 1:
        _command("expire", key, str(window_sec))

    allowed = count <= limit
    remaining = max(0, limit - count)
    return {
        "allowed": allowed,
        "remaining": remaining,
        "count": count,
        "backend": "upstash",
    }
