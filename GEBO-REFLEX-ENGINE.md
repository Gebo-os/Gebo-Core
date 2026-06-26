# Gebo Reflex Engine

**Official invention — memory-aware automation for Gebo Core (Owner NODE).**

Not n8n. Not basic trigger→action. Gebo builds **reflexes**.

> When Gebo detects a pattern → proposes the right action → Bb approves → Gebo executes → memory updates → the reflex gets smarter.

---

## Loop

```text
Memory → Pattern → Intention → Proposed Action → Approval → Execution → Reflection → Stronger Memory
```

Works with **Gebo Gym** (`GEBO-GYM.md`): Gym learns from repos; Reflexes learn from conversation patterns.

---

## Default reflexes

1. **Memory Capture Reflex** — important statements → save memory proposal
2. **Build Log Reflex** — progress/bugs/UI → build log + follow-up plan
3. **Mission Drift Reflex** — tangents → mission warning note
4. **Action Queue Reflex** — build/change/fix requests → proposed plan
5. **Daily Continuity Reflex** — day summaries → conversation summary memory
6. **Presence Activation Reflex** — focus/planning/creative cues → presence suggestion

All default to **approval required**.

---

## API

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/reflexes` | GET | List reflexes + last used |
| `/reflexes` | POST | Create custom reflex |
| `/reflexes/{id}/toggle` | POST | Enable / disable |
| `/reflex-events` | GET | Detection history |

`/chat` returns `detected_reflexes` alongside `proposed_actions`.

---

## UI

**Living Console → Reflexes** (`/reflexes`)

- Engine status
- Active reflex cards (toggle, trigger, action, approval badge, last used)
- Reflex history
- Create new reflex

Sidebar order: Pulse · Chat · Memory · Presences · Actions · **Reflexes** · Build Log · Settings

---

## Safety

- No shell commands from reflexes
- No internet access
- No GitHub pushes
- No silent execution on major reflexes (approval required by default)
- Safe internal tools only (`save_memory`, `write_project_note`, `create_plan`, `summarize_recent_messages`)

---

## Run

```powershell
# Backend
cd backend
.\.venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8000

# Frontend
cd frontend
npm run dev

# Tests
cd backend
.\.venv\Scripts\python -m pytest -q
```

Open http://localhost:3000/reflexes

Try in Chat:

```text
I fixed the frontend today but the memory page still looks weak.
```

Gebo should detect **Build Log Reflex** and propose actions for approval.
