# Gebo Owner NODE — Design System (Stitch / DESIGN.md)

> Source of truth for Google Stitch, Cursor, and any AI design agent working on this UI.

## Product

**Gebo Living Console** — private, local-first AI command center for a single owner (Bb).  
Stack: Next.js 14 App Router, React, plain CSS (no Tailwind). Backend: FastAPI + Ollama on `:8000`.

## Brand

- **Name:** Gebo OS · Owner NODE
- **Tone:** Calm, technical, trustworthy — a personal operating system, not a SaaS dashboard
- **Primary mark:** Letter **G** in a pulsing ring emblem
- **Tagline:** Memory, presence, and safe autonomy

## Color palette (CSS variables)

| Token | Hex | Use |
|-------|-----|-----|
| `--bg-base` | `#050505` | Page background |
| `--bg-elevated` | `#0c0c0c` | Sidebar |
| `--bg-panel` | `#111111` | Cards / widgets |
| `--green` | `#3dff6e` | Primary accent, live indicators |
| `--green-dim` | `#2ecc55` | Focus rings, secondary accent |
| `--text-primary` | `#f0f0f0` | Headings, body |
| `--text-secondary` | `#9a9a9a` | Labels |
| `--text-tertiary` | `#666666` | Hints, placeholders |
| `--danger` | `#e85555` | Errors |
| `--warning` | `#d4a017` | Warnings |
| `--info` | `#5b9bd5` | Info badges |

Light theme: `[data-theme="light"]` inverts to soft grays with same green accent.

## Typography

- **UI:** Inter, Segoe UI, system-ui — 15px base, line-height 1.55
- **Mono:** Cascadia Code, Consolas — code and timestamps
- **Scale:** Widget titles 0.85rem uppercase tracking; page titles 1.75rem

## Spacing & layout

- Sidebar: 240px fixed left
- Top bar: 56px
- Command dock: 64px bottom
- Content max-width (inner pages): 1120px
- Pulse dashboard: full-width 3-column grid (left / center emblem / right)
- Border radius: 6px (sm), 10px (md), 14px (lg)

## Shell structure

```
┌──────────┬─────────────────────────────────────────────┬─────────────┐
│ Sidebar  │ Top tabs (Command, Compute, Memory, …)    │             │
│ 11 items │ Model badge · icons · theme · clock         │  Assistant  │
│          ├─────────────────────────────────────────────┤    Rail     │
│          │ Main content (Pulse grid OR page panel)     │ Quick cmds  │
│          ├─────────────────────────────────────────────┤             │
│          │ Command dock: Ask Gebo anything…            │             │
└──────────┴─────────────────────────────────────────────┴─────────────┘
```

## Routes (must all be functional)

| Route | Purpose |
|-------|---------|
| `/` | Pulse Command Center — live widgets |
| `/chat` | Memory-aware chat (streaming) |
| `/studio` | AI Studio — chat in Build mode |
| `/memory` | View, search, add, export memories |
| `/presences` | Ecosystem beings (Gebo, LockIn, Dream, …) |
| `/actions` | Approve/reject proposed actions |
| `/reflexes` | Pattern automation |
| `/evolution` | Self-improvement loop |
| `/build-log` | Project journal |
| `/settings` | Consent, network, model, export |

## Components

### Widgets (`OsWidget`)
System Overview, Compute Grid, Memory Fabric, Global Network, Intelligence Feed, AI Orchestration, Device Continuity, Security — all must use **real API data** from `GeboProvider`, not fake metrics.

### Chat
Modes: Ask, Remember, Plan, Build, Search Memory. Streaming via SSE. Command dock and quick commands queue prompts into chat.

### States
- **Offline:** Red strip when backend `:8000` unreachable
- **Loading:** Skeleton on Pulse until bootstrap completes
- **Empty:** EmptyState on lists with clear CTA

## Interaction rules (functionability)

1. Every nav item goes to a distinct, working screen
2. Quick commands either navigate OR pre-fill chat with a prompt
3. Dashboard widget links go to the screen that controls that subsystem
4. Notification badge = count of pending + approved actions
5. Device continuity shows **real presence names**, not placeholder “GPhone” labels
6. Assistant rail controls **motion/animations** (real setting), not fake “listening”
7. No disabled buttons without explanation; remove dead controls
8. Export buttons use fetch+blob download pattern

## Accessibility

- Focus-visible green outline
- `aria-label` on icon-only controls
- `role="log"` on chat stream
- Sidebar `aria-current="page"` on active link

## Files map

| Area | Path |
|------|------|
| Shell | `components/GeboOsShell.tsx` |
| Dashboard | `components/OsDashboard.tsx`, `PulseCommandCenter.tsx` |
| Chat | `components/ChatPanel.tsx` |
| Nav config | `lib/osNav.ts` |
| Global state | `lib/GeboProvider.tsx` |
| Styles | `app/globals.css` (~3500 lines, `.os-*` namespace) |

## Stitch redesign goals

1. Keep dark OS aesthetic and green accent — refine, don’t rebrand
2. Make every visible control do something real (see Interaction rules)
3. Reduce visual noise on Pulse; prioritize actionable metrics
4. Unify Chat and Studio without duplicate sidebar entries feeling broken
5. Mobile: collapse sidebar + dock into bottom nav (future)
6. Export production-ready React/HTML that maps to existing routes and API
