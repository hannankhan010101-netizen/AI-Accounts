# Parity progress (latest)

**Generated:** 2026-05-30 10:23 UTC  
**Source:** `Backend/docs/FA-FEATURE-MATRIX.csv` (115 rows)

## Signals

| Gate | Status |
|------|--------|
| Nafy **go-live** | **GO** (see GO-LIVE-SIGNOFF-LATEST.md) |
| **Nafy in-scope parity** | **DONE** |
| **Full FA catalog parity** | **NOT DONE** |

## Matrix counts

| Done | Partial | Missing | Full parity % |
|------|---------|---------|---------------|
| 99 | 0 | 16 | 86.1% |

## Nafy in-scope parity (pharmacy tenant)

Excludes **16** licensed add-on rows listed in `Backend/config/nafy_parity_exclusions.json`.

| In-scope rows | Done | Partial | Missing | Nafy scope % |
|---------------|------|---------|---------|--------------|
| 99 | 99 | 0 | 0 | 100.0% |

| **Nafy in-scope parity** | **DONE** |

## Nafy release exit criteria

- [x] In-scope matrix: 99/99 done (see [NAFY-IN-SCOPE-SIGNOFF-LATEST.md](./NAFY-IN-SCOPE-SIGNOFF-LATEST.md))
- [x] `_go_live_check.py` required gates PASS
- [ ] Production deploy smoke (`nafy-prod-handoff.ps1`)
- [ ] Human UAT recorded ([NAFY-UAT-CHECKLIST.md](./NAFY-UAT-CHECKLIST.md) · [NAFY-UAT-SIGNOFF-LATEST.md](./NAFY-UAT-SIGNOFF-LATEST.md))
- [ ] Production Brevo/FBR env configured if licensed

## Full catalog parity exit criteria (all 115 FA rows)

- [ ] `FA-FEATURE-MATRIX.csv`: zero partial/missing
- [ ] Licensed add-ons implemented or permanently N/A
- [ ] Authenticated Playwright parity in CI (`PLAYWRIGHT_AUTH_READY=1`)

## Open rows by FA section (not full done)

- §8 Fixed assets: 5
- §1 Product entry & tenancy: 3
- §7 Inventory: 3
- §3 Cross-cutting: 2
- §2 Global navigation: 1
- §5 Sales: 1
- §6 Purchases: 1

## Regenerate

```powershell
python scripts/_generate_feature_matrix.py
python scripts/_parity_progress.py
```

Tracker: [AI-ACCOUNTS-PARITY-STATUS.md](./AI-ACCOUNTS-PARITY-STATUS.md)
