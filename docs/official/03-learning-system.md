# Learning System

Gebo learns from three sources:

## 1. Knowledge catalog

`backend/data/knowledge/catalog.json` — curated OSS repos, official doc URLs, open-weight models.

Collected into memory as `knowledge_oss`, `knowledge_doc`, `knowledge_model`.

## 2. Integration learnables

Integrations marked `mode: learnable` in `integrations_registry.py` (Google Docs API, TensorFlow, Hugging Face, etc.).

## 3. Private documents

Owner files in `backend/data/private-docs/` — **local only**, never uploaded.

## Commands

```powershell
.\scripts\gebo-knowledge-collect.ps1
curl -X POST http://127.0.0.1:8000/learning/cycle
```

## API

- `GET /knowledge/status` — stats
- `POST /knowledge/collect` — ingest without evolution event
- `POST /learning/cycle` — collect + record evolution lesson

## Internet

URL fetching requires `internet_access` enabled (Settings). Offline: URLs and metadata still stored.
