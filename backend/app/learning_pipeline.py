"""Gebo learning cycles — orchestrate knowledge collection and evolution hooks."""
from __future__ import annotations

from typing import Any

from app import db, knowledge_collector


def run_learning_cycle() -> dict[str, Any]:
    """One micromini workflow cycle: collect → record evolution event."""
    collection = knowledge_collector.run_full_collection()
    knowledge_status = knowledge_collector.status()

    lesson = (
        f"Learning cycle: ingested OSS/docs/models from catalog; "
        f"knowledge memories now {knowledge_status['knowledge_memory_count']}"
    )
    db.insert_evolution_event(
        source_type="learning_cycle",
        source_id=0,
        lesson=lesson,
        score=75,
        status="completed",
    )

    return {
        "ok": True,
        "collection": collection,
        "knowledge": knowledge_status,
        "lesson": lesson,
    }
