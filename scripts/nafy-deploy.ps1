# Nafy-Pharma production deploy orchestrator.
# Usage:
#   .\scripts\nafy-deploy.ps1                              # pre-deploy gates only
#   .\scripts\nafy-deploy.ps1 -EnvFile Backend\.env.production.local
#   .\scripts\nafy-deploy.ps1 -ApiUrl https://... -FrontendUrl https://...
param(
    [string]$EnvFile = "",
    [string]$ApiUrl = "",
    [string]$FrontendUrl = "",
    [switch]$SkipCi,
    [switch]$RunGoLive
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "=== Nafy deploy ===" -ForegroundColor Cyan

if (-not $SkipCi) {
    Write-Host "`n[1] Pre-deploy gates (CI + parity + data)..." -ForegroundColor Yellow
    if ($EnvFile) {
        & "$PSScriptRoot\release-check.ps1" -EnvFile $EnvFile
    } else {
        & "$PSScriptRoot\release-check.ps1" -SkipEnvStrict
    }
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} else {
    Write-Host "`n[1] Pre-deploy gates skipped (-SkipCi)" -ForegroundColor DarkGray
    python scripts/_release_readiness.py --strict-predeploy
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

python scripts/_release_readiness.py | Out-Null

if (-not $ApiUrl) {
    Write-Host ""
    Write-Host "=== Pre-deploy READY ===" -ForegroundColor Green
    Write-Host "  Dashboard: Backend/docs/NAFY-RELEASE-READINESS-LATEST.md"
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Deploy Railway (Backend/) + Vercel (Frontend/) — see Backend/docs/DEPLOY-QUICKSTART.md"
    Write-Host "  2. Re-run with prod URLs:"
    Write-Host "     .\scripts\nafy-deploy.ps1 -ApiUrl https://<api> -FrontendUrl https://<app> [-RunGoLive]"
    exit 0
}

Write-Host "`n[2] Production handoff smoke..." -ForegroundColor Yellow
$handoffArgs = @("-ApiUrl", $ApiUrl)
if ($FrontendUrl) { $handoffArgs += @("-FrontendUrl", $FrontendUrl) }
if ($RunGoLive) { $handoffArgs += "-RunGoLive" }
& "$PSScriptRoot\nafy-prod-handoff.ps1" @handoffArgs
exit $LASTEXITCODE
