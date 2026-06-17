# Nafy in-scope parity sign-off (latest)

**Generated:** 2026-05-30 10:23 UTC  
**Tenant:** `cmpfm1nst0001lhq3rz09938z` (Nafy-Pharma)  
**In-scope matrix:** 99/99 ✅ — **DONE**
**Data go-live gate:** **GO** (see GO-LIVE-SIGNOFF-LATEST.md)

## Excluded features (not licensed for this tenant)

- 2FA
- Asset register
- Bundle products
- Depreciation run
- Developer API keys UI
- Disposal + GL
- Distribution pricing (margin, trade offer, area qty)
- Emails add-on automation
- FA reports category
- Google Sign-In
- Import/export assets
- Inventory (Landed cost, LC)
- Landed cost
- Letter of credit
- POS mode
- Supplier notify email/SMS

## Release gates

| Gate | Status |
|------|--------|
| In-scope FA parity (99/99) | **DONE** |
| Migration / TB go-live (`_go_live_check.py`) | **GO** |
| Human UAT | **Pending** — complete [NAFY-UAT-CHECKLIST.md](./NAFY-UAT-CHECKLIST.md) |
| Prod integrations (FBR/email) | Configure on deploy — see Integration settings |

## Next steps

1. Deploy production (see [DEPLOY-QUICKSTART.md](./DEPLOY-QUICKSTART.md)).
2. Run `scripts/nafy-prod-handoff.ps1 -ApiUrl ... -FrontendUrl ... -RunGoLive`.
3. Complete [NAFY-UAT-CHECKLIST.md](./NAFY-UAT-CHECKLIST.md), then `scripts/record-uat-signoff.ps1` (see [NAFY-UAT-SIGNOFF-LATEST.md](./NAFY-UAT-SIGNOFF-LATEST.md)).

Regenerate: `python scripts/_generate_feature_matrix.py`
