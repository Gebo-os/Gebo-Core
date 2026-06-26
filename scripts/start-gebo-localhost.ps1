# Gebo Core Private — localhost with full network access
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

Write-Host "Gebo Core — starting on localhost with full internet access..." -ForegroundColor Green

$env:CORS_ORIGINS = "*"
$env:GEBO_BIND_HOST = "0.0.0.0"
$env:GEBO_BACKEND_URL = "http://127.0.0.1:8000"
$env:GEBO_FRONTEND_URL = "http://localhost:3000"

$backend = Start-Process -PassThru -WindowStyle Normal -WorkingDirectory "$Root\backend" -FilePath "$Root\backend\.venv\Scripts\uvicorn.exe" -ArgumentList @(
    "app.main:app",
    "--host", "0.0.0.0",
    "--port", "8000",
    "--reload"
)

Start-Sleep -Seconds 2

$frontend = Start-Process -PassThru -WindowStyle Normal -WorkingDirectory "$Root\frontend" -FilePath "npm" -ArgumentList @("run", "dev", "--", "-H", "0.0.0.0", "-p", "3000")

Write-Host ""
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Backend:  http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "  Health:   http://127.0.0.1:8000/health" -ForegroundColor Cyan
Write-Host "  Network:  CORS open (*), bind 0.0.0.0" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C in each window to stop." -ForegroundColor Gray
