# Go-live verification (latest run)

**Generated:** 2026-05-30 10:23 UTC  
**Tenant:** `cmpfm1nst0001lhq3rz09938z`  
**Overall:** **GO** (preflight + reconcile + TB pass)

| Check | Required | Result | Exit |
|-------|----------|--------|------|
| preflight_deploy | yes | PASS | 0 |
| reconcile | yes | PASS | 0 |
| trial_balance | yes | PASS | 0 |
| migration_health | no | PASS | 0 |
| report_spot_check | no | PASS | 0 |
| integrations | no | PASS | 0 |
| ar_ap_aging | no | REVIEW | 1 |

## Notes

- AR/AP and party aging often **REVIEW** with summary GL migration.
- ~47 draft SI / ~17 draft VI are expected; do not bulk-post on summary GL.
- Nafy in-scope parity: see [NAFY-IN-SCOPE-SIGNOFF-LATEST.md](./NAFY-IN-SCOPE-SIGNOFF-LATEST.md).
- Human UAT: [NAFY-UAT-CHECKLIST.md](./NAFY-UAT-CHECKLIST.md).
- Re-run: `python scripts/fastaccounts_migrate/_go_live_check.py`
- Full runbook: [GO-LIVE-RUNBOOK.md](./GO-LIVE-RUNBOOK.md)
