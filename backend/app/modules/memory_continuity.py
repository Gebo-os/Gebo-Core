"""Memory continuity — nodes, recall events, relevance, source trail."""
from __future__ import annotations

import os
from typing import Any

from app import db, memory
from app.modules.common import resolve_status

MODULE_META = {
    "id": "memory_continuity",
    "name": "Memory Continuity",
    "surface": "backend",
}


def _owner_live() -> bool:
    return True


def _production_live() -> bool:
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
    except Exception:
        return False


def status() -> dict[str, Any]:
    pgvector_note = "pgvector extension required for production embeddings"
    return {
        **MODULE_META,
        "status": resolve_status(
            "memory_continuity",
            production_live=_production_live(),
            owner_live=_owner_live(),
        ),
        "local_memory_count": db.count_memories(),
        "message_count": db.count_messages(),
        "delegates_to": ["memory.py", "db.py"],
        "env_required": ["DATABASE_URL"],
        "env_optional": ["SUPABASE_URL"],
        "pgvector_note": pgvector_note,
        "notes": "Owner node uses SQLite; production uses Supabase + pgvector.",
    }


def recall(query: str, limit: int = 8) -> dict[str, Any]:
    recalled = memory.get_relevant_memories(query, limit=limit)
    return {
        "query": query,
        "count": len(recalled),
        "memories": recalled,
        "source": "local_sqlite" if db.count_memories() else "empty",
    }


def handle_recall_event(query: str) -> dict[str, Any]:
    result = recall(query)
    return {
        "event": "recall",
        "query": query,
        "relevance_count": result["count"],
        "status": resolve_status(
            "memory_continuity",
            production_live=_production_live(),
            owner_live=_owner_live(),
        ),
    }


def handle_memory_node_stub(content: str, memory_type: str = "core") -> dict[str, Any]:
    memory_id = db.insert_memory(memory_type, content, "memory_continuity_api")
    return {
        "id": memory_id,
        "ok": True,
        "status": resolve_status(
            "memory_continuity",
            production_live=_production_live(),
            owner_live=_owner_live(),
        ),
    }
