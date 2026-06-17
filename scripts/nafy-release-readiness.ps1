# Print Nafy release readiness dashboard (pre-deploy / deploy / UAT gates).
# Usage: .\scripts\nafy-release-readiness.ps1
#        .\scripts\nafy-release-readiness.ps1 -StrictPredeploy
param(
    [switch]$StrictPredeploy,
    [switch]$StrictBusiness
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$argsList = @("scripts/_release_readiness.py")
if ($StrictPredeploy) { $argsList += "--strict-predeploy" }
if ($StrictBusiness) { $argsList += "--strict-business" }

python @argsList
exit $LASTEXITCODE
