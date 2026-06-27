# Google Hard-Core Developer Ecosystem (Gebo Private Backend)

All integration knowledge lives **privately in the backend** — SQLite memory, local doc cache, and manifest. Nothing leaves the Owner Node unless you enable internet fetch (still stored locally).

## Private backend API

| Endpoint | Purpose |
|----------|---------|
| `GET /system/private` | System snapshot — layers, knowledge stats, cache count |
| `POST /system/build` | Full build: collect → cache → memory → manifest |
| `POST /learning/cycle` | Learning cycle + evolution event |
| `POST /knowledge/web-collect` | Web deep fetch (internet required) |

## Gebo system layers (built around collected knowledge)

1. **Local Brain** — Ollama `gebo-custom`, memory, wiki
2. **Autonomy Core** — actions, reflexes, evolution, Codex lane
3. **Knowledge Fabric** — catalog, web cache, private docs, Google ecosystem taxonomy
4. **Integration Plane** — 50+ learnable + connector entries (Google, OSS, Firebase, GCP)
5. **Living Console** — Next.js shell + `geboClient` SDK

## Local data (gitignored)

```
backend/data/knowledge/cache/          # fetched doc excerpts
backend/data/knowledge/gebo-system-manifest.json
backend/data/private-docs/             # your private files
backend/data/gebo.db                   # all memories
```

## One-command private build

```powershell
.\scripts\gebo-system-build.ps1
```

Or: `Invoke-RestMethod -Method POST http://127.0.0.1:8000/system/build`

## Google developer stack

Taxonomy: `backend/data/knowledge/google-developer-ecosystem.json`  
Registry: `backend/app/integrations_registry.py` (52 integrations)

**Learnable** (Gebo studies docs): Flutter, TensorFlow, JAX, Bazel, Lighthouse, etc.  
**Connectors** (credentials later): Vertex AI, Firestore, GKE, Gmail, Gemini API.
