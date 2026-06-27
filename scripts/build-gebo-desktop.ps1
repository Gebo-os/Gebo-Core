# Build Gebo Owner NODE portable .exe and copy shortcut to Desktop
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Desktop = Join-Path $Root "desktop"
$Frontend = Join-Path $Root "frontend"
$Backend = Join-Path $Root "backend"

Write-Host "Gebo Owner NODE - building portable app..." -ForegroundColor Green

# Backend venv
$Python = Join-Path $Backend ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    Write-Host "Creating backend venv..." -ForegroundColor Yellow
    Push-Location $Backend
    python -m venv .venv
    .\.venv\Scripts\pip install -r requirements.txt
    Pop-Location
}

# Frontend production build (faster desktop startup)
if (-not (Test-Path (Join-Path $Frontend ".next"))) {
    Write-Host "Building frontend..." -ForegroundColor Yellow
    Push-Location $Frontend
    if (-not (Test-Path "node_modules")) { npm install }
    npm run build
    Pop-Location
}

# Desktop deps + portable exe
Push-Location $Desktop
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing Electron..." -ForegroundColor Yellow
    npm install
}
Write-Host "Packaging portable .exe (may take a few minutes)..." -ForegroundColor Cyan
npm run dist
Pop-Location

$Portable = Get-ChildItem -Path (Join-Path $Desktop "dist") -Filter "*.exe" -Recurse -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (-not $Portable) {
    Write-Host "Build failed - no .exe found in desktop\dist" -ForegroundColor Red
    exit 1
}

$UserDesktop = [Environment]::GetFolderPath("Desktop")
$Dest = Join-Path $UserDesktop "Gebo Owner NODE.exe"
Copy-Item -Path $Portable.FullName -Destination $Dest -Force

Write-Host ""
Write-Host "DONE" -ForegroundColor Green
Write-Host "  Portable app: $($Portable.FullName)" -ForegroundColor Cyan
Write-Host "  Copied to:    $Dest" -ForegroundColor Cyan
Write-Host ""
Write-Host "Double-click 'Gebo Owner NODE' on your Desktop to launch." -ForegroundColor White
Write-Host "Requires: Ollama running + backend venv (already in this repo)." -ForegroundColor DarkGray
