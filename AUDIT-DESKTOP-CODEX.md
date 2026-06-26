# Gebo Core Private — Desktop Release Audit (Codex CLI)

**Date:** 2026-06-26  
**Method:** `codex exec review` (Codex CLI 0.137.0)  
**Scope:** Full monorepo + desktop packaging readiness

---

## Executive Summary

Gebo Core Private is a coherent local-first stack: FastAPI + SQLite + Ollama backend, Next.js 14 Living Console frontend, approval-gated autonomy, offline wiki, internal agent registry, and **13 backend pytest tests**.

**Desktop app added:** `desktop/` Electron shell + `scripts/start-gebo-desktop.ps1`.

**Verdict:** Suitable for **local private use on one machine**. Many V0 audit items are already fixed (see below). Remaining gaps are mostly V1 hardening (auth token, migrations, frontend tests).

---

## Critical

### C1. CORS — **FIXED**
Was `allow_origins=["*"]` with credentials. Now restricted to localhost origins, `allow_credentials=False`.  
`backend/app/main.py`

---

## High

| # | Finding | Status |
|---|---------|--------|
| H1 | Action proposals skipped when consent on | Open — autonomy early-return |
| H2 | Terminal action reject transitions | Partially guarded |
| H3 | AutonomyPanel effect deps | **FIXED** |
| H4 | BuildLogPanel localStorage errors | Open |
| H5 | Input size limits | **FIXED** (Pydantic max_length) |

---

## Medium

| # | Finding | Status |
|---|---------|--------|
| M1 | No DB migrations | Open — use Alembic in V1 |
| M2 | run_action returns 500 on tool failure | Open |
| M3 | Memory recall falls back to recent | Open |
| M4 | Presence always Awake after first chat | Open |
| M5 | Docker frontend image size | Open |
| M6 | GeboProvider poll overlap | Open |
| M7 | gebo.db tracked in repo | Check `.gitignore` |
| M8 | No API auth on write paths | Acceptable for localhost V0 |

---

## Low

UX polish: disabled Archive/Delete buttons, unused constants, unpinned deps, no frontend tests.

---

## Already Fixed (this session / prior)

- CORS locked to localhost
- Pydantic input limits
- Memory prompt sanitization
- SQLite WAL mode
- Atomic action claim (`claim_approved_action`)
- Frontend fetch timeouts
- GitHub/local repo memory ingest
- Backend pytest suite (13 tests)
- Generative UI with FPS caps + motion toggle
- Offline banner + chat guard
- Electron desktop shell

---

## Desktop Launch

```powershell
.\scripts\start-gebo-desktop.ps1
```

Or:

```powershell
cd desktop
npm install
npm start
```

**Memory:** `backend/data/gebo.db`

---

## Test

```powershell
cd backend
.\.venv\Scripts\python -m pytest -q
```
