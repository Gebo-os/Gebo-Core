"""Private Gebo system hub — integrates knowledge, CLIs, and connectors in backend only."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app import (
    cli_registry,
    integrations_registry,
    knowledge_collector,
    learning_pipeline,
    production_security,
    release_stack,
)
from app.modules import MODULE_REGISTRY

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
KNOWLEDGE_DIR = PROJECT_ROOT / "backend" / "data" / "knowledge"
CACHE_DIR = KNOWLEDGE_DIR / "cache"
MANIFEST_PATH = KNOWLEDGE_DIR / "gebo-system-manifest.json"

GEBO_SYSTEM_LAYERS = [
    {
        "id": "brain",
        "name": "Local Brain",
        "components": ["ollama", "gebo-custom", "memory", "wiki"],
        "role": "Inference and recall — always local-first",
    },
    {
        "id": "autonomy",
        "name": "Autonomy Core",
        "components": ["actions", "reflexes", "evolution", "codex_lane"],
        "role": "Approval-gated tools and parallel agents",
    },
    {
        "id": "knowledge",
        "name": "Knowledge Fabric",
        "components": ["catalog", "web_cache", "private_docs", "google_ecosystem"],
        "role": "Collected docs and OSS patterns in SQLite memory",
    },
    {
        "id": "integrations",
        "name": "Integration Plane",
        "components": ["learnable_docs", "connectors", "firebase", "gcp"],
        "role": "Study public docs; wire credentials when ready",
    },
    {
        "id": "console",
        "name": "Living Console",
        "components": ["nextjs", "gebo_os_shell", "gebo_client_sdk"],
        "role": "Owner UI and future consumer app shell",
    },
    {
        "id": "release_plane",
        "name": "Official Release Plane",
        "components": list(MODULE_REGISTRY.keys()),
        "role": "Supabase + Vercel V1 modules — identity, memory, AI, docs, billing",
    },
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def private_status() -> dict[str, Any]:
    """Backend-only system snapshot — not for public consumer UI."""
    knowledge = knowledge_collector.status()
    integrations = integrations_registry.status()
    clis = cli_registry.status()
    cache_files = list(CACHE_DIR.glob("*.txt")) if CACHE_DIR.is_dir() else []
    manifest = load_manifest()
    return {
        "system": "Gebo OS Private",
        "built_at": manifest.get("built_at"),
        "layers": GEBO_SYSTEM_LAYERS,
        "knowledge": knowledge,
        "integrations": {
            "total": integrations["total"],
            "learnable": integrations["learnable"],
            "connectors": integrations["connectors"],
            "ready": integrations["ready"],
        },
        "clis": {"available": clis["available"], "total": clis["total"]},
        "doc_cache_count": len(cache_files),
        "doc_cache_dir": str(CACHE_DIR),
        "manifest_version": manifest.get("version", 0),
        "production_readiness": production_security.readiness(),
        "v1_readiness": release_stack.v1_readiness(),
        "release_modules": list(MODULE_REGISTRY.keys()),
    }


def load_manifest() -> dict[str, Any]:
    if not MANIFEST_PATH.is_file():
        return {"version": 0, "built_at": None, "last_collection": None}
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def save_manifest(collection_result: dict[str, Any]) -> dict[str, Any]:
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest()
    manifest.update(
        {
            "version": int(manifest.get("version", 0)) + 1,
            "built_at": _utc_now(),
            "last_collection": collection_result,
            "layers": GEBO_SYSTEM_LAYERS,
            "integration_count": integrations_registry.status()["total"],
            "knowledge_memories": knowledge_collector.status()["knowledge_memory_count"],
        }
    )
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def build_system() -> dict[str, Any]:
    """Full private build: collect docs → cache → memory → evolution → manifest."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    collection = knowledge_collector.run_full_collection()
    cycle = learning_pipeline.run_learning_cycle()
    manifest = save_manifest(collection)
    return {
        "ok": True,
        "collection": collection,
        "learning_cycle": cycle,
        "manifest": {
            "version": manifest["version"],
            "built_at": manifest["built_at"],
            "knowledge_memories": manifest["knowledge_memories"],
        },
        "status": private_status(),
    }
