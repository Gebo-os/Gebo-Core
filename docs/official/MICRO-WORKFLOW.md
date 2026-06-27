# Gebo OS — Micromini Workflow

Release-ready step sequence. Each step is one command or one API call.

## Phase 0 — Bootstrap (once)

| Step | Action | Command |
|------|--------|---------|
| 0.1 | Install Ollama + model | `ollama pull llama3.2:3b` |
| 0.2 | Create Gebo custom model | `.\scripts\create-gebo-model.ps1` |
| 0.3 | Activate all CLIs | `.\scripts\gebo-activate-clis.ps1` |
| 0.4 | Start Gebo (WiFi) | `.\scripts\start-gebo.ps1` |

## Phase 1 — Learn (repeat daily or on demand)

| Step | Action | Command |
|------|--------|---------|
| 1.1 | Drop private docs | Copy files → `backend/data/private-docs/` |
| 1.2 | Collect catalog + docs | `.\scripts\gebo-knowledge-collect.ps1` |
| 1.3 | Full learning cycle | `POST /learning/cycle` |
| 1.4 | Verify memories | Settings → Memory count / Evolution events |

## Phase 2 — Integrate (per connector)

| Step | Action | Notes |
|------|--------|-------|
| 2.1 | Learnable (Docs, TensorFlow, OSS) | Auto-ingested via knowledge collector |
| 2.2 | Connector (Gmail, Calendar, Gemini) | Set env keys in `backend/.env` |
| 2.3 | Approve actions | Autonomy panel — nothing runs without approval |
| 2.4 | Codex build/review | Actions → `codex_review` / `codex_build` |

## Phase 3 — Verify (before release)

| Step | Action | Command |
|------|--------|---------|
| 3.1 | Parallel verify | `.\scripts\gebo-parallel-verify.ps1` |
| 3.2 | All screens | Open `/` … `/settings` (10 routes) |
| 3.3 | Bootstrap API | `GET /integrate/bootstrap` |
| 3.4 | Production build | `cd frontend && npm run build` |

## Phase 4 — Consumer ship

| Step | Action | Doc |
|------|--------|-----|
| 4.1 | SDK integration | [CONSUMER-APP.md](../CONSUMER-APP.md) |
| 4.2 | Firebase (optional) | Set `FIREBASE_PROJECT_ID` |
| 4.3 | Docker deploy | `docker compose up --build` |
| 4.4 | Official docs publish | `docs/official/` → site or PDF |

## API quick reference

```
GET  /integrate/bootstrap     — consumer startup snapshot
GET  /integrations/status     — Google + OSS integration catalog
GET  /cli/status              — local CLI availability
GET  /knowledge/status        — catalog + private doc stats
POST /knowledge/collect       — ingest learnable knowledge
POST /learning/cycle          — collect + evolution event
```

## What Gebo learns vs integrates

| Type | Examples | Mechanism |
|------|----------|-----------|
| **Learnable** | Google Docs API docs, TensorFlow, OSS repos | Memory ingestion from catalog |
| **Connector** | Gmail, Calendar, Gemini API | OAuth/API keys + future adapters |
| **Private** | Your `.md` / `.txt` in private-docs | Local file ingestion |
| **Built-in** | Chat, memory, Codex, agents | Already in Gebo Core |
