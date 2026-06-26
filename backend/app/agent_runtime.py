"""Gebo internal agent runtime — 24/7 parallel heartbeat supervisor.

Active registry agents tick in parallel via a thread pool. A Codex lane runs
alongside agents each cycle (status ping; heavy tasks stay approval-gated).
"""
from __future__ import annotations

import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from app import agents, codex_client, db, ollama_client

TICK_INTERVAL_SEC = 30
MAX_PARALLEL_WORKERS = 12
CODex_AUDIT_EVERY_CYCLES = 20  # ~10 min at 30s ticks


def _testing() -> bool:
    return os.getenv("GEBO_TESTING", "").lower() == "true"

_lock = threading.Lock()
_running = False
_thread: threading.Thread | None = None
_executor: ThreadPoolExecutor | None = None
_states: dict[str, dict[str, Any]] = {}
_codex_lane: dict[str, Any] = {
    "available": False,
    "enabled": False,
    "version": None,
    "status": "idle",
    "message": "not started",
    "cycles": 0,
    "last_tick": None,
    "parallel_with_agents": True,
}
_cycle_count = 0
_started_at: str | None = None


def _tick_agent(agent: dict) -> None:
    agent_id = agent["id"]
    message = "idle"
    status = "ok"

    try:
        if agent_id == "memory_engineer":
            count = db.count_memories()
            message = f"memory scan: {count} entries"
        elif agent_id == "security_privacy":
            consent = db.get_consent()
            internet = db.get_internet_access()
            message = f"consent={'on' if consent else 'off'} · network={'open' if internet else 'local'}"
        elif agent_id == "autonomy_engineer":
            proposed = db.count_actions_by_status("proposed")
            approved = db.count_actions_by_status("approved")
            message = f"queue: {proposed} proposed · {approved} approved"
        elif agent_id == "fullstack_builder":
            codex_ok = _codex_lane.get("available")
            message = (
                f"stack: FastAPI + Next.js · codex={'ready' if codex_ok else 'offline'}"
            )
        elif agent_id == "product_architect":
            message = "architecture watch: Owner NODE V0 · Pulse command center"
        elif agent_id == "sleep_project_manager":
            message = "continuity watch: mission alignment"
        elif agent_id == "ux_ui_designer":
            message = "console UX: Gebo OS command center on Pulse"
        elif agent_id == "qa_bug_hunter":
            codex_st = _codex_lane.get("status", "idle")
            message = f"health patrol · codex lane: {codex_st}"
        elif agent_id == "local_model_engineer":
            model = ollama_client.get_model()
            message = f"model route: {model}"
        else:
            message = "standby"
    except Exception as exc:  # noqa: BLE001
        status = "error"
        message = str(exc)[:200]

    with _lock:
        prev = _states.get(agent_id, {})
        _states[agent_id] = {
            "agent_id": agent_id,
            "name": agent["name"],
            "category": agent["category"],
            "status": status,
            "message": message,
            "cycles": prev.get("cycles", 0) + 1,
            "last_tick": db.utc_now(),
            "tier": agent.get("tier", "v0"),
            "registry_status": agent.get("status", "active"),
        }


def _tick_codex_lane(run_light_audit: bool = False) -> None:
    """Codex lane — runs parallel to agent ticks (status always; audit rarely)."""
    status = "ok"
    message = "codex idle"
    audit_result: dict[str, Any] | None = None
    info: dict[str, Any] = {"available": False, "enabled": False, "version": None}

    try:
        info = codex_client.status()
        if not info.get("available"):
            status = "offline"
            message = "codex CLI not found"
        elif run_light_audit:
            audit_result = codex_client.run_task(
                "Quick health check: list top 3 code quality observations only. "
                "No file changes. One paragraph max.",
                mode="review",
            )
            if audit_result.get("ok"):
                status = "audit_ok"
                message = f"parallel audit · {audit_result.get('elapsed_sec', 0)}s"
            else:
                status = "audit_failed"
                message = (audit_result.get("error") or "audit failed")[:120]
        else:
            message = f"codex {info.get('version') or 'ready'} · workdir active"
    except Exception as exc:  # noqa: BLE001
        status = "error"
        message = str(exc)[:200]

    with _lock:
        prev_cycles = _codex_lane.get("cycles", 0)
        _codex_lane.update(
            {
                "available": bool(info.get("available")),
                "enabled": bool(info.get("enabled")),
                "version": info.get("version"),
                "status": status,
                "message": message,
                "cycles": prev_cycles + 1,
                "last_tick": db.utc_now(),
                "parallel_with_agents": True,
                "last_audit_ok": audit_result.get("ok") if audit_result else None,
            }
        )


def _run_parallel_cycle() -> None:
    global _cycle_count
    active = [a for a in agents.get_agents() if a.get("status") == "active"]
    run_audit = False
    with _lock:
        _cycle_count += 1
        run_audit = (
            not _testing()
            and _cycle_count % CODex_AUDIT_EVERY_CYCLES == 0
            and codex_client.is_available()
        )

    if not _executor:
        return

    futures = [_executor.submit(_tick_agent, agent) for agent in active]
    if codex_client.is_available() or _codex_lane.get("cycles", 0) == 0:
        futures.append(_executor.submit(_tick_codex_lane, run_audit))

    for future in as_completed(futures):
        try:
            future.result()
        except Exception:  # noqa: BLE001
            pass


def _loop() -> None:
    while _running:
        _run_parallel_cycle()
        time.sleep(TICK_INTERVAL_SEC)


def start() -> None:
    global _running, _thread, _started_at, _executor
    with _lock:
        if _running:
            return
        _running = True
        _started_at = db.utc_now()
        for agent in agents.get_agents():
            if agent.get("status") == "active":
                _states.setdefault(
                    agent["id"],
                    {
                        "agent_id": agent["id"],
                        "name": agent["name"],
                        "category": agent["category"],
                        "status": "starting",
                        "message": "initializing",
                        "cycles": 0,
                        "last_tick": _started_at,
                        "tier": agent.get("tier", "v0"),
                        "registry_status": agent.get("status", "active"),
                    },
                )
    _executor = ThreadPoolExecutor(
        max_workers=MAX_PARALLEL_WORKERS,
        thread_name_prefix="gebo-agent",
    )
    _thread = threading.Thread(target=_loop, name="gebo-agent-runtime", daemon=True)
    _thread.start()
    _run_parallel_cycle()


def stop() -> None:
    global _running, _executor
    _running = False
    if _executor:
        _executor.shutdown(wait=False, cancel_futures=True)
        _executor = None


def get_runtime_status() -> dict[str, Any]:
    with _lock:
        agent_list = list(_states.values())
        codex = dict(_codex_lane)
    active = [a for a in agent_list if a.get("registry_status") == "active"]
    errors = [a for a in active if a.get("status") == "error"]
    codex_ok = codex.get("status") not in ("error", "audit_failed")
    healthy = len(errors) == 0 and _running and codex_ok
    return {
        "running": _running,
        "started_at": _started_at,
        "tick_interval_sec": TICK_INTERVAL_SEC,
        "active_agents": len(active),
        "total_registry": len(agents.get_agents()),
        "healthy": healthy,
        "parallel_workers": MAX_PARALLEL_WORKERS,
        "cycle_count": _cycle_count,
        "codex_lane": codex,
        "agents": sorted(agent_list, key=lambda x: x.get("name", "")),
    }
