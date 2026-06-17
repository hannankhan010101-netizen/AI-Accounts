# Nafy-Pharma release verification (data + in-scope parity gates).
# Usage: .\scripts\go-live.ps1
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "=== Nafy release gates ===" -ForegroundColor Cyan

Write-Host "`n[1/2] In-scope parity (--strict-nafy)..." -ForegroundColor Yellow
python scripts/_generate_feature_matrix.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python scripts/_parity_progress.py --strict-nafy
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`n[2/2] Go-live data checks..." -ForegroundColor Yellow
python scripts/fastaccounts_migrate/_go_live_check.py
exit $LASTEXITCODE
