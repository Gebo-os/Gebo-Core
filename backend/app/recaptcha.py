"""reCAPTCHA Enterprise token verification (optional)."""
from __future__ import annotations

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

RECAPTCHA_VERIFY_URL = (
    "https://recaptchaenterprise.googleapis.com/v1/projects/{project}/assessments"
)


def recaptcha_configured() -> bool:
    return bool(os.getenv("RECAPTCHA_PROJECT_ID", "").strip())


def verify_recaptcha_token(
    token: str,
    *,
    action: str = "login",
    min_score: float = 0.5,
) -> dict[str, Any]:
    """Verify a reCAPTCHA Enterprise token. Returns ok=False when not configured."""
    project_id = os.getenv("RECAPTCHA_PROJECT_ID", "").strip()
    site_key = os.getenv("RECAPTCHA_SITE_KEY") or os.getenv(
        "NEXT_PUBLIC_RECAPTCHA_SITE_KEY", ""
    )

    if not project_id:
        return {"ok": False, "reason": "not_configured"}
    if not token:
        return {"ok": False, "reason": "missing_token"}

    api_key = os.getenv("RECAPTCHA_API_KEY", "").strip()
    if not api_key:
        return {"ok": False, "reason": "missing_api_key"}

    url = f"{RECAPTCHA_VERIFY_URL.format(project=project_id)}?key={api_key}"
    body = {
        "event": {
            "token": token,
            "siteKey": site_key,
            "expectedAction": action,
        }
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, json=body)
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        logger.warning("reCAPTCHA verify failed: %s", exc)
        return {"ok": False, "reason": "verify_error", "error": str(exc)}

    token_props = data.get("tokenProperties", {})
    valid = token_props.get("valid", False)
    score = data.get("riskAnalysis", {}).get("score", 0.0)
    ok = valid and score >= min_score
    return {
        "ok": ok,
        "valid": valid,
        "score": score,
        "action": token_props.get("action"),
    }
