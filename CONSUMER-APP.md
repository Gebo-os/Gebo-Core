# Gebo Consumer App Integration

How to embed or ship Gebo Core as a consumer-facing app (mobile shell, Electron, PWA, or white-label).

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Consumer shell (your app)                              │
│  import { geboClient } from "@/lib/geboClient"          │
└───────────────────────────┬─────────────────────────────┘
                            │ HTTP (LAN or localhost)
┌───────────────────────────▼─────────────────────────────┐
│  Gebo Backend (FastAPI :8000)                           │
│  GET /integrate/bootstrap  ← single startup call        │
│  POST /chat, /memory, /actions, …                       │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│  Ollama (local model, e.g. gebo-custom)                 │
└─────────────────────────────────────────────────────────┘
```

## Quick start (owner / dev)

```powershell
# WiFi + LAN (phones/tablets on same network) — default
.\scripts\start-gebo.ps1

# Localhost only
.\scripts\start-gebo.ps1 -Mode localhost

# Electron desktop window
.\scripts\start-gebo.ps1 -Mode desktop
```

## Bootstrap API (consumer contract)

**`GET /integrate/bootstrap`** returns everything needed to render the shell:

| Field | Purpose |
|-------|---------|
| `version` | Gebo API version |
| `status.model` | Active local Ollama model (e.g. `gebo-custom`) |
| `network` | LAN URLs, CORS mode, bind host |
| `codex` | Codex CLI availability |
| `wiki` | Offline wiki status |
| `agent_runtime` | Parallel agents + Codex lane |
| `capabilities` | Feature flags for UI gating |

Example:

```bash
curl http://127.0.0.1:8000/integrate/bootstrap
```

## Frontend SDK

```typescript
import { geboClient, loadSession } from "@/lib/geboClient";

// Full session (bootstrap + memories) — 2 parallel calls
const { online, bootstrap, memories } = await loadSession();
if (online && bootstrap) {
  console.log(bootstrap.status.model);   // gebo-custom
  console.log(bootstrap.network.backend_url);
  console.log(bootstrap.capabilities.codex);
}
```

**API URL on LAN:** `getApiUrl()` resolves from `window.location.hostname:8000` when no `NEXT_PUBLIC_API_URL` is set — phones on WiFi work without hardcoding IP.

## Environment

| Variable | Consumer use |
|----------|----------------|
| `NEXT_PUBLIC_API_URL` | Override API base (production builds) |
| `OLLAMA_MODEL` | Local model name (default `gebo-custom`) |
| `GEBO_BIND_HOST` | `0.0.0.0` for LAN |
| `GEBO_VERSION` | Reported in bootstrap |

Copy `backend/.env.example` and `frontend/.env.example` for full list.

## Custom local model

```powershell
.\scripts\create-gebo-model.ps1
# Set OLLAMA_MODEL=gebo-custom in backend/.env
```

Model appears in the OS shell top bar and Settings.

## External tools (optional)

| Tool | Install | Gebo use |
|------|---------|----------|
| **Codex CLI** | `npm install -g @openai/codex` | Approval-gated code review/build via Actions |
| **xAI CLI** | `irm https://x.ai/cli/install.ps1 \| iex` | Optional Grok CLI alongside Codex |
| **Ollama** | [ollama.com](https://ollama.com) | Required — local inference |

Codex reviews: use scoped paths or `.codexignore` — never scan `backend/.venv`.

## Docker (consumer deploy)

```powershell
docker compose up --build
```

Set `NEXT_PUBLIC_API_URL` to the host IP clients will use.

## Screens (Living Console)

All routes share `GeboOsShell` — Pulse, Chat, Memory, Actions, Build Log, Presences, Reflexes, Evolution, Settings.

## Security notes for consumer ship

- No API auth today — bind to LAN only or add auth before public deploy.
- Actions and Codex writes are **approval-gated**.
- Agents are backend-only; never exposed in public UI.

## Verification

```powershell
.\scripts\gebo-parallel-verify.ps1
cd backend; $env:GEBO_TESTING="true"; .\.venv\Scripts\python.exe -m pytest tests/ -q
cd frontend; npm run build
```
