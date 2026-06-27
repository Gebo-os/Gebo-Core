# Private Gebo system build — collect docs, cache locally, ingest memory
$ErrorActionPreference = "Stop"

Write-Host "Gebo OS — private system build" -ForegroundColor Green

try {
    $result = Invoke-RestMethod -Uri "http://127.0.0.1:8000/system/build" -Method POST -TimeoutSec 600
    Write-Host "Manifest v$($result.manifest.version) — $($result.manifest.knowledge_memories) knowledge memories" -ForegroundColor Cyan
    Write-Host "Doc cache: $($result.status.doc_cache_count) files" -ForegroundColor Cyan
    Write-Host ($result.collection | ConvertTo-Json -Depth 4 -Compress)
} catch {
    Write-Host "Backend offline. Start: .\scripts\start-gebo.ps1" -ForegroundColor Red
    exit 1
}
