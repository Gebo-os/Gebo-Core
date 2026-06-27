# Build downloadable Gebo Owner NODE package for Windows
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$DesktopDir = Join-Path $Root "desktop"
$Frontend = Join-Path $Root "frontend"
$Backend = Join-Path $Root "backend"
$UserDesktop = [Environment]::GetFolderPath("Desktop")
$OutFolder = Join-Path $UserDesktop "Gebo-Owner-NODE"
$ZipPath = Join-Path $UserDesktop "Gebo-Owner-NODE-Windows.zip"

Write-Host "Gebo Owner NODE - building downloadable package..." -ForegroundColor Green

$Python = Join-Path $Backend ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    Write-Host "Creating backend venv..." -ForegroundColor Yellow
    Push-Location $Backend
    python -m venv .venv
    .\.venv\Scripts\pip install -r requirements.txt
    Pop-Location
}

Push-Location $Frontend
if (-not (Test-Path "node_modules")) { npm install }
Write-Host "Building frontend..." -ForegroundColor Cyan
npm run build
Pop-Location

Push-Location $DesktopDir
if (-not (Test-Path "node_modules")) { npm install }
node scripts/ensure-electron.js
if ($LASTEXITCODE -ne 0) { Pop-Location; exit 1 }

Write-Host "Packaging app (unsigned dir build)..." -ForegroundColor Cyan
$env:CSC_IDENTITY_AUTO_DISCOVERY = "false"
npm run dist
if ($LASTEXITCODE -ne 0) { Pop-Location; exit 1 }
Pop-Location

$UnpackedDir = Join-Path $DesktopDir "dist\win-unpacked"
$PortableExe = Get-ChildItem -Path $UnpackedDir -Filter "Gebo Owner NODE.exe" -ErrorAction SilentlyContinue |
    Select-Object -First 1

if (-not $PortableExe) {
    Write-Host "Build failed - no exe found in desktop\dist\win-unpacked" -ForegroundColor Red
    exit 1
}

if (Test-Path $OutFolder) { Remove-Item -Recurse -Force $OutFolder }
Copy-Item -Path $UnpackedDir -Destination $OutFolder -Recurse -Force

$RootJson = @{ root = $Root } | ConvertTo-Json -Compress
Set-Content -Path (Join-Path $OutFolder "gebo-root.json") -Value $RootJson -Encoding UTF8 -NoNewline

$ReadmeLines = @(
    "Gebo Owner NODE - Windows Launcher",
    "================================",
    "",
    "1. Double-click Gebo Owner NODE.exe",
    "2. Requires Ollama: ollama serve and ollama pull llama3.2:3b",
    "3. gebo-root.json points to: $Root",
    "",
    "Edit gebo-root.json or set GEBO_ROOT to move the launcher.",
    "",
    "Repo: https://github.com/Gebo-os/Gebo-Core"
)
Set-Content -Path (Join-Path $OutFolder "README.txt") -Value $ReadmeLines -Encoding UTF8

if (Test-Path $ZipPath) { Remove-Item -Force $ZipPath }
Compress-Archive -Path "$OutFolder\*" -DestinationPath $ZipPath -Force

$ShortcutPath = Join-Path $UserDesktop "Gebo Owner NODE.lnk"
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = Join-Path $OutFolder "Gebo Owner NODE.exe"
$Shortcut.WorkingDirectory = $OutFolder
$Shortcut.Description = "Gebo Owner NODE - Private intelligence console"
$Shortcut.Save()

Write-Host ""
Write-Host "DOWNLOAD READY" -ForegroundColor Green
Write-Host "  Folder:   $OutFolder" -ForegroundColor Cyan
Write-Host "  Zip:      $ZipPath" -ForegroundColor Cyan
Write-Host "  Shortcut: $ShortcutPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "Double-click 'Gebo Owner NODE' on your Desktop to launch." -ForegroundColor White
