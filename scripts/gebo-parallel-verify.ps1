# Gebo parallel verify — pytest + codex status + agent runtime (concurrent)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

Write-Host "Gebo Parallel Verify" -ForegroundColor Green

$pytestJob = Start-Job -ScriptBlock {
    Set-Location $using:Root
    Set-Location backend
    & .\.venv\Scripts\python.exe -m pytest -q 2>&1
}

$codexJob = Start-Job -ScriptBlock {
    $cmd = Get-Command codex -ErrorAction SilentlyContinue
    if (-not $cmd) { return "Codex: not installed" }
    $v = & $cmd.Source --version 2>&1 | Select-Object -First 1
    return "Codex: $v"
}

$healthJob = Start-Job -ScriptBlock {
    try {
        $h = Invoke-RestMethod "http://127.0.0.1:8000/health" -TimeoutSec 5
        $a = Invoke-RestMethod "http://127.0.0.1:8000/agents/runtime/status" -TimeoutSec 5
        return "Backend: ok · agents=$($a.active_agents) · codex_lane=$($a.codex_lane.status)"
    } catch {
        return "Backend: offline (start uvicorn first)"
    }
}

Wait-Job $pytestJob, $codexJob, $healthJob | Out-Null

Write-Host ""
Receive-Job $pytestJob
Receive-Job $codexJob
Receive-Job $healthJob
Write-Host ""

Remove-Job $pytestJob, $codexJob, $healthJob -Force
