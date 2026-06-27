# Restart Gebo FastAPI backend on port 8000 (closes stale uvicorn/python on that port)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root "backend"
$Uvicorn = Join-Path $Backend ".venv\Scripts\uvicorn.exe"

Write-Host "Stopping processes on port 8000..." -ForegroundColor Yellow
for ($round = 0; $round -lt 5; $round++) {
    $listeners = @(Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue)
    if ($listeners.Count -eq 0) { break }
    foreach ($conn in $listeners) {
        $procId = $conn.OwningProcess
        $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "  Stopping PID $procId ($($proc.ProcessName))" -ForegroundColor Gray
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        }
    }
    Start-Sleep -Seconds 2
}

if (-not (Test-Path $Uvicorn)) {
    Write-Host "Missing $Uvicorn - run: cd backend; python -m venv .venv; pip install -r requirements.txt" -ForegroundColor Red
    exit 1
}

Write-Host "Starting Gebo backend on 0.0.0.0:8000..." -ForegroundColor Green
Start-Process -WindowStyle Normal -WorkingDirectory $Backend -FilePath $Uvicorn -ArgumentList @(
    "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"
)

for ($i = 0; $i -lt 30; $i++) {
    try {
        $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -TimeoutSec 2
        if ($health.ok) { break }
    } catch {
        Start-Sleep -Seconds 1
    }
}

try {
    $null = Invoke-RestMethod -Uri "http://127.0.0.1:8000/integrate/bootstrap" -TimeoutSec 5
    Write-Host "Backend online - bootstrap OK." -ForegroundColor Green
} catch {
    Write-Host "Warning: health OK but bootstrap failed - code may still be stale." -ForegroundColor Yellow
}

Write-Host "Backend: http://127.0.0.1:8000/health" -ForegroundColor Cyan
