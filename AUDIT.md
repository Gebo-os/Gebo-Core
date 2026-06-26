# Gebo Core Private — Security & Quality Audit

**Date:** 2026-06-26  
**Scope:** Full monorepo (FastAPI backend + Next.js Gebo Living Console)  
**Method:** Codex CLI review (partial) + manual verification

---

## Executive Summary

Gebo Core Private V0 is a functional local-first stack: chat, memory, autonomy, and a multi-page console all work. The architecture matches the spec for a private single-user tool.

**Main gaps before production use on a shared network:**

1. No authentication — all endpoints are open on `127.0.0.1` (acceptable for strict localhost; risky if bound to `0.0.0.0`).
2. CORS was misconfigured (`allow_origins=["*"]` with `allow_credentials=True`).
3. No input size limits on chat/memory/action payloads.
4. Recalled memory is injected raw into the Ollama system prompt (prompt-injection surface).
5. `summarize_recent_messages` and `create_plan` tools do not call Ollama — they produce structured stubs only.

**Verdict:** Suitable for **local private use on one machine**. Harden before exposing beyond localhost.

---

## Critical

| # | Finding | Path | Fix |
|---|---------|------|-----|
| 1 | CORS `*` + credentials invalid/unsafe | `backend/app/main.py` | Restrict origins to `localhost:3000`, drop credentials or use explicit origins |
| 2 | No auth on any endpoint | `backend/app/main.py` | Acceptable for V0 localhost; document never bind publicly without auth |
| 3 | Unbounded user input stored and sent to model | `backend/app/schemas.py` | Add `Field(max_length=...)` on message, memory, action fields |
| 4 | Raw memory in system prompt | `backend/app/memory.py` | Truncate/sanitize recalled content before prompt build |

---

## High

| # | Finding | Path | Fix |
|---|---------|------|-----|
| 5 | Export dumps all data with no gate | `GET /memory/export` | Local-only OK; add note in Settings |
| 6 | Consent-on saves "remember" without approval | `backend/app/autonomy.py` | By design for V0; document in Settings |
| 7 | Action run lacks atomic status check | `backend/app/db.py` | Use `UPDATE ... WHERE status='approved'` |
| 8 | No chat timeout on frontend | `frontend/lib/api.ts` | Add `AbortSignal.timeout(120000)` |
| 9 | Fallback recall returns recent, not relevant | `backend/app/memory.py` | Label as "recent" when score=0 or require min score |
| 10 | summarize/create_plan don't use LLM | `backend/app/autonomy.py` | Rename labels or call Ollama in V1 |

---

## Medium

| # | Finding | Path | Fix |
|---|---------|------|-----|
| 11 | No SQLite WAL mode | `backend/app/db.py` | `PRAGMA journal_mode=WAL` on init |
| 12 | No rate limiting on `/chat` | `backend/app/main.py` | V1: simple in-memory throttle |
| 13 | Build log only in localStorage | `frontend/lib/buildLog.ts` | V1: optional backend sync |
| 14 | No automated tests | — | Add smoke tests V1 |
| 15 | GitHub memory not integrated | — | Read-only ingest script + `gh auth login` |

---

## Low

| # | Finding | Path | Fix |
|---|---------|------|-----|
| 16 | Unused constants `CHAT_DRAFT_KEY`, `COMMAND_DRAFT_KEY` | `frontend/lib/constants.ts` | Align with sessionStorage keys |
| 17 | Archive/Delete disabled in UI | `MemoryCard.tsx` | Correct — backend has no delete |
| 18 | Codex MCP n8n plugin errors | Codex config | Disable broken n8n MCP server |

---

## Fixes Applied (2026-06-26)

- CORS restricted to local frontend origins
- Pydantic max lengths on inputs
- Memory prompt truncation
- SQLite WAL mode
- Atomic action run guard
- Frontend fetch timeout
- GitHub/local repo memory ingest script
- This audit document

---

## GitHub Memory (read-only)

Run after `gh auth login`:

```powershell
cd backend
.\.venv\Scripts\python scripts\ingest_repo_memory.py
```

Uses `gh repo list` when authenticated; falls back to local git repos. **Never pushes or edits GitHub.**
