"""V1 control health checks — live pings mapped to release_stack control IDs."""
from __future__ import annotations

import logging
import os
from typing import Any, Callable

import httpx

from app.v1_clients import ai_providers, stripe_client, supabase_client, turnstile_client, upstash_client

logger = logging.getLogger(__name__)

_CACHE: dict[str, bool] = {}


def _env_ready(keys: list[str]) -> bool:
    return all(os.getenv(k, "").strip() for k in keys)


def _database_ping() -> bool:
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        return False
    try:
        import psycopg2

        conn = psycopg2.connect(url, connect_timeout=5)
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return True
    except Exception as exc:
        logger.debug("database ping failed: %s", exc)
        return False


def _pgvector_ping() -> bool:
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        return False
    try:
        import psycopg2

        conn = psycopg2.connect(url, connect_timeout=5)
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM pg_extension WHERE extname = 'vector' LIMIT 1"
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row is not None
    except Exception as exc:
        logger.debug("pgvector ping failed: %s", exc)
        return False


def _vercel_ping() -> bool:
    if not _env_ready(["VERCEL_URL", "NEXT_PUBLIC_SUPABASE_URL"]):
        return False
    vercel_url = os.getenv("VERCEL_URL", "").strip()
    if not vercel_url:
        return False
    if not vercel_url.startswith("http"):
        vercel_url = f"https://{vercel_url}"
    try:
        with httpx.Client(timeout=8.0, follow_redirects=True) as client:
            response = client.get(vercel_url)
            return response.status_code < 500
    except Exception as exc:
        logger.debug("vercel ping failed: %s", exc)
        return False


_CONTROL_CHECKS: dict[str, Callable[[], bool]] = {}


def _register_checks() -> None:
    if _CONTROL_CHECKS:
        return
    _CONTROL_CHECKS.update({
        "supabase_postgres": lambda: supabase_client.ping() and _database_ping(),
        "pgvector": _pgvector_ping,
        "supabase_auth": lambda: supabase_client.auth_configured() and supabase_client.ping(),
        "supabase_storage": supabase_client.storage_ping,
        "vercel_deploy": _vercel_ping,
        "cloudflare_turnstile": turnstile_client.is_configured,
        "upstash_redis": upstash_client.ping,
        "stripe": stripe_client.ping,
        "vercel_ai_gateway": lambda: ai_providers.ping_openai() or False,
        "supabase_rls": supabase_client.ping,
        "resend": lambda: _env_ready(["RESEND_API_KEY"]),
        "sentry": lambda: _env_ready(["SENTRY_DSN"]),
        "langfuse": lambda: _env_ready(["LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"]),
        "posthog": lambda: _env_ready(["NEXT_PUBLIC_POSTHOG_KEY"]),
        "auth0": lambda: _env_ready(["AUTH0_DOMAIN", "AUTH0_CLIENT_ID"]),
        "workos": lambda: _env_ready(["WORKOS_API_KEY", "WORKOS_CLIENT_ID"]),
    })


def check_control(control_id: str) -> bool:
    _register_checks()
    if control_id in _CACHE:
        return _CACHE[control_id]
    checker = _CONTROL_CHECKS.get(control_id)
    if checker is None:
        return False
    try:
        result = bool(checker())
    except Exception as exc:
        logger.debug("check_control %s failed: %s", control_id, exc)
        result = False
    return result


def check_all_required() -> dict[str, bool]:
    from app.release_stack import V1_CONTROLS

    _register_checks()
    return {
        ctrl["id"]: check_control(ctrl["id"])
        for ctrl in V1_CONTROLS
        if ctrl.get("release_tier") == "required"
    }


def warmup() -> dict[str, bool]:
    """Cache ping results for all required V1 controls (non-blocking best-effort)."""
    from app.release_stack import V1_CONTROLS

    _register_checks()
    results: dict[str, bool] = {}
    for ctrl in V1_CONTROLS:
        cid = ctrl["id"]
        if ctrl.get("release_tier") != "required":
            continue
        try:
            results[cid] = check_control(cid)
        except Exception:
            results[cid] = False
        _CACHE[cid] = results[cid]
    return results


def clear_cache() -> None:
    _CACHE.clear()
