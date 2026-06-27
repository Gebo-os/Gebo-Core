"""Single-call bootstrap for Gebo Living Console and future consumer apps."""
from __future__ import annotations

import os
from typing import Any

from app import agent_runtime, cli_registry, codex_client, db, integrations_registry, knowledge_collector, ollama_client, wiki_client


GEBO_VERSION = os.getenv("GEBO_VERSION", "0.9.0")


def build_bootstrap() -> dict[str, Any]:
    runtime = agent_runtime.get_runtime_status()
    network_internet = db.get_internet_access()
    return {
        "version": GEBO_VERSION,
        "app": "Gebo Core Private",
        "health": {
            "ok": True,
            "app": "Gebo Core Private",
            "agent_runtime_healthy": runtime["healthy"],
        },
        "status": {
            "app": "Gebo Core Private",
            "model": ollama_client.get_model(),
            "consent": db.get_consent(),
            "memory_count": db.count_memories(),
            "message_count": db.count_messages(),
            "proposed_action_count": db.count_actions_by_status("proposed"),
            "approved_action_count": db.count_actions_by_status("approved"),
            "completed_action_count": db.count_actions_by_status("completed"),
        },
        "network": None,  # filled by main._network_settings_payload()
        "codex": codex_client.status(),
        "wiki": wiki_client.status(),
        "agent_runtime": runtime,
        "capabilities": {
            "chat": True,
            "memory": True,
            "actions": True,
            "codex": codex_client.is_available(),
            "wiki": wiki_client.is_enabled(),
            "reflexes": True,
            "evolution": True,
            "network_lan": network_internet,
            "local_model": True,
            "learning": True,
            "integrations": integrations_registry.status()["total"],
            "clis_available": cli_registry.status()["available"],
            "knowledge_memories": knowledge_collector.status()["knowledge_memory_count"],
        },
    }
