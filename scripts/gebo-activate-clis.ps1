# Scan local CLIs and print install hints for missing tools
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot

Write-Host "Gebo OS — CLI activation scan" -ForegroundColor Green

try {
    $status = Invoke-RestMethod -Uri "http://127.0.0.1:8000/cli/status" -TimeoutSec 5
    foreach ($item in $status.items) {
        if ($item.available) {
            Write-Host "  [OK] $($item.name) — $($item.version)" -ForegroundColor Green
        } else {
            Write-Host "  [--] $($item.name) — install: $($item.install_hint)" -ForegroundColor Yellow
        }
    }
    Write-Host ""
    Write-Host "Available: $($status.available) / $($status.total)" -ForegroundColor Cyan
    exit 0
} catch {
    Write-Host "Backend offline — running local scan only" -ForegroundColor Yellow
}

$checks = @(
    @{ Name = "Ollama"; Bin = "ollama"; Install = "https://ollama.com/download" },
    @{ Name = "Codex"; Bin = "codex"; Install = "npm install -g @openai/codex" },
    @{ Name = "GitHub CLI"; Bin = "gh"; Install = "https://cli.github.com/" },
    @{ Name = "Firebase CLI"; Bin = "firebase"; Install = "npm install -g firebase-tools" },
    @{ Name = "Google Cloud CLI"; Bin = "gcloud"; Install = "https://cloud.google.com/sdk" },
    @{ Name = "xAI CLI"; Bin = "xai"; Install = "irm https://x.ai/cli/install.ps1 | iex" }
)

foreach ($c in $checks) {
    $found = Get-Command $c.Bin -ErrorAction SilentlyContinue
    if ($found) {
        Write-Host "  [OK] $($c.Name)" -ForegroundColor Green
    } else {
        Write-Host "  [--] $($c.Name) — $($c.Install)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Optional: install xAI CLI now? (requires network)" -ForegroundColor Gray
Write-Host "  irm https://x.ai/cli/install.ps1 | iex" -ForegroundColor Gray
