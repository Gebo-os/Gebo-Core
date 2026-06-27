#Requires -Version 5.1
<#
.SYNOPSIS
  Opens Google Stitch in Chrome and the Gebo UI handoff files for UX redesign.
#>
$Root = Split-Path -Parent $PSScriptRoot
$StitchDir = Join-Path $Root "stitch"
$DesignMd = Join-Path $Root "frontend\DESIGN.md"
$Snapshot = Join-Path $StitchDir "current-ui-snapshot.html"
$Prompt = Join-Path $StitchDir "STITCH_PROMPT.md"
$UserDesktop = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $UserDesktop "Gebo Stitch.lnk"

function Get-ChromePath {
  $candidates = @(
    "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
  )
  foreach ($path in $candidates) {
    if (Test-Path $path) { return $path }
  }
  return $null
}

function Open-InChrome {
  param(
    [Parameter(Mandatory = $true)][string]$ChromeExe,
    [Parameter(Mandatory = $true)][string]$Target
  )
  Start-Process -FilePath $ChromeExe -ArgumentList @($Target, "--new-tab")
}

function Ensure-StitchDesktopShortcut {
  param(
    [Parameter(Mandatory = $true)][string]$ScriptPath,
    [Parameter(Mandatory = $true)][string]$OutPath
  )
  $WshShell = New-Object -ComObject WScript.Shell
  $Shortcut = $WshShell.CreateShortcut($OutPath)
  $Shortcut.TargetPath = "powershell.exe"
  $Shortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`""
  $Shortcut.WorkingDirectory = $Root
  $Shortcut.Description = "Open Google Stitch in Chrome with Gebo UI handoff"
  $Shortcut.IconLocation = "$env:ProgramFiles\Google\Chrome\Application\chrome.exe,0"
  $Shortcut.Save()
}

Write-Host "Gebo → Google Stitch handoff (Chrome)" -ForegroundColor Green
Write-Host "  DESIGN.md   : $DesignMd"
Write-Host "  Snapshot    : $Snapshot"
Write-Host "  Prompt      : $Prompt"
Write-Host ""

$Chrome = Get-ChromePath
if (-not $Chrome) {
  Write-Host "Google Chrome not found. Install Chrome or open stitch.withgoogle.com manually." -ForegroundColor Red
  Start-Process "https://stitch.withgoogle.com/"
  exit 1
}

if (Test-Path $Prompt) {
  $text = Get-Content $Prompt -Raw
  if ($text -match '(?s)## Prompt for Stitch\s*\r?\n(.+)') {
    Set-Clipboard -Value $Matches[1].Trim()
    Write-Host "Stitch prompt copied to clipboard." -ForegroundColor Cyan
  }
}

Ensure-StitchDesktopShortcut -ScriptPath $PSCommandPath -OutPath $ShortcutPath
Write-Host "Desktop shortcut: $ShortcutPath" -ForegroundColor Cyan

Open-InChrome -ChromeExe $Chrome -Target "https://stitch.withgoogle.com/"
if (Test-Path $Snapshot) {
  $SnapshotUri = ([Uri]$Snapshot).AbsoluteUri
  Open-InChrome -ChromeExe $Chrome -Target $SnapshotUri
}

Start-Process notepad.exe $Prompt

Write-Host ""
Write-Host "Chrome opened Stitch + UI snapshot. Paste the prompt (clipboard) and attach DESIGN.md in Stitch."
