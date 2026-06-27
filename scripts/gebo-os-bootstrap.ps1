# Gebo OS full bootstrap — model, CLIs, knowledge, start
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Gebo OS Official Bootstrap" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 0.1 — Ollama model
Write-Host "[1/5] Checking Ollama..." -ForegroundColor White
if (Get-Command ollama -ErrorAction SilentlyContinue) {
    $models = ollama list 2>$null
    if ($models -match "gebo-custom") {
        Write-Host "  gebo-custom model found" -ForegroundColor Green
    } else {
        Write-Host "  Creating gebo-custom model..." -ForegroundColor Yellow
        & "$Root\scripts\create-gebo-model.ps1"
    }
} else {
    Write-Host "  Install Ollama: https://ollama.com/download" -ForegroundColor Yellow
}

# Step 0.2 — CLI scan
Write-Host "[2/5] Scanning CLIs..." -ForegroundColor White
& "$Root\scripts\gebo-activate-clis.ps1"

# Step 0.3 — Start Gebo
Write-Host "[3/5] Starting Gebo (WiFi mode)..." -ForegroundColor White
& "$Root\scripts\start-gebo-wifi.ps1"

Start-Sleep -Seconds 5

# Step 0.4 — Knowledge collect
Write-Host "[4/5] Running learning cycle..." -ForegroundColor White
try {
    $cycle = Invoke-RestMethod -Uri "http://127.0.0.1:8000/learning/cycle" -Method POST -TimeoutSec 120
    Write-Host "  Knowledge memories: $($cycle.knowledge.knowledge_memory_count)" -ForegroundColor Green
} catch {
    Write-Host "  Learning cycle skipped (backend warming up)" -ForegroundColor Yellow
}

# Step 0.5 — Verify
Write-Host "[5/5] Verification..." -ForegroundColor White
try {
    $boot = Invoke-RestMethod -Uri "http://127.0.0.1:8000/integrate/bootstrap" -TimeoutSec 10
    Write-Host "  Model: $($boot.status.model)" -ForegroundColor Cyan
    Write-Host "  Integrations: $($boot.capabilities.integrations)" -ForegroundColor Cyan
    Write-Host "  CLIs available: $($boot.capabilities.clis_available)" -ForegroundColor Cyan
} catch {
    Write-Host "  Bootstrap check failed — retry in a few seconds" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Official docs: docs/official/README.md" -ForegroundColor White
Write-Host "Micromini workflow: docs/official/MICRO-WORKFLOW.md" -ForegroundColor White
Write-Host ""
