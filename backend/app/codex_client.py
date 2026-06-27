"""Codex CLI integration for Gebo Core.

Wraps the local `codex` CLI so Gebo can run real, approval-gated coding and
review tasks. All execution is local. Nothing here runs without an approved
action in the autonomy layer.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

# Project root = parent of the backend directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

CODEX_ENABLED = os.getenv("CODEX_ENABLED", "true").lower() == "true"
CODEX_WORKDIR = os.getenv("CODEX_WORKDIR", str(PROJECT_ROOT))
CODEX_TIMEOUT = int(os.getenv("CODEX_TIMEOUT", "900"))  # seconds

_SUBPROCESS_TEXT = {"text": True, "encoding": "utf-8", "errors": "replace"}

_VERSION_CACHE: dict[str, object] = {}


def _resolve_codex() -> str | None:
    for name in ("codex.cmd", "codex.exe", "codex"):
        found = shutil.which(name)
        if found:
            return found
    return None


def is_available() -> bool:
    if not CODEX_ENABLED:
        return False
    return _resolve_codex() is not None


def get_version() -> str | None:
    if "version" in _VERSION_CACHE:
        return _VERSION_CACHE["version"]  # type: ignore[return-value]
    exe = _resolve_codex()
    if not exe:
        return None
    try:
        result = subprocess.run(
            [exe, "--version"],
            capture_output=True,
            timeout=30,
            check=False,
            **_SUBPROCESS_TEXT,
        )
        version = (result.stdout or result.stderr or "").strip().splitlines()
        v = version[0] if version else None
        _VERSION_CACHE["version"] = v
        return v
    except (subprocess.TimeoutExpired, OSError):
        return None


def status() -> dict:
    available = is_available()
    return {
        "available": available,
        "enabled": CODEX_ENABLED,
        "version": get_version() if available else None,
        "workdir": CODEX_WORKDIR,
        "timeout_sec": CODEX_TIMEOUT,
    }


def _read_output_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore").strip()
    except OSError:
        return ""


def _tail(text: str, lines: int = 40, max_chars: int = 4000) -> str:
    parts = text.strip().splitlines()
    tail = "\n".join(parts[-lines:])
    if len(tail) > max_chars:
        tail = tail[-max_chars:]
    return tail


def run_task(prompt: str, mode: str = "review") -> dict:
    """Run a Codex task.

    mode = "review"  -> read-only code review (no file writes)
    mode = "build"   -> workspace-write task (can modify files in workdir)
    """
    exe = _resolve_codex()
    if not exe:
        return {
            "ok": False,
            "error": "Codex CLI not found. Install with: npm install -g @openai/codex",
        }

    if not prompt or not prompt.strip():
        return {"ok": False, "error": "Empty prompt"}

    out_file = Path(tempfile.gettempdir()) / f"gebo-codex-{int(time.time()*1000)}.txt"

    if mode == "review":
        cmd = [
            exe,
            "exec",
            "review",
            "--skip-git-repo-check",
            "-o",
            str(out_file),
            prompt,
        ]
    else:
        cmd = [
            exe,
            "exec",
            "--skip-git-repo-check",
            "--sandbox",
            "workspace-write",
            "-o",
            str(out_file),
            prompt,
        ]

    started = time.time()
    try:
        result = subprocess.run(
            cmd,
            cwd=CODEX_WORKDIR,
            capture_output=True,
            timeout=CODEX_TIMEOUT,
            check=False,
            env={**os.environ, "TERM": "xterm-256color"},
            **_SUBPROCESS_TEXT,
        )
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "error": f"Codex timed out after {CODEX_TIMEOUT}s",
            "mode": mode,
        }
    except OSError as exc:
        return {"ok": False, "error": f"Codex failed to start: {exc}", "mode": mode}

    elapsed = round(time.time() - started, 1)
    last_message = _read_output_file(out_file)
    try:
        out_file.unlink(missing_ok=True)
    except OSError:
        pass

    ok = result.returncode == 0
    return {
        "ok": ok,
        "mode": mode,
        "exit_code": result.returncode,
        "elapsed_sec": elapsed,
        "result": last_message or _tail(result.stdout or ""),
        "stderr_tail": _tail(result.stderr or "") if not ok else "",
        "workdir": CODEX_WORKDIR,
    }
