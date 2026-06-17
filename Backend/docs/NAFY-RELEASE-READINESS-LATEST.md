# Nafy release readiness (latest)

**Generated:** 2026-05-30 10:23 UTC  
**Pre-deploy ready:** **YES**  
**Deploy smoke:** **Pending**  
**Business go-live:** **NOT READY** — still needed: prod deploy smoke, human UAT

## Gates

| Gate | Phase | Status | Detail |
|------|-------|--------|--------|
| In-scope FA parity | pre-deploy | **PASS** | 99/99 in-scope rows ✅ |
| Migration / data go-live | pre-deploy | **PASS** | GO + report spot-check PASS |
| Production deploy smoke | deploy | **Pending** | not run — use nafy-prod-handoff.ps1 after deploy |
| Human UAT | post-deploy | **Pending** | Pending — complete [NAFY-UAT-CHECKLIST.md](./NAFY-UAT-CHECKLIST.md) |

## Commands

```powershell
# Pre-deploy (local / prod DB in Backend/.env)
.\scripts\release-check.ps1 -SkipEnvStrict

# After Railway + Vercel deploy
.\scripts\nafy-prod-handoff.ps1 -ApiUrl https://<api> -FrontendUrl https://<app>

# After UAT checklist
.\scripts\record-uat-signoff.ps1 -BusinessOwner ... -Finance ... -TechnicalLead ... -Result PASS

# Full business gate
python scripts/_parity_progress.py --strict-nafy-release
```

Artifacts: [GO-LIVE-SIGNOFF-LATEST.md](./GO-LIVE-SIGNOFF-LATEST.md) · [NAFY-IN-SCOPE-SIGNOFF-LATEST.md](./NAFY-IN-SCOPE-SIGNOFF-LATEST.md) · [NAFY-UAT-SIGNOFF-LATEST.md](./NAFY-UAT-SIGNOFF-LATEST.md)
