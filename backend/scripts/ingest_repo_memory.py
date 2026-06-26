#!/usr/bin/env python3
"""Read-only GitHub / local repo memory ingest for Gebo Core.

Never modifies GitHub. Saves repo summaries to Gebo SQLite via API or direct DB.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import httpx

API_URL = os.getenv("GEBO_API_URL", "http://127.0.0.1:8000")
MAX_README = 2000
SCAN_ROOTS = [
    Path.home() / "Desktop",
    Path.home() / ".agents",
    Path(__file__).resolve().parent.parent.parent,
]


def run(cmd: list[str], cwd: Path | None = None) -> str | None:
    try:
        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=60,
            check=False,
        )
        if r.returncode == 0:
            return r.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def gh_authenticated() -> bool:
    try:
        r = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        combined = (r.stdout or "") + (r.stderr or "")
        return r.returncode == 0 and "Logged in" in combined
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def fetch_github_repos() -> list[dict]:
    raw = run(
        [
            "gh",
            "repo",
            "list",
            "--limit",
            "50",
            "--json",
            "name,description,url,updatedAt,isPrivate,primaryLanguage,defaultBranchRef",
        ]
    )
    if not raw:
        return []
    return json.loads(raw)


def find_local_repos() -> list[dict]:
    repos: list[dict] = []
    seen: set[str] = set()
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for git_dir in root.rglob(".git"):
            if not git_dir.is_dir():
                continue
            repo_path = git_dir.parent
            key = str(repo_path.resolve())
            if key in seen:
                continue
            seen.add(key)
            cfg = git_dir / "config"
            remote = ""
            if cfg.exists():
                for line in cfg.read_text(encoding="utf-8", errors="ignore").splitlines():
                    if "url =" in line or "url=" in line:
                        remote = line.split("=", 1)[-1].strip()
                        break
            readme = repo_path / "README.md"
            readme_text = ""
            if readme.exists():
                readme_text = readme.read_text(encoding="utf-8", errors="ignore")[:MAX_README]
            repos.append(
                {
                    "name": repo_path.name,
                    "path": str(repo_path),
                    "url": remote or f"local://{repo_path.name}",
                    "description": f"Local repo at {repo_path}",
                    "readme": readme_text,
                    "source": "local_git",
                }
            )
    return repos


def build_memory_content(repo: dict) -> str:
    lines = [
        f"# Repo: {repo.get('name', 'unknown')}",
        f"URL: {repo.get('url', '')}",
    ]
    if repo.get("description"):
        lines.append(f"Description: {repo['description']}")
    if repo.get("path"):
        lines.append(f"Local path: {repo['path']}")
    if repo.get("updatedAt"):
        lines.append(f"Updated: {repo['updatedAt']}")
    if repo.get("primaryLanguage", {}).get("name"):
        lines.append(f"Language: {repo['primaryLanguage']['name']}")
    if repo.get("isPrivate") is not None:
        lines.append(f"Private: {repo['isPrivate']}")
    readme = repo.get("readme", "")
    if readme:
        lines.extend(["", "## README excerpt", readme[:MAX_README]])
    return "\n".join(lines)


def save_via_api(content: str, source: str) -> bool:
    try:
        tagged = f"[source:{source}]\n{content}"
        r = httpx.post(
            f"{API_URL}/memory",
            json={"memory_type": "project", "content": tagged[:12000]},
            headers={"Content-Type": "application/json"},
            timeout=10.0,
        )
        return r.status_code == 200
    except httpx.RequestError:
        return False


def save_via_db(content: str, source: str) -> bool:
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from app import db

        db.init_db()
        db.insert_memory("project", content, source)
        return True
    except Exception:
        return False


def main() -> int:
    ingested = 0
    repos: list[dict] = []

    if gh_authenticated():
        print("GitHub: authenticated — fetching repos (read-only)")
        for r in fetch_github_repos():
            name = r.get("name", "")
            url = r.get("url", "")
            readme = ""
            if url and "github.com" in url:
                parts = url.rstrip("/").split("/")
                if len(parts) >= 2:
                    owner, repo_name = parts[-2], parts[-1]
                    readme_raw = run(["gh", "api", f"repos/{owner}/{repo_name}/readme", "--jq", ".content"])
                    if readme_raw:
                        import base64

                        try:
                            readme = base64.b64decode(readme_raw).decode("utf-8", errors="ignore")[:MAX_README]
                        except Exception:
                            readme = ""
            repos.append({**r, "readme": readme, "source": "github_readonly"})
    else:
        print("GitHub: not authenticated — using local git repos only")
        print("  Run: gh auth login")

    local = find_local_repos()
    gh_urls = {r.get("url", "").rstrip(".git") for r in repos}
    for lr in local:
        remote = lr.get("url", "").rstrip(".git")
        if remote not in gh_urls:
            repos.append(lr)

    if not repos:
        print("No repos found.")
        return 1

    print(f"Found {len(repos)} repos — ingesting into Gebo memory...")
    for repo in repos:
        content = build_memory_content(repo)
        source = repo.get("source", "repo_ingest")
        ok = save_via_api(content, source)
        if not ok:
            ok = save_via_db(content, source)
        if ok:
            ingested += 1
            print(f"  + {repo.get('name', '?')}")
        else:
            print(f"  ! failed: {repo.get('name', '?')}")

    print(f"Done. {ingested}/{len(repos)} memories saved.")
    return 0 if ingested else 1


if __name__ == "__main__":
    raise SystemExit(main())
