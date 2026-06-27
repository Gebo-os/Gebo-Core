"""Presence router — route to Gebo, Dream, LockIn, Mya, Hunter, Slatt Tool."""
from __future__ import annotations

from typing import Any

from app.modules.common import resolve_status

MODULE_META = {
    "id": "presence_router",
    "name": "Presence Router",
    "surface": "backend",
}

PRESENCES: list[dict[str, str]] = [
    {"id": "gebo", "name": "Gebo", "role": "Primary orchestrator"},
    {"id": "dream", "name": "Dream", "role": "Creative / ideation"},
    {"id": "lockin", "name": "LockIn", "role": "Focus and execution"},
    {"id": "mya", "name": "Mya", "role": "Personal assistant"},
    {"id": "hunter", "name": "Hunter", "role": "Research and discovery"},
    {"id": "slatt_tool", "name": "Slatt Tool", "role": "Tool execution lane"},
]


def _owner_live() -> bool:
    return True


def _production_live() -> bool:
    return True


def status() -> dict[str, Any]:
    return {
        **MODULE_META,
        "status": resolve_status(
            "presence_router",
            production_live=_production_live(),
            owner_live=_owner_live(),
        ),
        "presences": PRESENCES,
        "default_presence": "gebo",
        "env_required": [],
        "notes": "Routes user intent to presence-specific prompts and tools.",
    }


def route(presence_id: str, message: str) -> dict[str, Any]:
    known = {p["id"] for p in PRESENCES}
    target = presence_id if presence_id in known else "gebo"
    return {
        "presence": target,
        "message": message,
        "routed": True,
        "status": resolve_status(
            "presence_router",
            production_live=_production_live(),
            owner_live=_owner_live(),
        ),
    }


def handle_route_stub(presence_id: str, message: str) -> dict[str, Any]:
    return route(presence_id, message)
