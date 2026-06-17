# Go-live runbook — Nafy-Pharma (FastAccounts migration)

Tenant: `cmpfm1nst0001lhq3rz09938z`

**Production hosting:** see [PRODUCTION-DEPLOYMENT.md](./PRODUCTION-DEPLOYMENT.md) · **First deploy:** [DEPLOY-QUICKSTART.md](./DEPLOY-QUICKSTART.md)

## Prerequisites

- `Backend/.env` with `DIRECT_URL` (session pooler `:5432`) for scripts
- Smart Settings defaults: receivables, payables, sales, purchases, bank nominals
- Migrations applied: `python Backend/scripts/migrate_deploy.py`

## Verification (run in order)

```bash
# From repo root (one command)
python scripts/fastaccounts_migrate/_go_live_check.py
# or: .\scripts\go-live.ps1   /   ./scripts/go-live.sh
python scripts/fastaccounts_migrate/_migration_health.py
python scripts/fastaccounts_migrate/_report_spot_check.py
```

| Check | Pass criteria |
|-------|----------------|
| Pre-flight | Env + Smart Settings posting defaults + bank nominals |
| Reconcile | Transaction doc counts match FA export |
| Trial balance | Total debits = total credits |
| Migration health | No posted docs without `journalId`; drafts OK |
| AR/AP aging | **REVIEW** expected with summary GL (6 nominals) |
| Priority report spot-check | **PASS** — `_report_spot_check.py` (TB/PNL/GL + sales/purchases/aging) |
| Report spot check | Priority reports return rows (budget vs actual may be empty if no budgets) |

## Draft documents (64 total)

- ~47 sales invoices and ~17 supplier bills remain **draft** (no `journalId`)
- This is normal for unpaid/open FA documents
- **Do not** run `_bulk_post_drafts.py` on this tenant unless moving to open-item GL
- Approve individual documents in the UI when they should post

## Bulk post (only when intentional)

```bash
python scripts/fastaccounts_migrate/_bulk_post_drafts.py --dry-run
# Live post requires explicit acknowledgment:
python scripts/fastaccounts_migrate/_bulk_post_drafts.py --i-understand-summary-gl-risk --limit 100
```

## Import jobs

- Draft import: default for SI/SR/VI/VP
- Post during import: checkbox **Post to GL** or column `status=posted`
- See Settings → Import jobs

## Integrations (post go-live)

1. Settings → **Integration status** — shows FBR/PayPro/Kuickpay env readiness (no secrets).
2. Configure `FBR_PRAL_*`, `PAYPRO_*`, `KUICKPAY_*` in API `.env` (see `Backend/.env.example`).
3. FBR errors: Settings → **FBR errors** → queue retries when PRAL is live.
4. PayPro: Settings → **Online payments**; webhook must reach `POST .../payments/paypro/webhook`.

CLI: `python scripts/fastaccounts_migrate/_integrations_readiness.py`

## Month-end scope

**In scope:** SI, VI, SR, VP, bank EP/IR, journals, TB, P&L, BS, statements, activity lists  
**Out of scope / REVIEW:** Party aging vs FA snapshot, full 200+ report FA tree parity, prod FBR/PayPro until credentials configured

## Sign-off

After `_go_live_check.py`, open the generated summary:

`Backend/docs/GO-LIVE-SIGNOFF-LATEST.md`

Record operator name and approval in your change log. Parity tracker: `Backend/docs/AI-ACCOUNTS-PARITY-STATUS.md`.

After human UAT, record sign-off:

```powershell
.\scripts\record-uat-signoff.ps1 -BusinessOwner "..." -Finance "..." -TechnicalLead "..." -Result PASS
```

Business release gate (parity + data GO + UAT): `python scripts/_parity_progress.py --strict-nafy-release`

### UI smoke (optional)

```bash
cd Frontend
npx playwright test e2e/parity/smoke.spec.ts
# Authenticated: see Frontend/e2e/README.md
```
