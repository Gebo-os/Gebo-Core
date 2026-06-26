"""Gebo Evolution Loop — behavioral self-improvement above Reflex Engine."""
from __future__ import annotations

from typing import Any

from app import db

UPGRADE_TYPES = frozenset(
    {
        "reflex",
        "tool",
        "agent",
        "memory_rule",
        "ui_improvement",
        "backend_improvement",
        "prompt_improvement",
        "workflow_improvement",
    }
)

UPGRADE_STATUSES = frozenset(
    {"proposed", "approved", "rejected", "completed", "failed"}
)

ACTION_UPGRADE_MAP: dict[str, dict[str, str]] = {
    "write_project_note": {
        "upgrade_type": "reflex",
        "title": "Auto Build Log Reflex",
        "description": (
            "Create a reflex that automatically formats build updates when Bb "
            "mentions progress, bugs, or UI work."
        ),
        "reason": "Bb keeps writing build updates manually — pattern detected.",
    },
    "save_memory": {
        "upgrade_type": "memory_rule",
        "title": "Stronger Memory Capture Rule",
        "description": (
            "Tighten auto-capture keywords and propose memory saves for mission-critical updates."
        ),
        "reason": "Repeated manual memory saves — automate capture rules.",
    },
    "create_plan": {
        "upgrade_type": "workflow_improvement",
        "title": "Plan-to-Action Workflow",
        "description": (
            "Streamline plan creation into a repeatable workflow with follow-up actions."
        ),
        "reason": "Frequent plan actions — workflow can be upgraded.",
    },
    "summarize_recent_messages": {
        "upgrade_type": "reflex",
        "title": "Daily Continuity Reflex Boost",
        "description": (
            "Enhance daily summary reflex to include mission score and next steps."
        ),
        "reason": "Regular continuity summaries — strengthen the reflex.",
    },
    "codex_review": {
        "upgrade_type": "tool",
        "title": "Native Review Tool",
        "description": (
            "Add a native review tool with structured severity output and memory linking."
        ),
        "reason": "Repeated Codex reviews — consider a native tool.",
    },
    "codex_build": {
        "upgrade_type": "agent",
        "title": "Build Specialist Agent",
        "description": (
            "Propose a Build Specialist agent for recurring implementation tasks."
        ),
        "reason": "Repeated build tasks — agent specialization may help.",
    },
}


def clamp_score(value: int) -> int:
    return max(1, min(10, value))


def calculate_total_score(
    mission_value: int,
    speed_score: int,
    risk_score: int,
    approval_score: int,
    memory_impact: int,
    product_impact: int,
    money_impact: int,
) -> int:
    scores = [
        clamp_score(mission_value),
        clamp_score(speed_score),
        clamp_score(risk_score),
        clamp_score(approval_score),
        clamp_score(memory_impact),
        clamp_score(product_impact),
        clamp_score(money_impact),
    ]
    return round(sum(scores) / len(scores))


def build_lesson_from_score(
    action_id: int | None,
    total_score: int,
    notes: str | None,
) -> str:
    action_part = f"Action #{action_id}" if action_id else "System action"
    outcome = (
        "Strong outcome — consider making this a reflex or tool."
        if total_score >= 8
        else "Moderate outcome — refine approach."
        if total_score >= 5
        else "Weak outcome — adjust or reject this pattern."
    )
    lines = [f"{action_part} scored {total_score}/10.", outcome]
    if notes:
        lines.append(f"Notes: {notes}")
    return "\n".join(lines)


def score_action(
    action_id: int,
    mission_value: int,
    speed_score: int,
    risk_score: int,
    approval_score: int,
    memory_impact: int,
    product_impact: int,
    money_impact: int,
    notes: str | None = None,
) -> dict[str, Any]:
    action = db.get_action(action_id)
    if not action:
        raise ValueError("Action not found")

    total = calculate_total_score(
        mission_value,
        speed_score,
        risk_score,
        approval_score,
        memory_impact,
        product_impact,
        money_impact,
    )
    score_id = db.insert_autonomy_score(
        action_id=action_id,
        mission_value=clamp_score(mission_value),
        speed_score=clamp_score(speed_score),
        risk_score=clamp_score(risk_score),
        approval_score=clamp_score(approval_score),
        memory_impact=clamp_score(memory_impact),
        product_impact=clamp_score(product_impact),
        money_impact=clamp_score(money_impact),
        total_score=total,
        notes=notes,
    )
    lesson = build_lesson_from_score(action_id, total, notes)
    recommended = None
    if total >= 8:
        recommended = "Consider reflex or tool upgrade for this action pattern."
    elif total <= 4:
        recommended = "Deprioritize or redesign this action pattern."

    event_id = db.insert_evolution_event(
        source_type="action",
        source_id=action_id,
        lesson=lesson,
        score=total,
        recommended_upgrade=recommended,
        status="scored",
    )

    db.insert_memory(
        "system",
        f"[Evolution Loop]\n{lesson}",
        "evolution",
    )

    analyze_repeat_patterns()

    return {
        "score_id": score_id,
        "event_id": event_id,
        "total_score": total,
        "lesson": lesson,
    }


