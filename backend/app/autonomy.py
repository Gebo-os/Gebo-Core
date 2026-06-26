import json
import re
import threading
from typing import Any

from app import codex_client, db

TOOL_REGISTRY = {
    "save_memory": {
        "description": "Save a memory to the database.",
        "safe": True,
        "background": False,
    },
    "summarize_recent_messages": {
        "description": "Summarize recent messages into a memory note.",
        "safe": True,
        "background": False,
    },
    "create_plan": {
        "description": "Create a project plan and save it as an action result.",
        "safe": True,
        "background": False,
    },
    "write_project_note": {
        "description": "Save a project note into memory.",
        "safe": True,
        "background": False,
    },
    "export_memory": {
        "description": "Prepare export link only. Do not download automatically.",
        "safe": True,
        "background": False,
    },
    "codex_review": {
        "description": "Run a read-only Codex code review of the project.",
        "safe": True,
        "background": True,
    },
    "codex_build": {
        "description": "Run Codex to implement a coding task in the project (writes files).",
        "safe": False,
        "background": True,
    },
}


def is_background_tool(action_type: str) -> bool:
    return bool(TOOL_REGISTRY.get(action_type, {}).get("background"))


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
        # Consent ON → handle_remember_direct saves immediately; skip duplicate proposal.
        # Do not return early — other intents (plan, codex, etc.) may still apply.
        if not consent:
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

    if codex_client.is_available():
        if re.search(r"\b(codex\s+)?(review|audit)\b", normalized):
            proposals.append(
                {
                    "action_type": "codex_review",
                    "title": "Codex code review",
                    "description": "Run a read-only Codex review of the project.",
                    "payload_json": {"prompt": user_message},
                }
            )
        if re.search(
            r"\b(build|code|implement|fix|refactor|add)\b.*\b(with\s+codex|codex|feature|function|endpoint|component|bug)\b",
            normalized,
        ) or re.search(r"\buse\s+codex\b", normalized):
            proposals.append(
                {
                    "action_type": "codex_build",
                    "title": "Codex build task",
                    "description": "Run Codex to implement this in the project (writes files). Requires approval.",
                    "payload_json": {"prompt": user_message},
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

    if action_type == "codex_review":
        prompt = payload.get("prompt") or (
            "Review this project for correctness, security, and quality. "
            "List findings by severity with file paths and fixes."
        )
        result = codex_client.run_task(prompt, mode="review")
        if result.get("ok") and result.get("result"):
            db.insert_memory("build_log", f"[codex review]\n{result['result']}"[:12000], "codex")
        return result

    if action_type == "codex_build":
        prompt = payload.get("prompt")
        if not prompt:
            return {"ok": False, "error": "codex_build requires a prompt"}
        result = codex_client.run_task(prompt, mode="build")
        if result.get("ok") and result.get("result"):
            db.insert_memory("build_log", f"[codex build]\n{result['result']}"[:12000], "codex")
        return result

    raise ValueError(f"Tool not implemented: {action_type}")


def _background_run(action_id: int, action_type: str, payload: dict[str, Any]) -> None:
    try:
        result = execute_tool(action_type, payload)
        status = "completed" if result.get("ok", True) else "failed"
        db.update_action_result(action_id, status, result)
    except Exception as exc:  # noqa: BLE001
        db.update_action_result(action_id, "failed", {"ok": False, "error": str(exc)})


def run_action(action_id: int) -> dict[str, Any]:
    action = db.claim_approved_action(action_id)
    if not action:
        raise ValueError("Action not found or not approved")

    action_type = action["action_type"]
    payload = json.loads(action["payload_json"] or "{}")

    if is_background_tool(action_type):
        thread = threading.Thread(
            target=_background_run,
            args=(action_id, action_type, payload),
            daemon=True,
        )
        thread.start()
        return {
            "ok": True,
            "status": "running",
            "message": "Codex task started. Results will appear when it finishes.",
        }

    try:
        result = execute_tool(action_type, payload)
        status = "completed" if result.get("ok", True) else "failed"
        db.update_action_result(action_id, status, result)
        return result
    except Exception as exc:
        db.update_action_result(action_id, "failed", {"ok": False, "error": str(exc)})
        raise
