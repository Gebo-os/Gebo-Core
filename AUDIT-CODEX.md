I have a complete picture. Compiling the audit now.

# Audit: Gebo Core Private Monorepo

## Executive Summary

Gebo Core Private is a small but reasonably structured local-first monorepo: a FastAPI + SQLite backend that fronts an Ollama-served Llama model, and a Next.js 14 (App Router) frontend. The architecture is coherent, the database layer is straightforward, and the autonomy/policy intent (propose → approve → run) is well modeled. There are no tests in either the backend or frontend, and the build/run pipeline depends on a venv and `node_modules` that are committed to the workspace (they should not be).

The most important concerns are around safety and correctness in the autonomy layer, missing input validation, an unsafe CORS configuration, and several runtime bugs in the React layer (effect dependency, race conditions, optimistic UI without rollback). None of these are likely to crash the app, but several will produce incorrect or confusing behavior; the CORS issue is the only one that could realistically expose the app if deployed beyond a single trusted host.

Findings are grouped by severity below. Each item includes file paths, the smallest reliable line range, and an actionable fix.

---

## Critical

### C1. CORS allows any origin with credentials — [backend/app/main.py:33-39]

`allow_origins=["*"]` combined with `allow_credentials=True` is both invalid per the CORS spec (browsers reject the combination) and unsafe. Any origin can call the API, which is fine for the localhost-only design but means that the moment this is exposed (a tunnel, a Docker host with a public port, a LAN address), any third-party site the user visits can issue authenticated cross-origin requests against the FastAPI service. There is no auth, so the only barrier is the origin restriction.

