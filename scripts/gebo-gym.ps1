# Gebo Gym — official training algorithm for Gebo Core (Owner NODE)
#
# Learn → Grow → Act → Verify → Repeat
#
# This script runs the automated phases. Grow and Act happen in the Living Console.
#
#   Learn   — ingest GitHub/local repos into project memory (read-only)
#   Grow    — chat with Gebo; recall + wiki deepen context (manual)
#   Act     — approve proposed actions; Codex/build log when ready (manual)
#   Verify  — pytest confirms the stack is healthy
#   Repeat  — run Gebo Gym again after pushes, weekly, or when memory feels stale
#
# Usage:  .\scripts\gebo-gym.ps1
# Alias:  .\scripts\evolve.ps1  (same script)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "backend"
$venv = Join-Path $backend ".venv\Scripts\python.exe"

Write-Host ""
Write-Host "  Gebo Gym" -ForegroundColor Cyan
Write-Host "  Learn -> Grow -> Act -> Verify -> Repeat" -ForegroundColor DarkGray
Write-Host ""

Write-Host "[Learn] Ingesting repos into memory..." -ForegroundColor Yellow
Push-Location $backend
try {
    & $venv scripts\ingest_repo_memory.py
    Write-Host ""
    Write-Host "[Verify] Running backend tests..." -ForegroundColor Yellow
    & $venv -m pytest -q
    Write-Host ""
    $count = & $venv -c "from app import db; db.init_db(); print(db.count_memories())"
    Write-Host "[Report] Memories: $count" -ForegroundColor Yellow
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "[Grow] Open Chat — ask what Gebo learned." -ForegroundColor Magenta
Write-Host "[Act]  Open Actions — approve the next move." -ForegroundColor Magenta
Write-Host "[Repeat] Run .\scripts\gebo-gym.ps1 again when ready." -ForegroundColor Green
Write-Host ""
