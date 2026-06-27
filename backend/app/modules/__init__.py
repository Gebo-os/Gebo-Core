"""Native Gebo V1 backend modules — official tool integrations."""
from __future__ import annotations

from typing import Any

from app.modules.common import resolve_status
from app.modules import (
    admin_console,
    ai_gateway,
    billing_usage,
    document_intelligence,
    identity_core,
    memory_continuity,
    presence_router,
    security_command,
)

MODULE_REGISTRY: dict[str, Any] = {
    "identity_core": identity_core,
    "memory_continuity": memory_continuity,
    "presence_router": presence_router,
    "ai_gateway": ai_gateway,
    "document_intelligence": document_intelligence,
    "security_command": security_command,
    "billing_usage": billing_usage,
    "admin_console": admin_console,
}


def all_module_statuses() -> list[dict[str, Any]]:
    return [mod.status() for mod in MODULE_REGISTRY.values()]


def module_status(module_id: str) -> dict[str, Any] | None:
    mod = MODULE_REGISTRY.get(module_id)
    return mod.status() if mod else None