**Fix:** Restrict to an explicit list (e.g. `["http://localhost:3000", "http://127.0.0.1:3000"]`) driven by an env var. Drop `allow_credentials=True` unless cookies are actually used (they are not in this app — the API is purely bearer-less JSON over fetch).

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
```

---

## High

### H1. `propose_action` does not run action intent detection for chat messages — [backend/app/main.py:108-128]

`detect_action_intents` produces a `save_memory` proposal only when consent is off. When consent is on, `handle_remember_direct` already writes a memory, so the chat handler inserts a memory **and** calls `detect_action_intents`. Because `detect_action_intents` returns early on consent (line 49 of `autonomy.py`), the chat flow never proposes a memory save when the user says "remember this". The UI's "View proposed actions →" link therefore never appears for the most common case. This is a logical correctness bug in the autonomy contract: consent-on chat flows never surface an action proposal.

**Fix:** Either always propose (and let the approval gate decide), or document and test the early-return behavior. The simplest fix is to remove the `if consent: return proposals` short-circuit so that proposals are always surfaced.

### H2. Action "reject" can erase prior `result_json` — [backend/app/db.py:225-232] and [backend/app/main.py:189-194]

`update_action_status` overwrites only `status`, leaving any prior `result_json` intact. That is fine for `proposed → approved → completed`, but a user can `reject` an `approved` action that already had a partial run, or accidentally approve a `rejected` action later. More importantly, there is no audit trail for who approved/rejected (no `actions_audit` table, no user field — acceptable for a single-user app, but the lack of a terminal `cancelled` state means rejected actions linger and `update_action_status` can also flip `completed → rejected`, erasing the completed-result semantics.

**Fix:** Either forbid transitions out of `completed`/`failed` in `reject_action`, or store an `audit_log` of status transitions. Minimum fix:

```python
@app.post("/actions/{action_id}/reject")
def reject_action(action_id: int):
    action = db.get_action(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    if action["status"] not in ("proposed", "approved"):
        raise HTTPException(status_code=400, detail="Action cannot be rejected")
    db.update_action_status(action_id, "rejected")
    return {"id": action_id, "status": "rejected"}
```
becomes:

```python
    if action["status"] in ("completed", "failed", "rejected"):
        raise HTTPException(status_code=400, detail="Terminal actions cannot be rejected")
```

### H3. `AutonomyPanel` effect has empty deps but mutates in flight — [frontend/components/AutonomyPanel.tsx:30-33]

```ts
useEffect(() => {
  refresh();
}, []);
```
With React 18 + Strict Mode (which is enabled in `next.config.js`), this effect runs twice in development, doubling the initial `GET /actions` call. Combined with the approve/reject/run handlers that call `await refresh()` after the mutation but **before** the local optimistic UI updates, the user can briefly see a stale state and then a flicker. More importantly, if the user clicks Approve and then quickly navigates away, the second `await refresh()` in Strict Mode can fire against a stale closure and update `actions` after unmount (the `useCallback` deps are `[]`, so `refresh` is captured once and uses the initial closure of `setSelected`). Minor, but the empty-deps form here is wrong because `refresh` references `setSelected` whose identity is stable but the pattern itself reads as a bug to anyone reviewing.

**Fix:** Add `refresh` to deps and ensure cleanup:

```ts
useEffect(() => {
  let cancelled = false;
  (async () => {
    try {
      const data = await getActions();
      if (cancelled) return;
      setActions(data);
    } finally {
      if (!cancelled) setLoading(false);
    }
  })();
  return () => { cancelled = true; };
}, [refresh]);
```

### H4. `BuildLogPanel` writes to `localStorage` from `useEffect` on every render — [frontend/components/BuildLogPanel.tsx:23-29]

`getBuildLogs()` is called inside `useEffect` with no deps array check, but `addBuildLog` is called inside `handleSubmit` and immediately followed by `refresh()`. `refresh` reads from `localStorage`, so this works, but the form fields are cleared *before* the state is committed and there is no error handling around `addBuildLog` (which throws on quota exceeded or if `crypto.randomUUID` is unavailable in older browsers). A thrown error inside `handleSubmit` leaves the form half-cleared and the entry never persisted.

**Fix:**

```ts
const handleSubmit = () => {
  if (!built.trim() && !learned.trim()) return;
  try {
    addBuildLog({ built: built.trim(), broke: broke.trim(), learned: learned.trim(), next_mission: nextMission.trim() });
    setBuilt(""); setBroke(""); setLearned(""); setNextMission("");
    refresh();
    setMessage("Log entry saved.");
  } catch (err) {
    setMessage(err instanceof Error ? err.message : "Could not save log.");
  }
  setTimeout(() => setMessage(null), 3000);
};
```

### H5. No request size or message length validation in `/chat`, `/memory`, `/actions/propose` — [backend/app/main.py:60-100, 108-115] and [backend/app/schemas.py]

`ChatRequest.message`, `MemoryCreate.content`, and `ActionPropose.title`/`description`/`payload_json` have no `max_length` constraints. A user (or any caller, given CORS issue C1) can submit a multi-megabyte payload that gets persisted to SQLite, returned in `/memory/export`, fed verbatim into the Ollama system prompt, and re-inserted into `build_system_prompt` on every subsequent chat. This will balloon `gebo.db` and stall the export endpoint.

**Fix:** Constrain inputs in Pydantic:

```python
from pydantic import Field

class ChatRequest(BaseModel):
    message: str = Field(..., max_length=8_000)

class MemoryCreate(BaseModel):
    memory_type: str = Field("manual", max_length=64)
    content: str = Field(..., max_length=16_000)

class ActionPropose(BaseModel):
    action_type: str = Field(..., max_length=64)
    title: str = Field(..., max_length=200)
    description: str = Field(..., max_length=2_000)
    payload_json: dict[str, Any] = Field(default_factory=dict)
```
Additionally cap the response size of `get_recent_messages(20)` / `get_all_memories()` used inside `build_system_prompt`, and cap the export body.

---

## Medium

### M1. `init_db` is not idempotent against schema changes — [backend/app/db.py:25-60]

`CREATE TABLE IF NOT EXISTS` will silently skip new columns. The repo currently has no migration tooling, so any future column addition (`actions.approved_at`, `messages.tokens`, etc.) will produce a runtime error or be silently dropped depending on how it's used. Not urgent for V0, but it bites immediately on the first schema change.

**Fix:** Add a `schema_version` row in `settings` and run `ALTER TABLE` migrations, or switch to Alembic.

### M2. `autonomy.run_action` swallows tool exceptions but still raises — [backend/app/autonomy.py:235-249]

`db.update_action_result(action_id, "failed", {...})` is called inside `except`, then `raise`. The `/actions/{id}/run` endpoint then returns HTTP 500 even though the action has been correctly marked `failed` in the DB. The UI's `runAction` treats 5xx as an error and shows "Run failed", hiding the fact that the action is now in the `failed` state and viewable.

**Fix:** Either catch in the endpoint and return 200 with `status: "failed"`:

```python
@app.post("/actions/{action_id}/run")
def run_action_endpoint(action_id: int):
    action = db.get_action(action_id)
    if not action or action["status"] != "approved":
        raise HTTPException(status_code=400, detail="Action must be approved before running")
    try:
        result = autonomy.run_action(action_id)
        return {"id": action_id, "status": "completed", "result": result}
    except Exception as exc:
        return {"id": action_id, "status": "failed", "error": str(exc)}
```
or return a structured response that includes `result`.

### M3. `get_relevant_memories` falls back to *most recent* memories on no-match — [backend/app/memory.py:50-65]

When nothing scores, the function returns `reversed(all_memories[-limit:])`, i.e. the most recent memories regardless of relevance. For a memory-owned identity system, surfacing the latest memory as "relevant" will silently bias the assistant toward whatever the user just talked about, including noise captured by `auto_capture`. This is a quality, not safety, bug but it directly contradicts the README's "memory owns identity" claim.

**Fix:** Return an empty list when there is no overlap, and let the prompt's "No relevant memories recalled." placeholder take effect.

### M4. `deriveStatus` always counts the primary presence "Awake" once message_count > 0 — [frontend/lib/presences.ts:5-25]

```ts
if (presenceId === "gebo") {
  if (status.message_count > 0) return "Awake";
  ...
}
```
This collapses any session with at least one message into "Awake" forever, even after a long idle. The "Resting" state is unreachable in practice once a user has chatted. Cosmetic, but it's also used in `deriveGeboStatus` to drive the pulse indicator.

**Fix:** Track `last_message_at` (already available — `messages.created_at`) and consider a recency window (e.g. "Awake" only if last message within 30 minutes).

### M5. Frontend Dockerfile copies full `node_modules` from builder — [frontend/Dockerfile:24-27]

```dockerfile
COPY --from=builder /app/node_modules ./node_modules
```
The runner image gets the builder's full `node_modules` (including dev deps), doubling image size and shipping `typescript`, `@types/*`, etc. into production. Use a `npm ci --omit=dev` step or copy `package-lock.json` and reinstall in the runner.

**Fix:**

```dockerfile
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY package*.json ./
RUN npm ci --omit=dev
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY next.config.js ./
EXPOSE 3000
CMD ["npm", "start"]
```

### M6. `GeboProvider` polls every 10s and never cancels in-flight requests — [frontend/lib/GeboProvider.tsx:96-100]

If the backend is slow or down, overlapping `checkBackendOnline` + `getStatus` + `getMemories` chains pile up. AbortController would prevent stale responses from clobbering fresh ones.

**Fix:** Add an `AbortController` per poll and abort in the interval reset.

### M7. SQLite database shipped in repo (`backend/data/gebo.db`) — [backend/data/gebo.db:28672 bytes]

`backend/data/gebo.db` is committed to the workspace, while `.gitignore` excludes `backend/data/gebo.db`. That is a contradiction — the file is present despite being ignored, which means it was committed before the gitignore rule. This is a privacy leak risk: any clone of the repo includes the developer's stored memories, messages, and consent settings.

**Fix:** Delete the tracked file (`git rm --cached backend/data/gebo.db` and remove from disk), and confirm `.gitignore` excludes `backend/data/*.db`.

### M8. No `Authorization` on action endpoints — [backend/app/main.py:174-221]

Anyone who can reach the backend can approve, reject, and run any action. The README emphasizes "Bb approves before anything runs", which is a UI-level approval. If the backend is ever exposed (CORS issue C1 makes this easy), the approval gate is purely cosmetic. Not urgent for localhost-only use, but worth a sticky note in the code that these are unauthenticated.

**Fix:** Add a shared `GEBO_API_TOKEN` env var and a FastAPI dependency that checks `Authorization: Bearer …` on write paths (`/chat`, `/memory`, `/actions/*`, `/settings/consent`).

---

## Low

### L1. `chat` mode prefix duplicates when user re-sends — [frontend/components/ChatPanel.tsx:35-45]

`getPrefixedMessage` checks `text.toLowerCase().startsWith(m.prefix.toLowerCase().trim())`. The prefix `Remember: ` trimmed lower is `remember:`, but the stored text might already start with `Remember` (no colon). On a re-send or retry the user will see `Remember: Remember: foo`. Minor UX.

**Fix:** Match the prefix including the trailing colon and case-insensitively after trimming both sides.

### L2. `_summarize_messages` uses `[-20:]` after a join — [backend/app/autonomy.py:139-147]

If `messages[-20:]` has fewer than 20 messages, the slice is harmless. But the prior `lines = [f"[{m['role']}] {m['content']}" for m in messages]` is built from the full `limit` (default 30), then truncated. Memory churn on large conversations is wasted.

**Fix:** Truncate first, then join.

### L3. `STATUS_RESPONSE` schema in `lib/types.ts` diverges from backend — [frontend/lib/types.ts:51-62]

The frontend `Status` interface matches the backend `StatusResponse` *today*, but the backend returns plain JSON without `presence` arrays. The frontend then derives `presences` client-side from memory content, which is brittle and produces nonsense for short-form memories. Already noted in M4; flagged here so it's visible in a types diff.

### L4. `CHAT_DRAFT_KEY` and `COMMAND_DRAFT_KEY` are exported but unused — [frontend/lib/constants.ts:103-105]

`CHAT_DRAFT_KEY` is defined in `constants.ts` but never read by any component. `COMMAND_DRAFT_KEY` is read in `TopCommandBar` (writes to `gebo-chat-pending`, reads `COMMAND_DRAFT_KEY`). Dead constants invite future bugs when someone assumes they are wired up.

**Fix:** Either use `CHAT_DRAFT_KEY` in `ChatPanel` for textarea autosave, or remove it.

### L5. `MemoryCard` Archive/Delete buttons are disabled placeholders — [frontend/components/MemoryCard.tsx:75-92]

Buttons are rendered disabled with tooltips explaining that the backend lacks the endpoints. This is honest, but it makes the UI feel broken. Either remove the buttons or hide them entirely (e.g. `{false && (<button>...</button>)}`).

### L6. README claims `.gitignore` ignores `backend/data/gebo.db` but it is present — see M7

Same root cause as M7; mentioning here so the docs/UX side is captured separately.

### L7. `pip` and `npm install` produce un-pinned versions — [backend/requirements.txt, frontend/package.json]

`fastapi>=0.115.0`, `next ^14.2.0`, etc. A future major release of FastAPI or Next will break the app without warning. The lockfiles exist (`backend/.venv/...` resolved, `frontend/package-lock.json`); pin runtime deps to the lockfile resolutions for reproducible builds.

**Fix:**

```
fastapi==0.115.6
uvicorn[standard]==0.32.1
httpx==0.27.2
pydantic==2.9.2
python-dotenv==1.0.1
```
and similarly constrain `next`, `react`, etc.

### L8. No backend or frontend tests — [backend/app/**, frontend/{app,components,lib}/**]

There are zero tests. The autonomy / approval flow is exactly the surface that benefits most from tests (proposal generation, state transitions, rejection gates). Add at minimum:
- pytest tests for `autonomy.detect_action_intents`, `db.update_action_status`, `run_action` failure path.
- React Testing Library tests for `AutonomyPanel` state transitions and `MemoryPanel` filtering.

---

## Summary of severity counts

- Critical: 1 (CORS)
- High: 5 (autonomy contract, terminal action transitions, React effect deps, localStorage write race, no input size limits)
- Medium: 8 (migrations, error swallowing, relevance fallback, presence status, Docker image size, polling, tracked DB file, no auth)
- Low: 8 (small UX/dx/cleanup items)

The codebase is small, readable, and clearly scoped. The architecture and the autonomy/approval model are sound; the issues above are the standard rough edges of a v0 of a privacy-sensitive app, and most are localized fixes.