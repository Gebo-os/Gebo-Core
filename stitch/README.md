# Send current UI to Google Stitch

## Quick start (2 minutes)

1. Double-click **Gebo Stitch** on your Desktop (opens Google Stitch in **Chrome**).
   Or run: `.\scripts\open-stitch-handoff.ps1` from `gebo-core-private`.
2. Sign in at **https://stitch.withgoogle.com/** if prompted.
3. Create a project: **Gebo Owner NODE**.
4. On the canvas, **upload** `current-ui-snapshot.html` (already open in Chrome).
5. Paste the prompt from your clipboard (copied automatically by the script).
6. Attach **frontend/DESIGN.md** as additional context (paste or upload).
7. Ask Stitch to generate all 5 screens as a linked prototype.

1. In Stitch → Settings → **API key** → copy key.
2. Edit `.cursor/mcp.json` at repo root — replace `REPLACE_WITH_KEY_FROM_stitch.withgoogle.com`.
3. Restart Cursor → Settings → Tools & MCP → enable **stitch**.
4. In chat: *"Using Stitch MCP, redesign Gebo Owner NODE per DESIGN.md and make every control functional."*

## After Stitch generates designs

1. Export HTML/React from Stitch.
2. Map components to `gebo-core-private/frontend/components/`.
3. Keep existing `GeboProvider` + `lib/api.ts` wiring — swap layout/CSS only.

## Files in this folder

| File | Purpose |
|------|---------|
| `STITCH_PROMPT.md` | Prompt to paste into Stitch |
| `current-ui-snapshot.html` | Visual snapshot of current shell |
| `../frontend/DESIGN.md` | Design system source of truth |
