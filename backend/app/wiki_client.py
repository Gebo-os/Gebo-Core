"""Offline knowledge wiki for Gebo.

Reads a local ZIM file (e.g. a Wikipedia export from https://download.kiwix.org)
with libzim. Fully local: after the one-time ZIM download there is no internet
access. Gebo consults this when a question has no relevant memory/context.

Gracefully degrades: if libzim is not installed or no ZIM file is configured,
status() reports unavailable and search() returns an empty list.
"""
from __future__ import annotations

import os
import re
import threading
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

WIKI_ENABLED = os.getenv("WIKI_ENABLED", "true").lower() in ("1", "true", "yes")
# auto modes: "nocontext" (consult only when no memory match), "always", "off"
WIKI_AUTO = os.getenv("WIKI_AUTO", "nocontext").lower()
WIKI_RESULTS = int(os.getenv("WIKI_RESULTS", "3"))
WIKI_SNIPPET_CHARS = int(os.getenv("WIKI_SNIPPET_CHARS", "600"))

_default_zim = PROJECT_ROOT / "backend" / "data" / "wiki"
WIKI_ZIM_PATH = os.getenv("WIKI_ZIM_PATH", "").strip()

_archive = None
_archive_lock = threading.Lock()
_load_error: str | None = None

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def _resolve_zim_path() -> Path | None:
    """Find the ZIM file: explicit env path, or first *.zim in data/wiki."""
    if WIKI_ZIM_PATH:
        p = Path(WIKI_ZIM_PATH)
        return p if p.exists() else None
    if _default_zim.is_dir():
        zims = sorted(_default_zim.glob("*.zim"))
        if zims:
            return zims[0]
    return None


def _get_archive():
    """Lazily open the ZIM archive once. Returns None if unavailable."""
    global _archive, _load_error
    if _archive is not None:
        return _archive
    with _archive_lock:
        if _archive is not None:
            return _archive
        path = _resolve_zim_path()
        if path is None:
            _load_error = "No ZIM file found"
            return None
        try:
            from libzim.reader import Archive  # type: ignore

            _archive = Archive(str(path))
            _load_error = None
        except ImportError:
            _load_error = "libzim not installed"
            return None
        except Exception as exc:  # noqa: BLE001
            _load_error = f"Failed to open ZIM: {exc}"
            return None
    return _archive


def _html_to_text(html: str, limit: int) -> str:
    text = _TAG_RE.sub(" ", html)
    text = _WS_RE.sub(" ", text).strip()
    if len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0] + "..."
    return text


def is_enabled() -> bool:
    return WIKI_ENABLED and WIKI_AUTO != "off"


def is_available() -> bool:
    return _get_archive() is not None


def search(query: str, limit: int = WIKI_RESULTS) -> list[dict]:
    """Full-text search the ZIM. Returns [{title, snippet, path}]."""
    archive = _get_archive()
    if archive is None or not query.strip():
        return []
    try:
        if not getattr(archive, "has_fulltext_index", False):
            return []
        from libzim.search import Query, Searcher  # type: ignore

        searcher = Searcher(archive)
        search_obj = searcher.search(Query().set_query(query))
        estimated = search_obj.getEstimatedMatches()
        if not estimated:
            return []
        paths = list(search_obj.getResults(0, max(1, limit)))
    except Exception:  # noqa: BLE001
        return []

    results: list[dict] = []
    for path in paths:
        try:
            entry = archive.get_entry_by_path(path)
            item = entry.get_item()
            mimetype = getattr(item, "mimetype", "") or ""
            if "html" not in mimetype and "text" not in mimetype:
                continue
            content = bytes(item.content).decode("utf-8", errors="ignore")
            snippet = _html_to_text(content, WIKI_SNIPPET_CHARS)
            if not snippet:
                continue
            results.append(
                {"title": entry.title, "snippet": snippet, "path": path}
            )
        except Exception:  # noqa: BLE001
            continue
    return results


def status() -> dict:
    archive = _get_archive()
    available = archive is not None
    path = _resolve_zim_path()
    info = {
        "enabled": WIKI_ENABLED,
        "available": available,
        "auto_mode": WIKI_AUTO,
        "zim_path": str(path) if path else None,
        "error": _load_error,
        "title": None,
        "article_count": None,
        "has_fulltext_index": None,
    }
    if available:
        try:
            info["has_fulltext_index"] = bool(
                getattr(archive, "has_fulltext_index", False)
            )
            info["article_count"] = getattr(archive, "article_count", None)
            try:
                info["title"] = bytes(archive.get_metadata("Title")).decode(
                    "utf-8", errors="ignore"
                )
            except Exception:  # noqa: BLE001
                info["title"] = None
        except Exception:  # noqa: BLE001
            pass
    return info
