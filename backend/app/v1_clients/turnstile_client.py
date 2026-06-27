"""Cloudflare Turnstile — siteverify via httpx."""
from __future__ import annotations

import logging
import os

import httpx

logger = logging.getLogger(__name__)

SITEVERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def is_configured() -> bool:
    return bool(os.getenv("TURNSTILE_SECRET_KEY", "").strip())


def verify(token: str, remote_ip: str | None = None) -> dict[str, object]:
    if not is_configured():
        return {"success": False, "error": "turnstile_not_configured"}
    if not token:
        return {"success": False, "error": "missing_token"}

    payload: dict[str, str] = {
        "secret": os.getenv("TURNSTILE_SECRET_KEY", "").strip(),
        "response": token,
    }
    if remote_ip:
        payload["remoteip"] = remote_ip

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(SITEVERIFY_URL, data=payload)
            response.raise_for_status()
            data = response.json()
            return {
                "success": bool(data.get("success")),
                "error_codes": data.get("error-codes", []),
                "hostname": data.get("hostname"),
            }
    except Exception as exc:
        logger.debug("turnstile verify failed: %s", exc)
        return {"success": False, "error": str(exc)}
