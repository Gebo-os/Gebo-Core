# Gebo Core Private — localhost with full network access
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

Write-Host "Gebo Core - starting on localhost (desktop only)..." -ForegroundColor Green

# Clear stale backend on port 8000 (old python without bootstrap routes)
& (Join-Path $PSScriptRoot "restart-gebo-backend.ps1")
if ($LASTEXITCODE -ne 0) { exit 1 }

$env:CORS_ORIGINS = "http://localhost:3000,http://127.0.0.1:3000"
$env:GEBO_BIND_HOST = "127.0.0.1"
$env:GEBO_BACKEND_URL = "http://127.0.0.1:8000"
$env:GEBO_FRONTEND_URL = "http://localhost:3000"

$frontend = Start-Process -PassThru -WindowStyle Normal -WorkingDirectory "$Root\frontend" -FilePath "npm" -ArgumentList @("run", "dev", "--", "-H", "127.0.0.1", "-p", "3000")

Write-Host ""
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Backend:  http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "  Health:   http://127.0.0.1:8000/health" -ForegroundColor Cyan
Write-Host "  Desktop:  .\scripts\start-gebo.ps1 -Mode desktop" -ForegroundColor Cyan
Write-Host "  Network:  localhost only (no LAN)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C in each window to stop." -ForegroundColor Gray
