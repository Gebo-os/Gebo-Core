# ============================================================
# GEBO OFFICIAL RELEASE — 10 FREE CLI INSTALL CBP
# Windows PowerShell / Terminal — Run as Administrator
# ============================================================

$ErrorActionPreference = "Stop"

Write-Host "`n[0] Installing Node.js LTS first because npm CLIs need it..." -ForegroundColor Green
winget install -e --id OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements

# Refresh PATH for this terminal session
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

Write-Host "`n[1] Git — source control" -ForegroundColor Green
winget install -e --id Git.Git --accept-package-agreements --accept-source-agreements

Write-Host "`n[2] GitHub CLI — repo, issues, PRs, auth" -ForegroundColor Green
winget install -e --id GitHub.cli --accept-package-agreements --accept-source-agreements

Write-Host "`n[3] Vercel CLI — frontend/backend deploy" -ForegroundColor Green
npm install -g vercel

Write-Host "`n[4] Supabase CLI — database, auth, storage, local backend" -ForegroundColor Green
npm install -g supabase

Write-Host "`n[5] Prisma CLI — database schema, migrations, ORM" -ForegroundColor Green
npm install -g prisma

Write-Host "`n[6] Cloudflare Wrangler — security edge, workers, proxy layer" -ForegroundColor Green
npm install -g wrangler

Write-Host "`n[7] Snyk CLI — security vulnerability scanning" -ForegroundColor Green
npm install -g snyk

Write-Host "`n[8] Clerk CLI — auth setup and management" -ForegroundColor Green
npm install -g clerk

Write-Host "`n[9] Stripe CLI — payments, billing, webhook testing" -ForegroundColor Green
npm install -g @stripe/cli

Write-Host "`n[10] Ollama CLI — local AI model runner" -ForegroundColor Green
winget install -e --id Ollama.Ollama --accept-package-agreements --accept-source-agreements

Write-Host "`n========== VERSION CHECK ==========" -ForegroundColor Cyan

function Show-Version($label, $cmd) {
    try {
        $out = & $cmd 2>&1 | Select-Object -First 1
        Write-Host "$label`: $out"
    } catch {
        Write-Host "$label`: not found" -ForegroundColor Yellow
    }
}

Show-Version "git" { git --version }
Show-Version "gh" { gh --version }
Show-Version "node" { node --version }
Show-Version "npm" { npm --version }
Show-Version "vercel" { vercel --version }
Show-Version "supabase" { supabase --version }
Show-Version "prisma" { prisma --version }
Show-Version "wrangler" { wrangler --version }
Show-Version "snyk" { snyk --version }
Show-Version "clerk" { clerk --version }
Show-Version "stripe" { stripe --version }
Show-Version "ollama" { ollama --version }

Write-Host "`n========== LOGIN COMMANDS WHEN READY ==========" -ForegroundColor Cyan
Write-Host "gh auth login"
Write-Host "vercel login"
Write-Host "supabase login"
Write-Host "wrangler login"
Write-Host "snyk auth"
Write-Host "clerk login"
Write-Host "stripe login"

Write-Host "`nDONE. Gebo CLI layer installed." -ForegroundColor Green
