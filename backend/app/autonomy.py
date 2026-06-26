import json
import re
from typing import Any

from app import db

TOOL_REGISTRY = {
    "save_memory": {
        "description": "Save a memory to the database.",
        "safe": True,
    },
    "summarize_recent_messages": {
        "description": "Summarize recent messages into a memory note.",
        "safe": True,
    },
    "create_plan": {
        "description": "Create a project plan and save it as an action result.",
        "safe": True,
    },
    "write_project_note": {
        "description": "Save a project note into memory.",
        "safe": True,
    },
    "export_memory": {
        "description": "Prepare export link only. Do not download automatically.",
        "safe": True,
    },
}


def is_valid_action_type(action_type: str) -> bool:
    return action_type in TOOL_REGISTRY


def detect_action_intents(user_message: str, consent: bool) -> list[dict[str, Any]]:
    """Detect user intents and return action proposals (not yet saved)."""
    normalized = user_message.lower().strip()
    proposals: list[dict[str, Any]] = []

    remember_patterns = [
        r"remember this",
        r"remember that",
        r"save this",
        r"don't forget",
        r"dont forget",
    ]
    if any(re.search(p, normalized) for p in remember_patterns):
        if consent:
            return proposals
        proposals.append(
            {
                "action_type": "save_memory",
                "title": "Save memory",
                "description": "Save the user's statement to permanent memory.",
                "payload_json": {
                    "memory_type": "manual",
                    "content": user_message,
                    "source": "chat_proposal",
                },
            }
        )

    if re.search(r"\b(make|create|build)\s+(a\s+)?plan\b", normalized):
        proposals.append(
            {
                "action_type": "create_plan",
                "title": "Create project plan",
                "description": "Generate a project plan based on recent context.",
                "payload_json": {"topic": user_message},
            }
        )

    summarize_patterns = [
        r"summarize",
        r"summary of",
        r"what we built",
        r"recap",
    ]
    if any(re.search(p, normalized) for p in summarize_patterns):
        proposals.append(
            {
                "action_type": "summarize_recent_messages",
                "title": "Summarize recent messages",
                "description": "Summarize recent conversation into a memory note.",
                "payload_json": {"limit": 30},
            }
        )

    if re.search(r"export\s*(memory|memories|data)?", normalized):
        proposals.append(
            {
                "action_type": "export_memory",
                "title": "Export memory",
                "description": "Prepare memory export link for download.",
                "payload_json": {},
            }
        )

    if re.search(r"(project\s+note|write\s+(a\s+)?note)", normalized):
        proposals.append(
            {
                "action_type": "write_project_note",
                "title": "Write project note",
                "description": "Save a project note to memory.",
                "payload_json": {"content": user_message},
            }
        )

    return proposals


def handle_remember_direct(user_message: str, consent: bool) -> int | None:
    normalized = user_message.lower().strip()
    remember_patterns = [
        r"remember this",
        r"remember that",
        r"save this",
    ]
    if consent and any(re.search(p, normalized) for p in remember_patterns):
        return db.insert_memory("manual", user_message, "chat_direct")
    return None


def _summarize_messages(limit: int = 30) -> str:
    messages = db.get_recent_messages(limit)
    if not messages:
        return "No messages to summarize."
    lines = [f"[{m['role']}] {m['content']}" for m in messages]
    summary = "Conversation summary:\n" + "\n".join(lines[-20:])
    if len(summary) > 2000:
        summary = summary[:2000] + "..."
    return summary


def execute_tool(action_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    if action_type not in TOOL_REGISTRY:
        raise ValueError(f"Unknown action type: {action_type}")

    if action_type == "save_memory":
        memory_id = db.insert_memory(
            payload.get("memory_type", "manual"),
            payload.get("content", ""),
            payload.get("source", "action"),
        )
        return {"ok": True, "memory_id": memory_id, "message": "Memory saved."}

    if action_type == "summarize_recent_messages":
        limit = int(payload.get("limit", 30))
        summary = _summarize_messages(limit)
        memory_id = db.insert_memory("summary", summary, "action")
        return {
            "ok": True,
            "memory_id": memory_id,
            "summary": summary,
            "message": "Summary saved to memory.",
        }

    if action_type == "create_plan":
        topic = payload.get("topic", "General project")
        messages = db.get_recent_messages(20)
        memories = db.get_memories(10)
        plan_lines = [
            f"# Project Plan: {topic}",
            "",
            "## Context from memory",
        ]
        for m in memories:
            plan_lines.append(f"- {m['content'][:200]}")
        plan_lines.extend(["", "## Recent discussion"])
        for msg in messages[-10:]:
            plan_lines.append(f"- [{msg['role']}] {msg['content'][:150]}")
        plan_lines.extend(
            [
                "",
                "## Proposed steps",
                "1. Clarify scope and success criteria",
                "2. Identify dependencies and blockers",
                "3. Break work into milestones",
                "4. Execute with memory logging",
                "5. Review and iterate",
            ]
        )
        plan_text = "\n".join(plan_lines)
        memory_id = db.insert_memory("plan", plan_text, "action")
        return {
            "ok": True,
            "memory_id": memory_id,
            "plan": plan_text,
            "message": "Plan created and saved to memory.",
        }

    if action_type == "write_project_note":
        content = payload.get("content", "")
        memory_id = db.insert_memory("project_note", content, "action")
        return {"ok": True, "memory_id": memory_id, "message": "Project note saved."}

    if action_type == "export_memory":
        return {
            "ok": True,
            "export_url": "/memory/export",
            "message": "Export ready. Use GET /memory/export to download.",
        }

    raise ValueError(f"Tool not implemented: {action_type}")


def run_action(action_id: int) -> dict[str, Any]:
    action = db.claim_approved_action(action_id)
    if not action:
        raise ValueError("Action not found or not approved")

    try:
        payload = json.loads(action["payload_json"] or "{}")
        result = execute_tool(action["action_type"], payload)
        db.update_action_result(action_id, "completed", result)
        return result
    except Exception as exc:
        db.update_action_result(action_id, "failed", {"ok": False, "error": str(exc)})
        raise
