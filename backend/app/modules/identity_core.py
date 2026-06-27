"""Identity core — users, roles, permissions, plans, device sessions."""
from __future__ import annotations

import os
from typing import Any

from app import auth_middleware, db
from app.modules.common import resolve_status
from app.v1_clients import supabase_client

MODULE_META = {
    "id": "identity_core",
    "name": "Identity Core",
    "surface": "backend",
}


def _owner_live() -> bool:
    try:
        db.get_consent()
        return True
    except Exception:
        return False


def _production_live() -> bool:
    return supabase_client.auth_configured() and supabase_client.ping()


def status() -> dict[str, Any]:
    mode = auth_middleware.release_mode()
    return {
        **MODULE_META,
        "status": resolve_status(
            "identity_core",
            production_live=_production_live(),
            owner_live=_owner_live(),
        ),
        "release_mode": mode,
        "owner_node": mode == "owner",
        "auth_enabled": auth_middleware.auth_enabled(),
        "auth_providers": auth_middleware.auth_providers(),
        "supabase_auth_live": supabase_client.auth_configured(),
        "env_required": [
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY",
            "SUPABASE_JWT_SECRET",
        ],
        "env_optional": ["FIREBASE_PROJECT_ID"],
        "sqlite_fallback": mode == "owner",
        "notes": "Production uses Supabase Auth; owner node bypasses auth.",
    }


def get_owner_status() -> dict[str, Any]:
    return {
        "owner_mode": auth_middleware.release_mode() == "owner",
        "consent": db.get_consent(),
        "status": resolve_status(
            "identity_core",
            production_live=_production_live(),
            owner_live=_owner_live(),
        ),
    }


def handle_profile_stub(user_id: str) -> dict[str, Any]:
    profile = None
    if supabase_client.is_configured():
        try:
            client = supabase_client.get_client()
            result = (
                client.table("profiles")
                .select("*")
                .eq("id", user_id)
                .limit(1)
                .execute()
            )
            if result.data:
                profile = result.data[0]
        except Exception:
            pass
    return {
        "user_id": user_id,
        "profile": profile,
        "status": resolve_status(
            "identity_core",
            production_live=_production_live(),
            owner_live=_owner_live(),
        ),
    }


def handle_session_stub(device_id: str) -> dict[str, Any]:
    return {
        "device_id": device_id,
        "session": None,
        "status": resolve_status(
            "identity_core",
            production_live=_production_live(),
            owner_live=_owner_live(),
        ),
    }


def supabase_configured() -> bool:
    return bool(
        os.getenv("SUPABASE_URL", "").strip()
        and os.getenv("SUPABASE_ANON_KEY", "").strip()
    )
