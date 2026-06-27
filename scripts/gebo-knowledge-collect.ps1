# Run Gebo knowledge collection (catalog + private docs + integrations)
$ErrorActionPreference = "Stop"

Write-Host "Gebo OS — knowledge collection" -ForegroundColor Green

try {
    $result = Invoke-RestMethod -Uri "http://127.0.0.1:8000/learning/cycle" -Method POST -TimeoutSec 120
    Write-Host ($result | ConvertTo-Json -Depth 5)
    Write-Host "Done." -ForegroundColor Green
} catch {
    Write-Host "Backend offline. Start Gebo first: .\scripts\start-gebo.ps1" -ForegroundColor Red
    exit 1
}