def suggest_upgrade(
    upgrade_type: str,
    title: str,
    description: str,
    reason: str,
) -> dict[str, Any]:
    if upgrade_type not in UPGRADE_TYPES:
        raise ValueError(f"Invalid upgrade_type: {upgrade_type}")
    upgrade_id = db.insert_upgrade_suggestion(
        upgrade_type=upgrade_type,
        title=title,
        description=description,
        reason=reason,
        status="proposed",
    )
    db.insert_evolution_event(
        source_type="upgrade",
        source_id=upgrade_id,
        lesson=f"Upgrade suggested: {title}. {reason}",
        score=0,
        recommended_upgrade=upgrade_type,
        status="proposed",
    )
    return {"id": upgrade_id, "status": "proposed"}


def approve_upgrade(upgrade_id: int) -> dict[str, Any]:
    upgrade = db.get_upgrade_suggestion(upgrade_id)
    if not upgrade:
        raise ValueError("Upgrade not found")
    if upgrade["status"] != "proposed":
        raise ValueError("Only proposed upgrades can be approved")

    action_id = db.insert_action(
        "create_plan",
        f"Evolution: {upgrade['title']}",
        upgrade["description"],
        {
            "topic": f"{upgrade['title']}\n\n{upgrade['reason']}",
            "upgrade_id": upgrade_id,
            "upgrade_type": upgrade["upgrade_type"],
            "source": "evolution_loop",
        },
        "proposed",
    )
    db.update_upgrade_status(upgrade_id, "approved", action_id)
    db.insert_evolution_event(
        source_type="upgrade",
        source_id=upgrade_id,
        lesson=f"Upgrade approved: {upgrade['title']}. Build action #{action_id} proposed.",
        score=0,
        recommended_upgrade=upgrade["upgrade_type"],
        status="approved",
    )
    return {"id": upgrade_id, "status": "approved", "proposed_action_id": action_id}


def reject_upgrade(upgrade_id: int) -> dict[str, Any]:
    upgrade = db.get_upgrade_suggestion(upgrade_id)
    if not upgrade:
        raise ValueError("Upgrade not found")
    if upgrade["status"] != "proposed":
        raise ValueError("Only proposed upgrades can be rejected")
    db.update_upgrade_status(upgrade_id, "rejected")
    db.insert_evolution_event(
        source_type="upgrade",
        source_id=upgrade_id,
        lesson=f"Upgrade rejected: {upgrade['title']}.",
        score=0,
        recommended_upgrade=None,
        status="rejected",
    )
    return {"id": upgrade_id, "status": "rejected"}


def analyze_repeat_patterns(min_count: int = 3) -> list[int]:
    """Suggest upgrades when action types repeat. Returns new suggestion ids."""
    created: list[int] = []
    for row in db.get_completed_actions_by_type(min_count):
        action_type = row["action_type"]
        template = ACTION_UPGRADE_MAP.get(action_type)
        if not template:
            continue
        if db.upgrade_suggestion_exists(template["title"]):
            continue
        result = suggest_upgrade(
            upgrade_type=template["upgrade_type"],
            title=template["title"],
            description=template["description"],
            reason=f"{template['reason']} ({row['cnt']} completed).",
        )
        created.append(result["id"])
    return created


def record_action_completion(action_id: int, final_status: str, result: dict) -> None:
    """Called when an action finishes — records outcome for later scoring."""
    action = db.get_action(action_id)
    if not action:
        return
    msg = result.get("message") or result.get("error") or final_status
    lesson = (
        f"Action completed: {action['title']} ({action['action_type']}).\n"
        f"Status: {final_status}.\n"
        f"Result: {msg}\n"
        "Score this outcome on the Evolution page to teach Gebo what worked."
    )
    db.insert_evolution_event(
        source_type="action",
        source_id=action_id,
        lesson=lesson,
        score=0,
        recommended_upgrade=None,
        status="proposed",
    )
    analyze_repeat_patterns()


def get_status() -> dict[str, Any]:
    avg = db.get_average_autonomy_score()
    proposed = db.get_upgrade_suggestions(status="proposed", limit=1)
    latest = db.get_latest_evolution_event()
    return {
        "average_autonomy_score": avg,
        "total_evolution_events": db.count_evolution_events(),
        "proposed_upgrades": db.count_upgrades_by_status("proposed"),
        "approved_upgrades": db.count_upgrades_by_status("approved"),
        "completed_upgrades": db.count_upgrades_by_status("completed"),
        "rejected_upgrades": db.count_upgrades_by_status("rejected"),
        "latest_lesson": latest["lesson"] if latest else None,
        "top_recommended_upgrade": proposed[0] if proposed else None,
    }
