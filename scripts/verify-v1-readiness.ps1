# Gebo V1 readiness — calls /system/v1-readiness and prints score + gaps
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$BaseUrl = if ($env:GEBO_BACKEND_URL) { $env:GEBO_BACKEND_URL.TrimEnd("/") } else { "http://127.0.0.1:8000" }

Write-Host "Gebo V1 Readiness Check" -ForegroundColor Green
Write-Host "Backend: $BaseUrl" -ForegroundColor DarkGray

try {
    $data = Invoke-RestMethod "$BaseUrl/system/v1-readiness" -TimeoutSec 15
} catch {
    Write-Host "Failed to reach $BaseUrl/system/v1-readiness" -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 1
}

$score = $data.readiness_score
$ready = $data.required_ready
$total = $data.required_total
$modulesReady = $data.modules_ready
$modulesTotal = $data.modules_total
$mode = $data.release_mode

Write-Host ""
Write-Host "Release mode:  $mode"
Write-Host "Score:         $score / 100 ($ready / $total required controls)"
Write-Host "Modules:       $modulesReady / $modulesTotal active"
Write-Host "V1 ready:      $($data.v1_ready)"
Write-Host ""

$missing = @($data.controls | Where-Object { $_.release_tier -eq "required" -and -not $_.ready })
if ($missing.Count -eq 0) {
    Write-Host "All required V1 controls are live." -ForegroundColor Green
} else {
    Write-Host "Missing / not live ($($missing.Count)):" -ForegroundColor Yellow
    foreach ($ctrl in $missing) {
        $envList = ($ctrl.env -join ", ")
        Write-Host "  - $($ctrl.name) [$($ctrl.id)]" -ForegroundColor Yellow
        Write-Host "    env: $envList"
        Write-Host "    docs: $($ctrl.docs)"
    }
}

if ($data.next_steps) {
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    foreach ($step in $data.next_steps) {
        Write-Host "  • $step"
    }
}

Write-Host ""
if ($score -ge 100 -and $mode -eq "production") {
    Write-Host "10/10 production readiness achieved." -ForegroundColor Green
    exit 0
}
if ($mode -eq "owner") {
    Write-Host "Owner mode: score 0 is expected until GEBO_RELEASE_MODE=production." -ForegroundColor DarkGray
}
exit 0
