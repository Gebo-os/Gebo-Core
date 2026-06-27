"""Admin console — users, logs, failed AI, document jobs."""
from __future__ import annotations

from typing import Any

from app import db
from app.modules.common import resolve_status
from app.v1_clients import supabase_client

MODULE_META = {
    "id": "admin_console",
    "name": "Admin Console",
    "surface": "backend",
}


def _owner_live() -> bool:
    return False


def _production_live() -> bool:
    return supabase_client.ping()


def _local_stats() -> dict[str, int]:
    return {
        "memories": db.count_memories(),
        "messages": db.count_messages(),
        "proposed_actions": db.count_actions_by_status("proposed"),
    }


def _supabase_counts() -> dict[str, int] | None:
    if not supabase_client.is_configured():
        return None
    try:
        client = supabase_client.get_client()
        profiles = client.table("profiles").select("id", count="exact").limit(0).execute()
        audit = client.table("audit_logs").select("id", count="exact").limit(0).execute()
        return {
            "users": profiles.count or 0,
            "audit_logs": audit.count or 0,
        }
    except Exception:
        return None


def status() -> dict[str, Any]:
    counts = _supabase_counts() or _local_stats()
    return {
        **MODULE_META,
        "status": resolve_status(
            "admin_console",
            production_live=_production_live(),
            owner_live=_owner_live(),
        ),
        "counts": counts,
        "local_stats": _local_stats(),
        "env_required": ["SUPABASE_SERVICE_ROLE_KEY"],
        "notes": "Admin routes — production gated by role + RLS bypass service role.",
    }


def handle_users_stub(limit: int = 50) -> dict[str, Any]:
    users: list[dict[str, Any]] = []
    if supabase_client.is_configured():
        try:
            client = supabase_client.get_client()
            result = client.table("profiles").select("*").limit(limit).execute()
            users = result.data or []
        except Exception:
            pass
    return {
        "users": users,
        "limit": limit,
        "status": resolve_status(
            "admin_console",
            production_live=_production_live(),
            owner_live=_owner_live(),
        ),
    }


def handle_failed_ai_stub(limit: int = 20) -> dict[str, Any]:
    return {
        "failed_requests": [],
        "limit": limit,
        "status": resolve_status(
            "admin_console",
            production_live=_production_live(),
            owner_live=_owner_live(),
        ),
    }


def handle_document_jobs_stub(limit: int = 20) -> dict[str, Any]:
    return {
        "jobs": [],
        "limit": limit,
        "status": resolve_status(
            "admin_console",
            production_live=_production_live(),
            owner_live=_owner_live(),
        ),
    }
