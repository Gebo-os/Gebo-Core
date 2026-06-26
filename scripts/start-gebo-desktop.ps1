# Gebo Owner NODE — one-click desktop launcher (Windows)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$DesktopDir = Join-Path $Root "desktop"

Write-Host "Gebo Owner NODE — starting desktop app..." -ForegroundColor Green

# Ensure frontend deps
$FrontendDir = Join-Path $Root "frontend"
if (-not (Test-Path (Join-Path $FrontendDir "node_modules"))) {
  Write-Host "Installing frontend dependencies..."
  Push-Location $FrontendDir
  npm install
  Pop-Location
}

# Ensure backend venv
$Python = Join-Path $Root "backend\.venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
  Write-Host "Creating backend venv..."
  Push-Location (Join-Path $Root "backend")
  python -m venv .venv
  .\.venv\Scripts\pip install -r requirements.txt
  Pop-Location
}

# Ensure desktop deps
if (-not (Test-Path (Join-Path $DesktopDir "node_modules"))) {
  Write-Host "Installing desktop (Electron) dependencies..."
  Push-Location $DesktopDir
  npm install
  Pop-Location
}

Push-Location $DesktopDir
npm start
Pop-Location
