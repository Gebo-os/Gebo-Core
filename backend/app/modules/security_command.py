"""Security command — rate limits, abuse detection, audit logs."""
from __future__ import annotations

import os
from typing import Any

from app import auth_middleware, model_armor, recaptcha
from app.modules.common import resolve_status
from app.v1_clients import supabase_client, turnstile_client, upstash_client

MODULE_META = {
    "id": "security_command",
    "name": "Security Command",
    "surface": "backend",
}


def _owner_live() -> bool:
    return False


def _production_live() -> bool:
    return upstash_client.ping() and turnstile_client.is_configured()


def status() -> dict[str, Any]:
    return {
        **MODULE_META,
        "status": resolve_status(
            "security_command",
            production_live=_production_live(),
            owner_live=_owner_live(),
        ),
        "auth_enabled": auth_middleware.auth_enabled(),
        "model_armor_active": model_armor.model_armor_active(),
        "recaptcha_configured": recaptcha.recaptcha_configured(),
        "turnstile_configured": turnstile_client.is_configured(),
        "upstash_live": upstash_client.ping(),
        "env_required": [
            "UPSTASH_REDIS_REST_URL",
            "UPSTASH_REDIS_REST_TOKEN",
            "TURNSTILE_SECRET_KEY",
        ],
        "notes": "Upstash rate limits + Turnstile + Supabase audit logs in production.",
    }


def handle_rate_limit_stub(
    client_id: str,
    route: str,
    *,
    limit: int = 60,
    window_sec: int = 60,
) -> dict[str, Any]:
    identifier = f"{client_id}:{route}"
    result = upstash_client.check_rate_limit(identifier, limit, window_sec)
    return {
        "client_id": client_id,
        "route": route,
        "allowed": result.get("allowed", True),
        "remaining": result.get("remaining"),
        "count": result.get("count"),
        "backend": result.get("backend"),
        "status": resolve_status(
            "security_command",
            production_live=_production_live(),
            owner_live=_owner_live(),
        ),
    }


def handle_audit_stub(event_type: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    logged = supabase_client.insert_audit_log(event_type, payload)
    return {
        "event_type": event_type,
        "payload": payload or {},
        "logged": logged,
        "status": resolve_status(
            "security_command",
            production_live=_production_live(),
            owner_live=_owner_live(),
        ),
    }


def verify_turnstile(token: str, remote_ip: str | None = None) -> dict[str, Any]:
    return turnstile_client.verify(token, remote_ip)
