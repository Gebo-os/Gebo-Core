# Create your Gebo custom Ollama model
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Modelfile = Join-Path $Root "models\Gebo.Modelfile"

Write-Host "Gebo Custom Model Setup" -ForegroundColor Green
Write-Host ""

if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "Ollama not found. Install from https://ollama.com/download" -ForegroundColor Red
    exit 1
}

Write-Host "1. Pulling base model llama3.2:3b (if needed)..." -ForegroundColor Cyan
ollama pull llama3.2:3b

Write-Host "2. Creating gebo-custom from Modelfile..." -ForegroundColor Cyan
ollama create gebo-custom -f $Modelfile

Write-Host "3. Quick test..." -ForegroundColor Cyan
ollama run gebo-custom "Who are you? One sentence." --verbose 2>$null | Select-Object -First 5

Write-Host ""
Write-Host "Done. Add to backend/.env:" -ForegroundColor Green
Write-Host "  OLLAMA_MODEL=gebo-custom"
Write-Host ""
Write-Host "Restart the backend, then verify at GET /status" -ForegroundColor Yellow
