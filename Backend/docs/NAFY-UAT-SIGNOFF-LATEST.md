# Nafy UAT sign-off (latest)

**Generated:** 2026-05-30 10:23 UTC  
**Tenant:** `cmpfm1nst0001lhq3rz09938z` (Nafy-Pharma)  
**Status:** **Pending** — no recorded sign-off yet.

## How to record

1. Complete every row in [NAFY-UAT-CHECKLIST.md](./NAFY-UAT-CHECKLIST.md).
2. Run:

```powershell
.\scripts\record-uat-signoff.ps1 `
  -BusinessOwner "..." -Finance "..." -TechnicalLead "..." `
  -Result PASS
```

Template: `Backend/config/nafy_uat_signoff.json.example`
