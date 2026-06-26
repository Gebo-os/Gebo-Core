"""Gebo Reflex Engine — memory-aware pattern → proposal → approval automation."""
from __future__ import annotations

import json
import re
from typing import Any

from app import autonomy, db

DEFAULT_REFLEXES: list[dict[str, Any]] = [
    {
        "name": "Memory Capture Reflex",
        "description": (
            "When Bb says something important about Gebo, goals, career, business, "
            "tools, architecture, or personal direction, propose saving it as memory."
        ),
        "trigger_type": "keyword",
        "trigger_pattern": (
            r"remember|my goal|i want|gebo should|don't forget|dont forget|"
            r"important|architecture|mission"
        ),
        "action_type": "save_memory",
        "approval_required": 1,
    },
    {
        "name": "Build Log Reflex",
        "description": (
            "When Bb mentions app progress, bugs, code, Cursor, Codex, backend, "
            "frontend, memory, or UI, create a build log and propose the next task."
        ),
        "trigger_type": "keyword",
        "trigger_pattern": (
            r"i fixed|it broke|cursor made|backend failed|frontend|ui|bug|codex|"
            r"deploy|build progress|still looks weak|still needs"
        ),
        "action_type": "write_project_note",
        "approval_required": 1,
    },
    {
        "name": "Mission Drift Reflex",
        "description": (
            "When Bb switches to a low-priority tangent during an active mission, "
            "warn and suggest parking the idea."
        ),
        "trigger_type": "keyword",
        "trigger_pattern": (
            r"what about buying|new laptop|hardware|camera|side project|"
            r"random idea|instead let's|maybe we should try"
        ),
        "action_type": "write_project_note",
        "approval_required": 1,
    },
    {
        "name": "Action Queue Reflex",
        "description": (
            "When Bb asks Gebo to build, change, fix, or create something, "
            "turn it into a proposed action instead of silently executing."
        ),
        "trigger_type": "keyword",
        "trigger_pattern": (
            r"build this|change this|add this|fix this|implement|refactor|"
            r"create a|update the|make the"
        ),
        "action_type": "create_plan",
        "approval_required": 1,
    },
    {
        "name": "Daily Continuity Reflex",
        "description": (
            "When Bb gives a day summary or build update, compress into continuity memory."
        ),
        "trigger_type": "keyword",
        "trigger_pattern": (
            r"today i|update:|build log|end of day|summary of today|what changed"
        ),
        "action_type": "summarize_recent_messages",
        "approval_required": 1,
    },
    {
        "name": "Presence Activation Reflex",
        "description": (
            "Suggest the right Presence when Bb signals need for focus, planning, "
            "wording, or worldbuilding."
        ),
        "trigger_type": "keyword",
        "trigger_pattern": (
            r"need discipline|need planning|help me focus|wording|story|worldbuilding|"
            r"lock in|creative direction"
        ),
        "action_type": "write_project_note",
        "approval_required": 1,
    },
]

PRESENCE_HINTS = {
    "need discipline": "LockIn — focus and follow-through",
    "help me focus": "LockIn — focus and follow-through",
    "lock in": "LockIn — focus and follow-through",
    "need planning": "Sleep — planning and structure",
    "wording": "Verbal Creator — wording and voice",
    "story": "Hunter — story and worldbuilding",
    "worldbuilding": "Hunter — story and worldbuilding",
    "creative direction": "Dream — vision and exploration",
}


def seed_default_reflexes() -> None:
    existing = db.count_reflexes()
    if existing > 0:
        return
    for reflex in DEFAULT_REFLEXES:
        db.insert_reflex(
            name=reflex["name"],
            description=reflex["description"],
            trigger_type=reflex["trigger_type"],
            trigger_pattern=reflex["trigger_pattern"],
            action_type=reflex["action_type"],
            approval_required=bool(reflex["approval_required"]),
            enabled=True,
        )


def _matches_pattern(pattern: str, text: str) -> bool:
    normalized = text.lower().strip()
    try:
        return bool(re.search(pattern, normalized, re.IGNORECASE))
    except re.error:
        return False


def _presence_suggestion(message: str) -> str:
    lower = message.lower()
    for key, hint in PRESENCE_HINTS.items():
        if key in lower:
            return hint
    return "Gebo — memory, strategy, and continuity"


