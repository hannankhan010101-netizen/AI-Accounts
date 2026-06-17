# Local CI gate — mirrors GitHub Actions checks (no Docker/E2E).
# Usage: .\scripts\ci-local.ps1
param(
    [switch]$SkipFrontend
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "=== Backend pytest ===" -ForegroundColor Cyan
Set-Location Backend
$env:PYTHONPATH = "src"
$env:SKIP_PRISMA = "1"
$env:OUTBOX_POLL_ENABLED = "0"
python -m pytest src/tests -q
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`n=== Feature matrix ===" -ForegroundColor Cyan
Set-Location $Root
python scripts/_generate_feature_matrix.py
python scripts/_parity_progress.py --strict-nafy
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $SkipFrontend) {
    Write-Host "`n=== Frontend typecheck ===" -ForegroundColor Cyan
    Set-Location Frontend
    npm run typecheck
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Write-Host "`n=== Frontend lint ===" -ForegroundColor Cyan
    npm run lint
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Write-Host "`n=== Frontend build ===" -ForegroundColor Cyan
    $env:NEXT_PUBLIC_API_BASE_URL = "https://api.example.com"
    npm run build
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Set-Location $Root
Write-Host "`n=== CI local: PASS ===" -ForegroundColor Green
exit 0
