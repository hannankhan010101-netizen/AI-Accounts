# P1 — Operational integrity (implemented)

Builds on [P0-FOUNDATION.md](./P0-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P1.1 | **Outbox + worker** | `outbox_events` table; `OutboxWorkerService`; background poll in `main.py` (15s); `POST .../platform/process-outbox` |
| P1.1b | **Durable report runs** | `report_runs` table; `POST .../reports/runs` → pending + outbox |
| P1.1c | **Import jobs queued** | `POST .../import-jobs` enqueues `import_job.process` |
| P1.2 | **Bank reconciliation** | `POST/GET .../bank-reconciliations`, clear-items, complete |
| P1.3 | **AR/AP tie-out** | `GET .../reports/subledger-tieout/ar` and `/ap` |
| P1.4 | **COGS on SI approve** | Second journal `SALES_INVOICE_COGS` when stock lines have `product.cost` |
| P1.5 | **Journal reversal** | `POST .../journals/{id}/reverse`; original `status=reversed` |

## Migration

```bash
cd Backend
prisma migrate deploy
prisma generate
```

Folder: `prisma/migrations/20260521170000_p1_foundation/`

## Smart Settings (additional)

- `cogsNominalCode` — COGS expense account
- `inventoryNominalCode` — already used for stock adjustments

## Permissions (new)

| Action | Code |
|--------|------|
| Process outbox | `settings.platform.process` (or `*`) |
| Bank recon start | `bank.reconciliation.create` |
| Bank recon clear | `bank.reconciliation.update` |
| Bank recon complete | `bank.reconciliation.complete` |
| Reverse journal | `settings.journals.reverse` |

## Bank reconciliation flow

1. `POST /bank-reconciliations` — supplies statement date/balance; loads uncleared bank movements as items.
2. `POST .../{id}/clear-items` — tick items that appear on the statement.
3. `POST .../{id}/complete` — compares cleared total vs statement balance.

## Report runs

1. `POST /reports/runs` → `status: pending`
2. Worker executes (poll or manual `process-outbox`)
3. `GET /reports/runs/{id}` → `completed` with `rows`

Implemented queries: report `071` (bank payments list), `028` (posted sales invoices stub).

## Environment

- `OUTBOX_POLL_ENABLED=1` (default) — background worker in API process
- Set `OUTBOX_POLL_ENABLED=0` for tests or single-worker deploys using external cron hitting `process-outbox`

## Next (P2)

- Real Excel import parsers
- ClickHouse / read replica for analytics
- Goods issue document separate from invoice COGS
- PDC present/clear
- Full report catalog SQL
