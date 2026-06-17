# Post-deploy verification (after Railway/Vercel are live).

param(

    [Parameter(Mandatory = $true)]

    [string]$ApiUrl,

    [string]$FrontendUrl = "",

    [string]$CompanyId = "cmpfm1nst0001lhq3rz09938z",

    [string]$Token = "",

    [switch]$RunGoLive

)



$ErrorActionPreference = "Stop"

& "$PSScriptRoot\nafy-prod-handoff.ps1" @PSBoundParameters

