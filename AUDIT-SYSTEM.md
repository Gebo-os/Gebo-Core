# Gebo Core Private — System Audit

**Date:** 2026-06-26  
**Method:** Runtime verification + scoped manual audit (9 files)  
**Verdict:** **PASS** — no code changes required this session

---

## Runtime verification

| Check | Result |
|-------|--------|
| `pytest tests/` (`GEBO_TESTING=true`) | **40 passed**, 1 Starlette/httpx deprecation warning, ~32s |
| `npm run build` (frontend) | **Pass** — 12 static routes compiled |
| `GET /health` | **ok** — `agent_runtime_healthy: true` |
| `GET /agents/runtime/status` | **ok** — 8 active agents, codex lane `ok`, `healthy: true` |
| Debug instrumentation (`7284/ingest`, `#region agent log`) | **None** in scoped frontend files |

### Build routes (12)

`/`, `/_not-found`, `/actions`, `/build-log`, `/chat`, `/evolution`, `/memory`, `/presences`, `/reflexes`, `/settings`

---

## Scoped files reviewed

| File | Role |
|------|------|
| `backend/app/main.py` | FastAPI app, CORS, routes, action lifecycle |
| `backend/app/agent_runtime.py` | Parallel agent heartbeat + Codex lane |
| `backend/app/autonomy.py` | Intent detection, tool execution, background runs |
| `frontend/components/GeboOsShell.tsx` | Gebo OS layout shell |
| `frontend/components/AppShell.tsx` | Root shell wrapper |
| `frontend/components/OsNavLink.tsx` | View-transition navigation |
| `frontend/lib/osNav.ts` | Sidebar/tabs/quick-command config |
| `frontend/app/page.tsx` | Pulse home route |
| `scripts/gebo-parallel-verify.ps1` | Parallel pytest + codex + health check |

**Codex CLI:** Skipped full `codex exec review` (hangs scanning `backend/.venv`). Manual scoped audit used instead.

---

## Comparison to prior audits (`AUDIT-CODEX.md`, `AUDIT-DESKTOP-CODEX.md`)

### Already fixed (verified this session)

| ID | Finding | Status |
|----|---------|--------|
| C1 | CORS `*` + credentials | **Fixed** — `allow_credentials=False`; localhost defaults; open CORS only when `internet_access` enabled (`main.py`) |
| H2 | Terminal action reject transitions | **Fixed** — only `proposed` / `approved` may be rejected (`main.py:349-350`) |
| H5 | Unbounded input payloads | **Fixed** — Pydantic `max_length` in `schemas.py` (used by `main.py` routes) |
| H1 | Consent-on skips all proposals | **Fixed / by design** — only `save_memory` skipped when consent saves directly; other intents still proposed (`autonomy.py:68-69`) |
| H3 | AutonomyPanel effect deps | **Fixed** (prior session, out of scoped list) |
| — | Debug fetch logs in OS shell | **Removed** — `GeboOsShell.tsx` clean |
| — | Agent runtime Codex audit during tests | **Guarded** — `_testing()` skips periodic Codex audit (`agent_runtime.py:151-154`); conftest sets `GEBO_TESTING=true` |

### Open / low priority (not fixed — no runtime failure)

| Severity | Finding | Notes |
|----------|---------|-------|
| Medium | `run_action` sync tools return HTTP 500 after marking `failed` | `main.py:562-563`; UI still shows error; DB state correct |
| Medium | Memory recall falls back to recent when no match | `memory.py` (out of scope); quality issue |
| Medium | No DB migrations | V1 — Alembic |
| Medium | No API auth on write paths | Acceptable for localhost V0 |
| Low | `gebo-parallel-verify.ps1` omits explicit `GEBO_TESTING` | Harmless — `conftest.py` monkeypatches it |
| Low | Sidebar duplicate targets (`Chat` + `AI Studio` → `/chat`; `Network` + `Settings` → `/settings`) | OS mockup UX, not broken routes |
| Low | `CODex_AUDIT_EVERY_CYCLES` typo in constant name | Cosmetic only |
| Low | AutonomyPanel Strict Mode double-fetch, BuildLogPanel try/catch, Docker image size, frontend tests | From prior audits; out of scope |

---

## Issues found in scoped files (this session)

No **Critical** or **High** runtime bugs confirmed in scoped files. All navigation targets resolve to existing routes; shell wiring is consistent.

---

## Fixed this session

**None.** Tests and build were green before and after audit; no minimal fix was warranted under “fix only what needs.”

---

## Verified OK (no change needed)

- **CORS / network:** Settings-driven `internet_access`; middleware reflects DB state; credentials disabled.
- **Chat flow:** Intent detection, reflex proposals, wiki consult, and action insertion wired correctly in `main.py`.
- **Action lifecycle:** Approve/reject/run guards; background Codex tools return `running` status.
- **Agent runtime:** Parallel ticks, Codex lane status, health aggregation; test-mode audit skip.
- **Autonomy:** Tool registry, background threading, evolution hooks; consent-on remember is direct-save (documented).
- **Gebo OS shell:** Theme persistence, offline strip, Pulse skeleton, command dock → chat pending message, view-transition nav via `OsNavLink`.
- **Navigation config:** `getActiveSidebarIndex` resolves most-specific match; tabs cover all console sections.
- **`gebo-parallel-verify.ps1`:** Concurrent pytest, codex version, and backend health jobs structured correctly.

---

## Blockers

- **Codex full-repo scan:** `codex exec review` at repo root stalls on `backend/.venv` (~15+ min). Use scoped file lists or `codex_client.run_task()` with explicit paths for future audits.

---

## Commands to reproduce

```powershell
Set-Location backend
$env:GEBO_TESTING = "true"
.\.venv\Scripts\python.exe -m pytest tests/ -q

Set-Location ..\frontend
npm run build
```

Optional (backend running):

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/agents/runtime/status
```
