# Full release gate — run before tagging or production deploy.
# Usage:
#   .\scripts\release-check.ps1                    # CI + prod env + DB + go-live
#   .\scripts\release-check.ps1 -SkipEnvStrict     # CI + DB + go-live (dev .env OK)
#   .\scripts\release-check.ps1 -SkipGoLive        # CI + preflight only
#   .\scripts\release-check.ps1 -EnvFile Backend\.env.production.local
param(
    [switch]$SkipGoLive,
    [switch]$SkipDb,
    [switch]$SkipEnvStrict,
    [string]$EnvFile = ""
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "=== Release check (Nafy-Pharma) ===" -ForegroundColor Cyan

Write-Host "`n[1/3] Local CI..." -ForegroundColor Yellow
& "$PSScriptRoot\ci-local.ps1"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`n[2/3] Deploy preflight..." -ForegroundColor Yellow
if ($SkipDb -and $SkipEnvStrict) {
    Write-Host "  (preflight skipped)" -ForegroundColor DarkGray
} elseif ($SkipDb) {
    if ($EnvFile) {
        python scripts/_prod_env_check.py --strict --env-file $EnvFile
    } else {
        python scripts/_prod_env_check.py --strict
    }
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} elseif ($SkipEnvStrict) {
    & "$PSScriptRoot\deploy-preflight.ps1" -SkipEnvCheck
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} elseif ($EnvFile) {
    & "$PSScriptRoot\deploy-preflight.ps1" -Strict -EnvFile $EnvFile
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} else {
    & "$PSScriptRoot\deploy-preflight.ps1" -Strict
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

if ($SkipGoLive) {
    Write-Host "`n=== Release readiness ===" -ForegroundColor Yellow
    python scripts/_release_readiness.py
    Write-Host "`n=== Release check: PASS (go-live skipped) ===" -ForegroundColor Green
    exit 0
}

Write-Host "`n[3/3] Go-live verification (may take several minutes)..." -ForegroundColor Yellow
& "$PSScriptRoot\go-live.ps1"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`n=== Release readiness ===" -ForegroundColor Yellow
python scripts/_release_readiness.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "=== Release check: PASS (pre-deploy) ===" -ForegroundColor Green
Write-Host "  Dashboard: Backend/docs/NAFY-RELEASE-READINESS-LATEST.md" -ForegroundColor Cyan
Write-Host "  Next: deploy prod, then nafy-prod-handoff.ps1 + human UAT" -ForegroundColor Cyan
exit 0
