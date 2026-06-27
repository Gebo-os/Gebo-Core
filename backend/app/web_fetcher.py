"""Web fetching for Gebo knowledge collection — public docs and OSS metadata only."""
from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app import db

USER_AGENT = "Gebo-Knowledge-Collector/1.0 (+local-first; public-docs-only)"
MAX_BYTES = 64_000
GITHUB_API = "https://api.github.com/repos/{repo}"
CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "knowledge" / "cache"


def internet_enabled() -> bool:
    return db.get_internet_access()


def _request(url: str, accept: str = "*/*") -> bytes | None:
    if not internet_enabled():
        return None
    try:
        req = Request(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": accept,
            },
        )
        with urlopen(req, timeout=15) as resp:
            return resp.read(MAX_BYTES)
    except (HTTPError, URLError, OSError, TimeoutError):
        return None


def strip_html(html: str) -> str:
    text = re.sub(r"(?is)<script.*?>.*?</script>", " ", html)
    text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
    text = re.sub(r"(?is)<[^>]+>", " ", text)
    text = unescape(re.sub(r"\s+", " ", text)).strip()
    return text[:6000]


def _cache_key(url: str) -> str:
    import hashlib

    return hashlib.sha256(url.encode()).hexdigest()[:16]


def _write_cache(url: str, text: str) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"{_cache_key(url)}.txt"
    header = f"# source: {url}\n# cached_by: gebo\n\n"
    path.write_text(header + text[:50000], encoding="utf-8", errors="ignore")


def _read_cache(url: str) -> str | None:
    path = CACHE_DIR / f"{_cache_key(url)}.txt"
    if not path.is_file():
        return None
    raw = path.read_text(encoding="utf-8", errors="ignore")
    if raw.startswith("# source:"):
        parts = raw.split("\n\n", 1)
        return parts[1] if len(parts) > 1 else raw
    return raw


def fetch_page_text(url: str) -> str | None:
    cached = _read_cache(url)
    if cached:
        return cached
    raw = _request(url, accept="text/html,application/xhtml+xml,text/plain,*/*")
    if not raw:
        return None
    text = raw.decode("utf-8", errors="ignore")
    if "<html" in text.lower() or "<body" in text.lower():
        body = strip_html(text)
    else:
        body = text[:6000]
    _write_cache(url, body)
    return body


def fetch_github_repo(repo: str) -> dict[str, Any] | None:
    raw = _request(GITHUB_API.format(repo=repo), accept="application/vnd.github+json")
    if not raw:
        return None
    try:
        data = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict) or "message" in data and data.get("message") == "Not Found":
        return None
    readme = fetch_page_text(f"https://raw.githubusercontent.com/{repo}/main/README.md")
    if not readme:
        readme = fetch_page_text(f"https://raw.githubusercontent.com/{repo}/master/README.md")
    return {
        "full_name": data.get("full_name", repo),
        "description": data.get("description") or "",
        "stars": data.get("stargazers_count", 0),
        "language": data.get("language") or "unknown",
        "topics": data.get("topics") or [],
        "homepage": data.get("homepage") or "",
        "readme_excerpt": (readme or "")[:2500],
    }


def fetch_url_summary(url: str, title: str = "") -> dict[str, Any]:
    body = fetch_page_text(url)
    return {
        "url": url,
        "title": title,
        "fetched": body is not None,
        "excerpt": (body or "")[:4000],
        "offline": body is None,
    }
