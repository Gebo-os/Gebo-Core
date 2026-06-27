"""Shared module status resolution for owner vs production modes."""
from __future__ import annotations

import os


def resolve_status(module_id: str, *, production_live: bool, owner_live: bool) -> str:
    mode = os.getenv("GEBO_RELEASE_MODE", "owner").lower()
    if mode == "owner" and owner_live:
        return "active"
    if mode == "production" and production_live:
        return "active"
    return "inactive"
