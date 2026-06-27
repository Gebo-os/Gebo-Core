# Gebo OS Official Documentation

**Version:** 0.9.0 (Owner NODE V0)  
**Status:** Release candidate — local-first, approval-gated autonomy

## Document index

| Doc | Audience | Purpose |
|-----|----------|---------|
| [MICRO-WORKFLOW.md](./MICRO-WORKFLOW.md) | Operators | Step-by-step daily workflow |
| [01-getting-started.md](./01-getting-started.md) | Everyone | Install and first run |
| [02-architecture.md](./02-architecture.md) | Developers | System design |
| [03-learning-system.md](./03-learning-system.md) | Operators | Knowledge collection |
| [04-integrations.md](./04-integrations.md) | Developers | Google, OSS, connectors |
| [05-cli-toolkit.md](./05-cli-toolkit.md) | Operators | CLI activation |
| [06-consumer-app.md](./06-consumer-app.md) | Ship team | Consumer SDK |

## Master law

All Gebo OS behavior is governed by [`GEBO-ECOSYSTEM-MASTER.md`](../../GEBO-ECOSYSTEM-MASTER.md).

## Principles

1. **Local-first** — Ollama (`gebo-custom`) is the default brain.
2. **Approval-gated** — Actions, Codex writes, and connectors require explicit approval.
3. **Learn then integrate** — Public docs and OSS patterns enter memory; APIs need credentials.
4. **Agents are silent** — Registry runs in backend; never shown in public consumer UI.
5. **Presence is identity** — User-facing AI is Presences, not raw agent threads.

## Quick start

```powershell
.\scripts\gebo-os-bootstrap.ps1
```

Open **http://localhost:3000** or **http://YOUR_LAN_IP:3000** on WiFi.
