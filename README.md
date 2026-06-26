# Gebo Core Private

Private full-stack local AI memory app for Bb.

**Stack:** Next.js + FastAPI + SQLite + Ollama (llama3.2:3b)

Memory owns identity. The model generates responses. Actions require approval.

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

Browser: **http://localhost:3000**

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

See also: `AUDIT.md` for security review.

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
  backend/          FastAPI + SQLite + Ollama + Autonomy
  frontend/         Next.js dashboard
  docker-compose.yml
  README.md
```

---

## Gebo identity

Gebo Core is Bb's private intelligence layer — calm, direct, strategic, memory-aware, approval-based.

Gebo helps build: Gebo OS, Owner Node, Memory Continuity API, Presence Architecture, Dream, Mya, LockIn, Slatt Tool, Sleep, Future Presences.

# Gebo-Core
