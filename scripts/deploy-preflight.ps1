# Pre-production deploy gate — env vars + optional DB tenant check.

# Usage: .\scripts\deploy-preflight.ps1

#        .\scripts\deploy-preflight.ps1 -Strict

#        .\scripts\deploy-preflight.ps1 -SkipEnvCheck   # DB tenant only (dev .env OK)

param(

    [switch]$Strict,

    [switch]$SkipDb,

    [switch]$SkipEnvCheck,

    [string]$EnvFile = ""

)



$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot

Set-Location $Root



if (-not $SkipEnvCheck) {

    $envArgs = @()

    if ($Strict) { $envArgs += "--strict" }

    if ($EnvFile) { $envArgs += "--env-file"; $envArgs += $EnvFile }

    python scripts/_prod_env_check.py @envArgs

    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

}



if (-not $SkipDb) {

    python scripts/fastaccounts_migrate/_preflight_deploy.py

    exit $LASTEXITCODE

}



exit 0

