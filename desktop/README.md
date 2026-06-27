# Gebo Owner NODE — Desktop App

Electron shell for the Gebo Living Console. Starts backend + frontend locally and opens in a native window.

## Prerequisites (one-time)

1. **Ollama** running with `llama3.2:3b` pulled
2. **Backend venv** installed:

```powershell
cd ..\backend
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

3. **Frontend** built (recommended for faster desktop startup):

```powershell
cd ..\frontend
npm install
npm run build
```

4. **Desktop** dependencies:

```powershell
cd desktop
npm install
```

## Launch

```powershell
cd desktop
npm start
```

Or from project root:

```powershell
.\scripts\start-gebo-desktop.ps1
```

### ffmpeg.dll not found

If Electron fails with **ffmpeg.dll not found**, repair the binary:

```powershell
cd desktop
node scripts/ensure-electron.js
npm start
```

`ensure-electron.js` re-downloads and fully extracts `electron.exe` + `ffmpeg.dll` when npm leaves a partial install (locales-only folder).

## What it does

1. Checks if backend (`:8000`) and frontend (`:3000`) are already running
2. Starts them if not (backend via uvicorn, frontend via `next start` or `next dev`)
3. Opens **Gebo Owner NODE** in an Electron window
4. Stops spawned processes when you close the app

## Memory location

SQLite database: `backend/data/gebo.db`

## Portable build (optional)

```powershell
npm run dist
```

Output in `desktop/dist/`. Note: Python venv and Ollama must still be installed on the machine.
