# Gebo Evolution Loop

**Official invention — behavioral self-improvement for Gebo Core (Owner NODE).**

Sits above **Reflex Engine**. Connects toward **Throne Engine** (governor, planned).

| Layer | Role |
|-------|------|
| Memory | Identity |
| Actions | Hands |
| Approval Gate | Control |
| Reflex Engine | Nervous system |
| Throne Engine | Governor (planned) |
| **Evolution Loop** | **Self-improvement** |

> Reflex Engine reacts. Evolution Loop learns what works and upgrades the system over time.

**Not model training** — this is **behavioral evolution**.

---

## Core cycle

```text
Observe → Decide → Propose → Approve → Execute → Reflect → Score → Upgrade → Remember
```

Gebo tracks:
- What did I try?
- Did it work?
- Did Bb approve it?
- Did it help the mission?
- Should this become a reflex, tool, or agent?

---

## Features

### 1. Outcome Memory
Every completed action can be scored. Lessons saved to `evolution_events` and system memory.

### 2. Autonomy Scoring
Seven dimensions (1–10): mission, speed, risk, approval, memory, product, money → `total_score`.

### 3. Pattern Upgrades
Repeated action types (≥3 completed) auto-suggest reflex/tool/agent upgrades.

### 4. Tool & Agent Birth
Upgrade types: `reflex`, `tool`, `agent`, `memory_rule`, `ui_improvement`, `backend_improvement`, `prompt_improvement`, `workflow_improvement`.

All upgrades require **Bb approval** before build actions are proposed.

---

## API

| Endpoint | Method |
|----------|--------|
| `/evolution/status` | GET |
| `/evolution/events` | GET |
| `/evolution/scores` | GET |
| `/evolution/upgrades` | GET |
| `/evolution/score-action` | POST |
| `/evolution/suggest-upgrade` | POST |
| `/evolution/upgrades/{id}/approve` | POST |
| `/evolution/upgrades/{id}/reject` | POST |

---

## UI

**Living Console → Evolution** (`/evolution`)

- Autonomy score cards
- Score action panel
- Upgrade suggestions (approve / reject)
- Evolution timeline
- Manual upgrade proposals

Sidebar: … Actions · Reflexes · **Evolution** · Build Log · Settings

---

## Run

```powershell
cd backend
.\.venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8000

cd frontend
npm run dev

cd backend
.\.venv\Scripts\python -m pytest -q
```

Open http://localhost:3000/evolution

Pairs with **Gebo Gym** (`GEBO-GYM.md`) and **Reflex Engine** (`GEBO-REFLEX-ENGINE.md`).
