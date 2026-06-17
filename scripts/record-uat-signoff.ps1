# Record Nafy-Pharma human UAT sign-off after completing NAFY-UAT-CHECKLIST.md.

# Usage:

#   .\scripts\record-uat-signoff.ps1 -BusinessOwner "..." -Finance "..." -TechnicalLead "..."

#   .\scripts\record-uat-signoff.ps1 ... -Result PASS_WITH_WAIVERS -Waivers "B6 skipped — Brevo not live"

param(

    [Parameter(Mandatory = $true)]

    [string]$BusinessOwner,

    [Parameter(Mandatory = $true)]

    [string]$Finance,

    [Parameter(Mandatory = $true)]

    [string]$TechnicalLead,

    [ValidateSet("PASS", "PASS_WITH_WAIVERS", "FAIL")]

    [string]$Result = "PASS",

    [string]$Waivers = "",

    [string]$Notes = ""

)



$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot

Set-Location $Root



$argsList = @(

    "scripts/_uat_signoff.py",

    "--record",

    "--business-owner", $BusinessOwner,

    "--finance", $Finance,

    "--technical-lead", $TechnicalLead,

    "--result", $Result

)

if ($Waivers) { $argsList += @("--waivers", $Waivers) }

if ($Notes) { $argsList += @("--notes", $Notes) }



python @argsList

exit $LASTEXITCODE

