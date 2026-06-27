"""Collect learnable knowledge: catalog, private docs, web fetch → Gebo memory."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app import db, web_fetcher

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CATALOG_PATH = PROJECT_ROOT / "backend" / "data" / "knowledge" / "catalog.json"
GOOGLE_DEV_ECOSYSTEM_PATH = PROJECT_ROOT / "backend" / "data" / "knowledge" / "google-developer-ecosystem.json"
PRIVATE_DOCS_DIR = PROJECT_ROOT / "backend" / "data" / "private-docs"
MAX_PRIVATE_FILE_BYTES = 256_000


def load_catalog() -> dict[str, Any]:
    if not CATALOG_PATH.is_file():
        return {"oss_repos": [], "official_docs": [], "open_weight_models": []}
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def _ingest_memory(memory_type: str, content: str, source: str) -> int | None:
    if db.memory_exists(content):
        return None
    return db.insert_memory(memory_type, content, source)


def collect_web_github_repos() -> dict[str, int]:
    """Fetch live GitHub metadata + README excerpts when internet is on."""
    catalog = load_catalog()
    stats = {"ingested": 0, "skipped": 0, "fetched": 0, "offline": 0}
    if not web_fetcher.internet_enabled():
        stats["offline"] = len(catalog.get("oss_repos", []))
        return stats

    for repo in catalog.get("oss_repos", []):
        name = repo["name"]
        meta = web_fetcher.fetch_github_repo(name)
        if meta:
            stats["fetched"] += 1
            content = (
                f"Web knowledge [GitHub {meta['full_name']}]: "
                f"{meta['description']}. Language: {meta['language']}. "
                f"Stars: {meta['stars']}. Topics: {', '.join(meta['topics'][:8])}. "
                f"Learn: {repo.get('learn', '')}. "
                f"README excerpt: {meta['readme_excerpt'][:2000]}"
            )
        else:
            content = (
                f"OSS reference: {name} — topic: {repo.get('topic', 'general')}. "
                f"Gebo learning note: {repo.get('learn', '')}. "
                f"https://github.com/{name}"
            )
        if _ingest_memory("knowledge_web_github", content, f"github/{name}") is not None:
            stats["ingested"] += 1
        else:
            stats["skipped"] += 1
    return stats


def collect_web_official_docs() -> dict[str, int]:
    """Fetch public documentation pages when internet is on."""
    catalog = load_catalog()
    stats = {"ingested": 0, "skipped": 0, "fetched": 0, "offline": 0}
    if not web_fetcher.internet_enabled():
        stats["offline"] = len(catalog.get("official_docs", []))
        return stats

    for doc in catalog.get("official_docs", []):
        summary = web_fetcher.fetch_url_summary(doc["url"], doc.get("title", ""))
        if summary["fetched"]:
            stats["fetched"] += 1
        content = (
            f"Web knowledge [doc {doc.get('title', doc['url'])}] "
            f"({doc.get('provider', 'unknown')}): {doc['url']}. "
            f"Excerpt: {summary['excerpt'][:3500]}"
        )
        if _ingest_memory("knowledge_web_doc", content, f"web/{doc.get('id', doc['url'])}") is not None:
            stats["ingested"] += 1
        else:
            stats["skipped"] += 1
    return stats


def collect_web_integration_docs() -> dict[str, int]:
    """Fetch integration documentation URLs from registry."""
    from app import integrations_registry

    stats = {"ingested": 0, "skipped": 0, "fetched": 0}
    if not web_fetcher.internet_enabled():
        return stats

    for item in integrations_registry.INTEGRATIONS:
        url = item.get("docs")
        if not url or not url.startswith("http"):
            continue
        summary = web_fetcher.fetch_url_summary(url, item["name"])
        if summary["fetched"]:
            stats["fetched"] += 1
        content = (
            f"Web knowledge [integration {item['name']}] ({item['category']}, "
            f"{item['mode']}): {url}. Excerpt: {summary['excerpt'][:2500]}"
        )
        if _ingest_memory("knowledge_web_integration", content, f"integration/{item['id']}") is not None:
            stats["ingested"] += 1
        else:
            stats["skipped"] += 1
    return stats


def collect_catalog_memories() -> dict[str, int]:
    """Static catalog entries (works offline)."""
    catalog = load_catalog()
    stats = {"oss": 0, "docs": 0, "models": 0, "skipped": 0}

    for repo in catalog.get("oss_repos", []):
        content = (
            f"OSS catalog: {repo['name']} — topic: {repo.get('topic', 'general')}. "
            f"Gebo learning note: {repo.get('learn', '')}. "
            f"https://github.com/{repo['name']}"
        )
        if _ingest_memory("knowledge_oss", content, "knowledge_collector") is not None:
            stats["oss"] += 1
        else:
            stats["skipped"] += 1

    for doc in catalog.get("official_docs", []):
        content = (
            f"Doc catalog: {doc['title']} ({doc.get('provider', 'unknown')}) — {doc['url']}"
        )
        if _ingest_memory("knowledge_doc", content, "knowledge_collector") is not None:
            stats["docs"] += 1
        else:
            stats["skipped"] += 1

    for model in catalog.get("open_weight_models", []):
        content = (
            f"Open-weight model: {model['name']} via {model.get('via', 'unknown')} — "
            f"{model.get('notes', '')}"
        )
        if _ingest_memory("knowledge_model", content, "knowledge_collector") is not None:
            stats["models"] += 1
        else:
            stats["skipped"] += 1

    return stats


def collect_private_docs() -> dict[str, int]:
    PRIVATE_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    stats = {"ingested": 0, "skipped": 0, "files": 0}
    allowed = {".md", ".txt", ".json", ".csv"}
    for path in sorted(PRIVATE_DOCS_DIR.iterdir()):
        if not path.is_file() or path.suffix.lower() not in allowed:
            continue
        stats["files"] += 1
        if path.stat().st_size > MAX_PRIVATE_FILE_BYTES:
            stats["skipped"] += 1
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")[:12000]
        content = f"Private document [{path.name}]: {text}"
        if _ingest_memory("private_doc", content, f"private-docs/{path.name}") is not None:
            stats["ingested"] += 1
        else:
            stats["skipped"] += 1
    return stats


def collect_google_developer_ecosystem() -> dict[str, int]:
    """Ingest structured Google developer ecosystem taxonomy."""
    stats = {"ingested": 0, "skipped": 0}
    if not GOOGLE_DEV_ECOSYSTEM_PATH.is_file():
        return stats
    data = json.loads(GOOGLE_DEV_ECOSYSTEM_PATH.read_text(encoding="utf-8"))
    for layer in data.get("layers", []):
        for item in layer.get("items", []):
            mode = "connector" if item.get("connector") else "learnable"
            content = (
                f"Google developer ecosystem [{layer['name']}]: {item['id']} — "
                f"mode={mode}. Docs: {item.get('docs', 'n/a')}. "
                f"Gebo uses learnable entries for memory; connectors need GCP/Firebase credentials."
            )
            if _ingest_memory("knowledge_google_dev", content, "google-developer-ecosystem") is not None:
                stats["ingested"] += 1
            else:
                stats["skipped"] += 1
    return stats


def collect_integration_learnings() -> dict[str, int]:
    from app import integrations_registry

    stats = {"ingested": 0, "skipped": 0}
    for item in integrations_registry.INTEGRATIONS:
        if item["mode"] != "learnable":
            continue
        content = (
            f"Integration learnable: {item['name']} ({item['category']}) — "
            f"docs: {item.get('docs', 'n/a')}. Connectors like email require OAuth."
        )
        if _ingest_memory("knowledge_integration", content, "integrations_registry") is not None:
            stats["ingested"] += 1
        else:
            stats["skipped"] += 1
    return stats


def status() -> dict[str, Any]:
    catalog = load_catalog()
    PRIVATE_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    private_files = [
        p.name
        for p in PRIVATE_DOCS_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in {".md", ".txt", ".json", ".csv"}
    ]
    knowledge_memories = db.count_memories_by_type_prefix("knowledge")
    web_memories = db.count_memories_by_type_prefix("knowledge_web")
    return {
        "catalog_path": str(CATALOG_PATH),
        "private_docs_dir": str(PRIVATE_DOCS_DIR),
        "private_doc_count": len(private_files),
        "private_doc_files": private_files[:20],
        "catalog_oss_count": len(catalog.get("oss_repos", [])),
        "catalog_docs_count": len(catalog.get("official_docs", [])),
        "catalog_models_count": len(catalog.get("open_weight_models", [])),
        "knowledge_memory_count": knowledge_memories,
        "web_knowledge_memory_count": web_memories,
        "internet_access": db.get_internet_access(),
        "web_fetch_ready": db.get_internet_access(),
    }


def run_web_collection() -> dict[str, Any]:
    return {
        "github": collect_web_github_repos(),
        "official_docs": collect_web_official_docs(),
        "integration_docs": collect_web_integration_docs(),
    }


def run_full_collection() -> dict[str, Any]:
    result = {
        "catalog": collect_catalog_memories(),
        "private_docs": collect_private_docs(),
        "integrations": collect_integration_learnings(),
        "google_developer_ecosystem": collect_google_developer_ecosystem(),
    }
    if web_fetcher.internet_enabled():
        result["web"] = run_web_collection()
    else:
        result["web"] = {"skipped": True, "reason": "internet_access disabled"}
    return result
