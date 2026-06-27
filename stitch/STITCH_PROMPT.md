# Paste this into Google Stitch (stitch.withgoogle.com)

Open [Google Stitch](https://stitch.withgoogle.com/), create a project named **Gebo Owner NODE**, upload `current-ui-snapshot.html` from this folder, attach `../frontend/DESIGN.md` as context, then paste the prompt below.

---

## Prompt for Stitch

You are the UX designer for **Gebo Owner NODE** — a private local AI command center (Next.js + FastAPI + Ollama). I am giving you our current UI as HTML/CSS context plus DESIGN.md.

**Your job:** Redesign this interface so every control is **functional and honest** — not a decorative mockup. Keep the dark “Gebo OS” aesthetic (black panels, `#3dff6e` green accent, Inter font, pulsing G emblem).

### What we have today

- Full-screen OS shell: left sidebar (11 items), top tab bar, center content, right assistant rail, bottom command dock
- Pulse home (`/`) with 8 dashboard widgets fed by live API data
- Chat with streaming, 5 modes, memory recall
- Memory, Presences, Actions, Reflexes, Evolution, Build Log, Settings pages — all wired to backend

### Problems to fix in your redesign

1. **Duplicate nav** — “Chat” and “AI Studio” felt like the same screen; Studio should be a distinct creation workspace (`/studio`, Build mode default)
2. **Fake affordances** — “Stop Listening” did nothing; replace with real controls (e.g. pause animations / open chat)
3. **Placeholder devices** — “GPhone, GBook Pro” should show real presence names (Gebo, LockIn, Dream, Mya, Slatt)
4. **Decorative metrics** — Temperature, fake TB/s bandwidth, inflated node counts confuse users; show only data we can compute from API or label as estimates
5. **Quick commands** — must either navigate to the right page OR queue a chat prompt (Summarize Activity, Generate Report)
6. **Notification bell** — should reflect pending action count, link to `/actions`
7. **Intelligence feed items** — should link to Memory
8. **Widget CTAs** — every “Open X →” link must go to the screen that controls that subsystem

### Screens to generate (linked prototype)

1. **Pulse Command Center** (`/`) — 3-column dashboard with emblem center
2. **Chat** (`/chat`) — streaming conversation + mode toolbar
3. **AI Studio** (`/studio`) — Build-focused chat variant
4. **Memory Fabric** (`/memory`) — search, add, export
5. **Settings** (`/settings`) — consent, network, model status

### Technical constraints

- Target: **React + Next.js App Router**, existing CSS variable tokens from DESIGN.md
- Do NOT invent a new backend; buttons call existing REST endpoints on `localhost:8000`
- Prefer refining layout/spacing/hierarchy over flashy 3D globes
- Include component names that map to our codebase: `GeboOsShell`, `OsWidget`, `ChatPanel`, `PulseCommandCenter`
- Output: high-fidelity screens + DESIGN.md updates + HTML/React snippets we can drop into `frontend/components/`

### Success criteria

A new user can open the app, understand system status on Pulse, chat with Gebo, manage memory, approve actions, and change settings — **without hitting a dead button or fake label**.

Make it functionable.
