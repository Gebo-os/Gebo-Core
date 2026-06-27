# CLI Toolkit

Gebo scans and reports local CLIs via `GET /cli/status`.

## Activate / verify

```powershell
.\scripts\gebo-activate-clis.ps1
```

## Catalog

| CLI | Role |
|-----|------|
| Ollama | Local model inference |
| Codex | Code review/build (approval-gated) |
| GitHub CLI (`gh`) | Repo operations |
| Firebase CLI | Consumer app deploy |
| Google Cloud (`gcloud`) | Cloud deploy |
| Azure CLI (`az`) | Cloud deploy |
| Docker | Container deploy |
| Node/npm/Python | Runtime |

## Install hints

The activate script prints install commands for missing tools. xAI CLI:

```powershell
irm https://x.ai/cli/install.ps1 | iex
```

Codex:

```powershell
npm install -g @openai/codex
```
