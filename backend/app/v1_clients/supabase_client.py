"""Supabase — official Python SDK client."""
from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

_client: Any | None = None


def is_configured() -> bool:
    return bool(
        os.getenv("SUPABASE_URL", "").strip()
        and os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    )


def auth_configured() -> bool:
    return bool(
        os.getenv("SUPABASE_URL", "").strip()
        and os.getenv("SUPABASE_ANON_KEY", "").strip()
        and (
            os.getenv("SUPABASE_JWT_SECRET", "").strip()
            or os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        )
    )


def get_client() -> Any:
    global _client
    if _client is None:
        from supabase import create_client

        url = os.getenv("SUPABASE_URL", "").strip()
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        if not url or not key:
            raise RuntimeError("Supabase not configured")
        _client = create_client(url, key)
    return _client


def ping() -> bool:
    if not is_configured():
        return False
    try:
        client = get_client()
        client.table("profiles").select("id").limit(1).execute()
        return True
    except Exception as exc:
        logger.debug("supabase ping failed: %s", exc)
        try:
            client = get_client()
            client.auth.get_session()
            return True
        except Exception:
            return False


def storage_ping() -> bool:
    if not is_configured():
        return False
    try:
        client = get_client()
        buckets = client.storage.list_buckets()
        names = {b.name for b in buckets} if buckets else set()
        if "gebo-documents" in names:
            return True
        return bool(buckets)
    except Exception as exc:
        logger.debug("supabase storage ping failed: %s", exc)
        return False


def insert_audit_log(event_type: str, payload: dict[str, Any] | None = None) -> bool:
    if not is_configured():
        return False
    try:
        client = get_client()
        client.table("audit_logs").insert(
            {"event_type": event_type, "payload": payload or {}}
        ).execute()
        return True
    except Exception as exc:
        logger.debug("audit log insert failed: %s", exc)
        return False
