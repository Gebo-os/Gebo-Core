# Gebo Gym

**Official training algorithm for Gebo Core (Owner NODE).**

Gebo Gym is how Bb's private intelligence **learns, grows, evolves, and repeats** — without autopilot writes or cloud dependency.

---

## The loop

```
Learn  →  Grow  →  Act  →  Verify  →  Repeat
```

| Phase | What | Where |
|-------|------|--------|
| **Learn** | Index GitHub + local git repos into `project` memory (read-only) | `gebo-gym.ps1` |
| **Grow** | Chat — recall, wiki, strategic dialogue | Living Console → Chat |
| **Act** | Approve proposed actions (plan, summarize, Codex review/build) | Actions |
| **Verify** | Backend pytest — stack health check | `gebo-gym.ps1` |
| **Repeat** | Run Gebo Gym again after pushes, merges, or when context feels stale | `gebo-gym.ps1` |

Automated phases: **Learn**, **Verify**, **Repeat**.  
Human phases: **Grow**, **Act** (approval-gated by design).

---

## Run Gebo Gym

One command from the repo root:

```powershell
.\scripts\gebo-gym.ps1
```

Alias (same script):

```powershell
.\scripts\evolve.ps1
```

**First time:** authenticate GitHub for full repo coverage:

```powershell
gh auth login
```

Without `gh`, Gebo Gym still learns from local git repos under Desktop and `.agents`.

---

## Rules (keep these)

1. **Read-only ingest** — Gebo Gym never pushes or edits GitHub.
2. **Upsert, don't duplicate** — re-running updates existing project memories by repo URL/path.
3. **Approval before action** — Grow and Act stay in the console; no silent autonomy.
4. **Local memory is truth** — `backend/data/gebo.db` is yours; not in git.
5. **Repeat beats perfection** — small loops compound; run the gym often.

---

## When to run

- After you push to `Gebo-os/Gebo-Core`
- After layering a new repo into memory
- Weekly rhythm, or whenever chat feels under-informed
- Before a Codex review/build action you intend to approve

---

## Identity

Gebo Gym is not a product feature name in the UI — it is **Bb's training ritual** for the Owner NODE. Keep it.
