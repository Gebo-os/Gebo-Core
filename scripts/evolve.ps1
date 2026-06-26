# Gebo evolution loop — learn, grow, repeat (one command)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "backend"
$venv = Join-Path $backend ".venv\Scripts\python.exe"

Write-Host "Gebo evolve — ingest repos, verify tests, report memory" -ForegroundColor Cyan

Push-Location $backend
try {
    & $venv scripts\ingest_repo_memory.py
    Write-Host ""
    & $venv -m pytest -q
    Write-Host ""
    & $venv -c "from app import db; db.init_db(); print(f'Memories: {db.count_memories()}')"
} finally {
    Pop-Location
}

Write-Host "Done. Chat with Gebo to use what it learned." -ForegroundColor Green
