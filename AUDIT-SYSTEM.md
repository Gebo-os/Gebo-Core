# Gebo Core Private — System Audit

**Date:** 2026-06-26  
**Method:** Full pytest + frontend build + endpoint smoke tests + git push  
**Verdict:** **PASS** — V1 stack audited, finalized, and pushed to GitHub

---

## Runtime verification

| Check | Result |
|-------|--------|
| `pytest tests/` (`GEBO_TESTING=true`) | **65 passed**, 1 Starlette/httpx deprecation warning, ~72s |
| `npm run build` (frontend) | **Pass** — 12 static routes compiled |
| `test_all_endpoints.py` | **Pass** — 22 GET routes + POST lifecycle coverage |
| `test_v1_release.py` | **Pass** — V1 readiness, modules, owner auth mode |
| Bootstrap check (scripts + desktop) | **Pass** — `/integrate/bootstrap` verified, not health-only |

### Build routes (12)

`/`, `/_not-found`, `/actions`, `/build-log`, `/chat`, `/evolution`, `/memory`, `/presences`, `/reflexes`, `/settings`

---

## Endpoint coverage

**GET routes smoke-tested (22):**

`/health`, `/status`, `/integrate/bootstrap`, `/memory`, `/actions`, `/codex/status`, `/wiki/status`, `/reflexes`, `/reflex-events`, `/agents/runtime/status`, `/evolution/status`, `/evolution/events`, `/evolution/scores`, `/evolution/upgrades`, `/settings/network`, `/integrations/status`, `/cli/status`, `/knowledge/status`, `/system/private`, `/system/production-readiness`, `/system/v1-readiness`, `/system/modules`, `/v1/billing/plans`, `/v1/identity/owner-status`

**POST routes exercised:**

`/settings/consent`, `/settings/network`, `/memory`, `/chat`, `/actions/propose`, `/actions/{id}/approve`, `/actions/{id}/run`, `/reflexes`, `/reflexes/{id}/toggle`, `/evolution/score-action`, `/evolution/suggest-upgrade`, `/evolution/upgrades/{id}/approve`, `/learning/cycle`, `/system/build`, `/knowledge/collect`, `/v1/security/verify-turnstile`

**Not smoke-tested (conditional / destructive):**

- `POST /knowledge/web-collect` — requires `internet_access` enabled
- `POST /actions/{id}/reject` — covered by unit guards in `main.py`
- `POST /evolution/upgrades/{id}/reject` — covered by evolution flow tests

---

## Fixes applied this session

| File | Fix |
|------|-----|
| `frontend/lib/GeboProvider.tsx` | Import `getStatus` + `getNetworkSettings` for bootstrap fallback |
| `backend/tests/test_all_endpoints.py` | Added V1 billing/identity, turnstile, knowledge/collect tests |
| `scripts/build-gebo-desktop.ps1` | Use `npm run pack` (no code signing) + correct exe path |
| `README.md` | V1 stack scripts section + restart troubleshooting |

---

## Git push

| Item | Value |
|------|-------|
| V1 release commit | `c9aae9d` — Add V1 release stack, knowledge system, production security, and desktop tooling |
| Finalization commit | See `git log -1` after push |
| Remote | https://github.com/Gebo-os/Gebo-Core.git |
| Branch | `main` |

---

## Known gaps (expected)

| Gap | Notes |
|-----|-------|
| Cloud env not configured | Supabase, Stripe, Upstash, Turnstile — owner node runs without them |
| `POST /knowledge/web-collect` | Skipped in smoke tests unless internet access enabled |
| Codex full-repo scan | `codex exec review` stalls on `backend/.venv`; use scoped paths |
| No frontend unit tests | Backend pytest covers API; frontend validated via `npm run build` |
| DB migrations | V1 uses SQLite init; Alembic planned for production |

---

## Commands to reproduce

```powershell
Set-Location backend
$env:GEBO_TESTING = "true"
.\.venv\Scripts\python.exe -m pytest tests/ -q

Set-Location ..\frontend
npm run build

Set-Location ..\backend
$env:GEBO_TESTING = "true"
.\.venv\Scripts\python.exe -m pytest tests/test_all_endpoints.py tests/test_v1_release.py -q
```

Optional (backend running):

```powershell
Invoke-RestMethod http://127.0.0.1:8000/integrate/bootstrap
Invoke-RestMethod http://127.0.0.1:8000/system/v1-readiness
Invoke-RestMethod http://127.0.0.1:8000/v1/billing/plans
```