def build_proposals(reflex: dict, user_message: str) -> list[dict[str, Any]]:
    """Build one or more action proposals for a matched reflex."""
    name = reflex["name"]
    base_payload: dict[str, Any] = {
        "reflex_id": reflex["id"],
        "reflex_name": name,
        "source": "reflex_engine",
    }

    if name == "Memory Capture Reflex":
        return [
            {
                "action_type": "save_memory",
                "title": f"Reflex: Save memory ({name})",
                "description": reflex["description"],
                "payload_json": {
                    **base_payload,
                    "memory_type": "core",
                    "content": user_message,
                },
            }
        ]

    if name == "Build Log Reflex":
        return [
            {
                "action_type": "write_project_note",
                "title": "Reflex: Save build log",
                "description": "Save this progress update as a build log memory.",
                "payload_json": {
                    **base_payload,
                    "memory_type": "build_log",
                    "content": f"Build Log:\n{user_message}",
                },
            },
            {
                "action_type": "create_plan",
                "title": "Reflex: Propose follow-up task",
                "description": "Create a pending plan for the next improvement task.",
                "payload_json": {
                    **base_payload,
                    "topic": f"Follow-up: {user_message[:500]}",
                },
            },
        ]

    if name == "Mission Drift Reflex":
        return [
            {
                "action_type": "write_project_note",
                "title": "Reflex: Mission drift warning",
                "description": "Park this tangent and refocus on Gebo Core private launch.",
                "payload_json": {
                    **base_payload,
                    "memory_type": "system",
                    "content": (
                        "Mission drift detected.\n"
                        f"Tangential topic: {user_message}\n"
                        "This is parked. Current mission is Gebo Core private launch."
                    ),
                },
            }
        ]

    if name == "Action Queue Reflex":
        return [
            {
                "action_type": "create_plan",
                "title": "Reflex: Queue build task",
                "description": "Turn this request into a proposed action plan.",
                "payload_json": {
                    **base_payload,
                    "topic": user_message,
                },
            }
        ]

    if name == "Daily Continuity Reflex":
        return [
            {
                "action_type": "summarize_recent_messages",
                "title": "Reflex: Daily continuity summary",
                "description": (
                    "Summarize what changed, what matters, what broke, and next mission."
                ),
                "payload_json": {**base_payload, "limit": 30},
            }
        ]

    if name == "Presence Activation Reflex":
        presence = _presence_suggestion(user_message)
        return [
            {
                "action_type": "write_project_note",
                "title": "Reflex: Presence suggestion",
                "description": f"Suggest activating {presence.split(' — ')[0]}.",
                "payload_json": {
                    **base_payload,
                    "memory_type": "presence",
                    "content": (
                        f"Presence Reflex:\nSuggested presence: {presence}\n"
                        f"Context: {user_message}"
                    ),
                },
            }
        ]

    action_type = reflex["action_type"]
    if not autonomy.is_valid_action_type(action_type):
        return []

    return [
        {
            "action_type": action_type,
            "title": f"Reflex: {reflex['name']}",
            "description": reflex["description"],
            "payload_json": {**base_payload, "content": user_message},
        }
    ]


def detect_and_propose(
    user_message: str,
    existing_action_types: set[str] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Match enabled reflexes and create proposed actions + reflex events.
    Returns (detected_reflexes, proposed_action_summaries).
    """
    existing_action_types = existing_action_types or set()
    detected: list[dict[str, Any]] = []
    proposals: list[dict[str, Any]] = []

    for reflex in db.get_reflexes(enabled_only=True):
        if not _matches_pattern(reflex["trigger_pattern"], user_message):
            continue

        intent_list = build_proposals(reflex, user_message)
        event_action_id: int | None = None
        event_result = "proposed"
        reflex_proposal_count = 0

        for intent in intent_list:
            if intent["action_type"] in existing_action_types:
                continue
            if not autonomy.is_valid_action_type(intent["action_type"]):
                continue

            approval_required = bool(reflex.get("approval_required", 1))
            status = "proposed" if approval_required else "approved"

            action_id = db.insert_action(
                intent["action_type"],
                intent["title"],
                intent["description"],
                intent["payload_json"],
                status,
            )
            event_action_id = action_id
            existing_action_types.add(intent["action_type"])

            proposals.append(
                {
                    "id": action_id,
                    "action_type": intent["action_type"],
                    "title": intent["title"],
                    "description": intent["description"],
                    "status": status,
                    "reflex_id": reflex["id"],
                    "reflex_name": reflex["name"],
                }
            )
            reflex_proposal_count += 1

            if not approval_required:
                try:
                    autonomy.run_action(action_id)
                    event_result = "executed"
                except Exception as exc:  # noqa: BLE001
                    event_result = f"failed: {exc}"

        db.insert_reflex_event(
            reflex_id=reflex["id"],
            input_text=user_message[:2000],
            proposed_action_id=event_action_id,
            result=event_result if reflex_proposal_count else "matched_no_action",
        )

        detected.append(
            {
                "reflex_id": reflex["id"],
                "name": reflex["name"],
                "description": reflex["description"],
                "trigger_pattern": reflex["trigger_pattern"],
                "action_type": reflex["action_type"],
                "approval_required": bool(reflex.get("approval_required", 1)),
                "proposals_created": reflex_proposal_count,
            }
        )

    return detected, proposals
