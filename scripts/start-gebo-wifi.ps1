# Gebo Core Private - WiFi/LAN access for phones and tablets on the same network
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

function Get-LanIp {
    $addr = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object {
            $_.IPAddress -notmatch '^(127\.|169\.254\.)' -and
            $_.PrefixOrigin -ne 'WellKnown'
        } |
        Sort-Object -Property InterfaceMetric |
        Select-Object -First 1 -ExpandProperty IPAddress

    if ($addr) { return $addr }

    try {
        $udp = New-Object System.Net.Sockets.UdpClient
        $udp.Connect("8.8.8.8", 80)
        $endpoint = $udp.Client.LocalEndPoint
        $udp.Close()
        return $endpoint.Address.ToString()
    }
    catch {
        return $null
    }
}

$LanIp = Get-LanIp
if (-not $LanIp) {
    Write-Host "Could not detect LAN IP - falling back to localhost." -ForegroundColor Yellow
    $LanIp = "127.0.0.1"
}

Write-Host "Gebo Core - starting for WiFi/LAN access..." -ForegroundColor Green
Write-Host "Detected LAN IP: $LanIp" -ForegroundColor Cyan

$env:CORS_ORIGINS = "*"
$env:GEBO_BIND_HOST = "0.0.0.0"
Remove-Item Env:GEBO_BACKEND_URL -ErrorAction SilentlyContinue
Remove-Item Env:GEBO_FRONTEND_URL -ErrorAction SilentlyContinue

$backend = Start-Process -PassThru -WindowStyle Normal -WorkingDirectory "$Root\backend" -FilePath "$Root\backend\.venv\Scripts\uvicorn.exe" -ArgumentList @(
    "app.main:app",
    "--host", "0.0.0.0",
    "--port", "8000",
    "--reload"
)

Write-Host "Waiting for backend health..." -ForegroundColor Gray
$healthOk = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -TimeoutSec 2
        if ($health.ok) {
            $healthOk = $true
            break
        }
    }
    catch {
        Start-Sleep -Seconds 1
    }
}

if (-not $healthOk) {
    Write-Host "Backend did not become healthy on port 8000." -ForegroundColor Red
    exit 1
}

try {
    $null = Invoke-RestMethod -Uri "http://127.0.0.1:8000/system/v1-readiness" -TimeoutSec 3
}
catch {
    Write-Host "Warning: /system/v1-readiness returned 404 — an old backend may still be on port 8000." -ForegroundColor Yellow
    Write-Host "Close other uvicorn/backend windows, then run this script again." -ForegroundColor Yellow
}

try {
    $body = '{"internet_access": true}'
    $network = Invoke-RestMethod -Uri "http://127.0.0.1:8000/settings/network" -Method POST -ContentType "application/json" -Body $body
    Write-Host "Network settings updated (internet_access=true, cors_mode=$($network.cors_mode))." -ForegroundColor Green
}
catch {
    Write-Host "Warning: could not POST /settings/network" -ForegroundColor Yellow
}

$frontend = Start-Process -PassThru -WindowStyle Normal -WorkingDirectory "$Root\frontend" -FilePath "npm" -ArgumentList @("run", "dev", "--", "-H", "0.0.0.0", "-p", "3000")

Write-Host ""
Write-Host "  From this PC:" -ForegroundColor White
Write-Host "    Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "    Backend:  http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "  From phone/tablet on same WiFi (LAN IP $LanIp):" -ForegroundColor White
Write-Host "    Frontend: http://${LanIp}:3000" -ForegroundColor Cyan
Write-Host "    Backend:  http://${LanIp}:8000" -ForegroundColor Cyan
Write-Host "    Health:   http://${LanIp}:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "  CORS open (*), bind 0.0.0.0 - close windows to stop." -ForegroundColor Yellow
