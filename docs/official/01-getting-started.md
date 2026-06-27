# Getting Started

## Prerequisites

- Python 3.11+, Node.js 20+, Ollama, Git

## One-command bootstrap

```powershell
cd gebo-core-private
.\scripts\gebo-os-bootstrap.ps1
```

This runs: custom model check → CLI scan → knowledge collect → start WiFi mode.

## Manual start

```powershell
.\scripts\start-gebo.ps1              # WiFi + LAN
.\scripts\start-gebo.ps1 -Mode localhost
```

## First actions

1. **Allow Memory Collection** (Settings)
2. **Enable Full Internet Access** if using LAN/phone clients
3. Run **Learning cycle**: Settings → Integrations & Learning → Run Learning Cycle
4. Chat on **Pulse** or **Chat** — model badge shows `gebo-custom` in top bar

## Private documents

Copy your files to `backend/data/private-docs/` then run:

```powershell
.\scripts\gebo-knowledge-collect.ps1
```
