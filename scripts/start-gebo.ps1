# Gebo Core — unified launcher
param(
    [ValidateSet("wifi", "localhost", "desktop")]
    [string]$Mode = "wifi"
)

$Root = Split-Path -Parent $PSScriptRoot
$Script = switch ($Mode) {
    "wifi" { Join-Path $PSScriptRoot "start-gebo-wifi.ps1" }
    "localhost" { Join-Path $PSScriptRoot "start-gebo-localhost.ps1" }
    "desktop" { Join-Path $PSScriptRoot "start-gebo-desktop.ps1" }
}

Write-Host "Gebo Core - mode: $Mode" -ForegroundColor Green
& $Script
