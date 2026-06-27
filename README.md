# Gebo Core Private

Private full-stack local AI memory app for Bb — **Owner NODE V0**.

**Official master law:** [`GEBO-ECOSYSTEM-MASTER.md`](GEBO-ECOSYSTEM-MASTER.md)

**Stack:** Next.js + FastAPI + SQLite + Ollama (llama3.2:3b)

Presence is identity. Memory is continuity. Owner Node is authority. The model generates responses. Actions require approval.

---

## Prerequisites (Windows)

1. **Python 3.11+** — [python.org](https://www.python.org/downloads/)
2. **Node.js 20+** — [nodejs.org](https://nodejs.org/)
3. **Ollama** — [ollama.com](https://ollama.com/download)

---

## 1. Install Ollama model

Open PowerShell:

```powershell
ollama pull llama3.2:3b
```

## 2. Test Ollama

```powershell
ollama run llama3.2:3b
```

Type a test message, then exit with `/bye` or Ctrl+D.

Make sure the Ollama app is running in the background before using Gebo.

---

## 3. Run backend

```powershell
cd gebo-core-private\backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend: http://127.0.0.1:8000  
Health check: http://127.0.0.1:8000/health

---

## 4. Run frontend

Open a **new** PowerShell window:

```powershell
cd gebo-core-private\frontend
npm install
npm run dev
```

Frontend: http://localhost:3000

---

## 5. Open app

**One command (WiFi + LAN — recommended):**

```powershell
.\scripts\start-gebo.ps1
```

Browser: **http://localhost:3000** (this PC) or **http://YOUR_LAN_IP:3000** (phone/tablet).

Other modes: `.\scripts\start-gebo.ps1 -Mode localhost` or `-Mode desktop`.

**Consumer / white-label integration:** see [`CONSUMER-APP.md`](CONSUMER-APP.md).

Or launch as a **desktop app** (Electron window):

```powershell
.\scripts\start-gebo-desktop.ps1
```

See `desktop/README.md` for details.

1. Click **Allow Memory Collection** to enable auto-memory capture.
2. Chat with Gebo.
3. Add manual memories in the Memory panel.
4. Approve and run proposed actions in the Autonomy panel.
5. Use **Export Memory** to download all data as JSON.

---

## 6. GitHub (optional)

```powershell
cd gebo-core-private
git init
git add .
git commit -m "Initial Gebo Core private app"
```

---

## 7. Docker

```powershell
cd gebo-core-private
docker compose up --build
```

**Note:** Ollama is not containerized. Run Ollama on the host.

For Docker on Windows, set in `.env`:

```
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

Local (non-Docker) uses:

```
OLLAMA_BASE_URL=http://localhost:11434
```

---

## Environment

Copy `.env.example` to `.env` at the repo root:

```
OLLAMA_MODEL=llama3.2:3b
OLLAMA_BASE_URL=http://localhost:11434
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Backend-only `.env` in `backend/`:

```
OLLAMA_MODEL=llama3.2:3b
OLLAMA_BASE_URL=http://localhost:11434
```

---

## GitHub repo memory (read-only)

Gebo can index GitHub repos into local memory without editing GitHub.

1. Authenticate (one time):

```powershell
gh auth login
```

2. Ingest repos into Gebo memory:

```powershell
cd backend
.\.venv\Scripts\activate
python scripts\ingest_repo_memory.py
```

This reads repo metadata and README excerpts only. Nothing is pushed or modified on GitHub.

If `gh` is not logged in, the script falls back to local git repos under Desktop and `.agents`.

Re-ingest **updates** existing project memories (same repo URL/path) instead of duplicating.

See also: `AUDIT.md` for security review.

---

## Gebo Gym (official training algorithm)

**Learn → Grow → Act → Verify → Repeat**

Gebo Gym is Bb's training loop for the Owner NODE — how Gebo learns from repos, grows through chat, acts with approval, verifies with tests, and repeats.

```powershell
.\scripts\gebo-gym.ps1
```

| Phase | Automated? | What |
|-------|------------|------|
| Learn | Yes | Repo ingest → project memory |
| Grow | Console | Chat with recall + wiki |
| Act | Console | Approve actions / Codex tasks |
| Verify | Yes | `pytest -q` |
| Repeat | Yes | Run Gebo Gym again |

Full spec: [`GEBO-GYM.md`](GEBO-GYM.md)

---

## Gebo Reflex Engine

Memory-aware automation — pattern → proposal → approval → execution → stronger memory.

- Page: `/reflexes`
- Spec: [`GEBO-REFLEX-ENGINE.md`](GEBO-REFLEX-ENGINE.md)
- Pairs with Gebo Gym: Gym ingests repos; Reflexes detect chat patterns

---

## Gebo Evolution Loop

Behavioral self-improvement — score outcomes, learn patterns, propose upgrades (reflex / tool / agent).

- Page: `/evolution`
- Spec: [`GEBO-EVOLUTION-LOOP.md`](GEBO-EVOLUTION-LOOP.md)
- Stack: Memory → Actions → Reflexes → **Evolution** → (Throne, planned)

---

## Offline knowledge wiki (free, local)

Gebo can consult a free offline knowledge base (a Kiwix **ZIM** file, e.g. Wikipedia)
when a question has no matching memory. It is fully local — no internet is used at
query time.

1. Install the reader (already in `requirements.txt`):

```powershell
cd backend
.\.venv\Scripts\pip install libzim
```

2. Download a free ZIM from https://download.kiwix.org/zim/ and place it in
   `backend/data/wiki/`. Good starter options:

| ZIM | Size | Notes |
|-----|------|-------|
| `wikipedia_en_100_nopic` | ~300 MB | Tiny sample for testing |
| `wikipedia_en_simple_all_nopic` | ~1 GB | Simple English Wikipedia, no images |
| `wikipedia_en_all_nopic` | ~50 GB | Full English Wikipedia, no images |

Gebo auto-detects the first `*.zim` file in `backend/data/wiki/`. Or set an explicit
path with `WIKI_ZIM_PATH` in `.env`.

3. Restart the backend. Check status at `GET /wiki/status` or the Settings page.

Config (in `backend/.env`):

- `WIKI_ENABLED=true`
- `WIKI_AUTO=nocontext` — consult only when no memory matches (`always` or `off` also valid)
- `WIKI_RESULTS=3` — number of articles to reference

The ZIM must have a full-text index (most Wikipedia ZIMs do). Files in
`backend/data/wiki/` are git-ignored.

---

## Backend tests

```powershell
cd backend
.\.venv\Scripts\python -m pytest -q
```

Tests use an isolated temp SQLite database and mock Ollama — they never touch `data/gebo.db`.

---

## Custom Gebo model (Ollama)

Gebo ships a **Modelfile** that bakes in Presence law, memory-first behavior, and approval-gated actions.

```powershell
# From repo root — pulls llama3.2:3b, creates gebo-custom
.\scripts\create-gebo-model.ps1
```

Then in `backend/.env`:

```
OLLAMA_MODEL=gebo-custom
```

Restart the backend. Chat will use your custom Gebo personality instead of raw Llama.

Edit `models/Gebo.Modelfile` to tune voice, temperature, or base model (`FROM llama3.2:3b` → any Ollama model you have).

---

## Parallel agents + Codex

The **agent runtime** ticks all active registry agents **in parallel** (thread pool). A **Codex lane** runs alongside each cycle:

- Status ping every 30s (version, workdir)
- Light parallel audit ~every 10 minutes when Codex CLI is installed
- Heavy Codex build/review tasks remain **approval-gated** via Actions

Check status: `GET /agents/runtime/status` or **Settings → Agent Runtime**.

Verify everything in parallel:

```powershell
.\scripts\gebo-parallel-verify.ps1
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| **Ollama not running** | Start Ollama app. Run `ollama list` to verify. |
| **Model not pulled** | Run `ollama pull llama3.2:3b` |
| **Backend port busy** | Stop other apps on port 8000, or change port in uvicorn command |
| **Frontend port busy** | Run `npm run dev -- -p 3001` and open http://localhost:3001 |
| **Docker cannot reach Ollama** | Use `OLLAMA_BASE_URL=http://host.docker.internal:11434` |
| **Chat returns 503** | Ollama unreachable — check it's running and model is installed |

---

## Project structure

```
gebo-core-private/
  backend/                    FastAPI + SQLite + Ollama + Autonomy
  frontend/                   Next.js Living Console
  scripts/                    gebo-gym.ps1 — training ritual
  GEBO-ECOSYSTEM-MASTER.md    Official master prompt (canonical law)
  prompts/01-gebo-lattice-prompting.md   Expert prompting style #01
  memory/core/00-default-gebo-build-prompt.md   Core memory #00
  GEBO-GYM.md                 Training algorithm
  GEBO-REFLEX-ENGINE.md       Memory-aware reflex automation
  GEBO-EVOLUTION-LOOP.md      Behavioral self-improvement
  docker-compose.yml
  README.md
```

---

## Gebo identity

Gebo Core is Bb's private intelligence layer — calm, direct, strategic, memory-aware, approval-based.

Full ecosystem law: [`GEBO-ECOSYSTEM-MASTER.md`](GEBO-ECOSYSTEM-MASTER.md)

| Invention | Spec |
|-----------|------|
| Gebo Gym | [`GEBO-GYM.md`](GEBO-GYM.md) |
| Reflex Engine | [`GEBO-REFLEX-ENGINE.md`](GEBO-REFLEX-ENGINE.md) |
| Evolution Loop | [`GEBO-EVOLUTION-LOOP.md`](GEBO-EVOLUTION-LOOP.md) |
| Lattice Prompting #01 | [`prompts/01-gebo-lattice-prompting.md`](prompts/01-gebo-lattice-prompting.md) |
| Core memory #00 | [`memory/core/00-default-gebo-build-prompt.md`](memory/core/00-default-gebo-build-prompt.md) |

Gebo helps build: Gebo OS, Owner Node, Memory Continuity API, Presence Architecture, Dream, Mya, LockIn, Slatt Tool, Sleep, Future Presences.

# Gebo-Core
