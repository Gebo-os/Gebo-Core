"""Detect and report local CLIs Gebo can orchestrate."""
from __future__ import annotations

import shutil
import subprocess
from typing import Any

CLI_CATALOG: list[dict[str, Any]] = [
    {"id": "ollama", "name": "Ollama", "bins": ["ollama"], "install": "https://ollama.com/download", "role": "local_model"},
    {"id": "codex", "name": "OpenAI Codex CLI", "bins": ["codex", "codex.cmd"], "install": "npm install -g @openai/codex", "role": "code_agent"},
    {"id": "gh", "name": "GitHub CLI", "bins": ["gh"], "install": "https://cli.github.com/", "role": "git_ops"},
    {"id": "git", "name": "Git", "bins": ["git"], "install": "https://git-scm.com/", "role": "version_control"},
    {"id": "node", "name": "Node.js", "bins": ["node"], "install": "https://nodejs.org/", "role": "runtime"},
    {"id": "npm", "name": "npm", "bins": ["npm"], "install": "bundled with Node.js", "role": "packages"},
    {"id": "python", "name": "Python", "bins": ["python", "python3"], "install": "https://python.org/", "role": "runtime"},
    {"id": "docker", "name": "Docker", "bins": ["docker"], "install": "https://docker.com/", "role": "containers"},
    {"id": "firebase", "name": "Firebase CLI", "bins": ["firebase"], "install": "npm install -g firebase-tools", "role": "consumer_deploy"},
    {"id": "gcloud", "name": "Google Cloud CLI", "bins": ["gcloud"], "install": "https://cloud.google.com/sdk", "role": "cloud"},
    {"id": "az", "name": "Azure CLI", "bins": ["az"], "install": "https://aka.ms/installazurecli", "role": "cloud"},
    {"id": "cursor", "name": "Cursor CLI", "bins": ["cursor"], "install": "https://cursor.com/", "role": "ide"},
]


def _version_for(exe: str) -> str | None:
    flags = [
        ["--version"],
        ["-v"],
        ["version"],
    ]
    for args in flags:
        try:
            r = subprocess.run(
                [exe, *args],
                capture_output=True,
                text=True,
                timeout=8,
                encoding="utf-8",
                errors="replace",
            )
            out = (r.stdout or r.stderr or "").strip().splitlines()
            if out:
                return out[0][:120]
        except (OSError, subprocess.TimeoutExpired):
            continue
    return None


def scan_clis() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for item in CLI_CATALOG:
        exe = None
        for name in item["bins"]:
            found = shutil.which(name)
            if found:
                exe = found
                break
        results.append(
            {
                "id": item["id"],
                "name": item["name"],
                "role": item["role"],
                "available": exe is not None,
                "path": exe,
                "version": _version_for(exe) if exe else None,
                "install_hint": item["install"],
            }
        )
    return results


def status() -> dict[str, Any]:
    items = scan_clis()
    available = sum(1 for i in items if i["available"])
    return {
        "total": len(items),
        "available": available,
        "items": items,
    }
