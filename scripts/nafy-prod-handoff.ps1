# Production handoff after Railway + Vercel deploy (Nafy-Pharma).
# Usage:
#   .\scripts\nafy-prod-handoff.ps1 -ApiUrl https://your-api.railway.app -FrontendUrl https://app.yourdomain.com
#   .\scripts\nafy-prod-handoff.ps1 -ApiUrl https://... -RunGoLive   # also runs DB go-live gates
param(
    [Parameter(Mandatory = $true)]
    [string]$ApiUrl,
    [string]$FrontendUrl = "",
    [string]$CompanyId = "cmpfm1nst0001lhq3rz09938z",
    [string]$Token = "",
    [switch]$RunGoLive
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "=== Nafy production handoff ===" -ForegroundColor Cyan

Write-Host "`n[1/2] HTTP smoke (API + optional frontend)..." -ForegroundColor Yellow
$smokeArgs = @("--api-url", $ApiUrl, "--company-id", $CompanyId)
if ($FrontendUrl) { $smokeArgs += @("--frontend-url", $FrontendUrl) }
if ($Token) { $smokeArgs += @("--token", $Token) }
python scripts/_post_deploy_smoke.py @smokeArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$handoffPath = Join-Path $Root "Backend\config\nafy_prod_handoff.json"
@{
    apiUrl      = $ApiUrl.TrimEnd("/")
    frontendUrl = $FrontendUrl.TrimEnd("/")
    recordedAt  = (Get-Date -Format "yyyy-MM-dd")
    result      = "PASS"
    companyId   = $CompanyId
} | ConvertTo-Json -Depth 3 | Set-Content -Path $handoffPath -Encoding utf8
python scripts/_release_readiness.py | Out-Null

if ($RunGoLive) {
    Write-Host "`n[2/2] Go-live data + parity gates (requires Backend/.env -> prod DB)..." -ForegroundColor Yellow
    & "$PSScriptRoot\go-live.ps1"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} else {
    Write-Host "`n[2/2] Go-live skipped (use -RunGoLive when Backend/.env points at prod DB)" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "=== Handoff status ===" -ForegroundColor Green
Write-Host "  In-scope parity:  Backend/docs/NAFY-IN-SCOPE-SIGNOFF-LATEST.md"
Write-Host "  Data go-live:     Backend/docs/GO-LIVE-SIGNOFF-LATEST.md"
Write-Host "  Readiness:        Backend/docs/NAFY-RELEASE-READINESS-LATEST.md"
Write-Host "  Human UAT:        Backend/docs/NAFY-UAT-CHECKLIST.md"
Write-Host "  UAT sign-off:     Backend/docs/NAFY-UAT-SIGNOFF-LATEST.md  (record via record-uat-signoff.ps1)"
Write-Host "  Day-1 ops:        Backend/docs/DAY-1-OPERATIONS.md"
Write-Host ""

if (-not $RunGoLive) {
    Write-Host "Next: set Backend/.env to prod DATABASE_URL/DIRECT_URL, then:" -ForegroundColor Cyan
    Write-Host "  .\scripts\nafy-prod-handoff.ps1 -ApiUrl $ApiUrl -FrontendUrl '$FrontendUrl' -RunGoLive" -ForegroundColor Cyan
}

exit 0
