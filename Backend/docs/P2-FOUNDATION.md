# P2 — Inventory, imports, PDC, reports (implemented)

Builds on [P1-FOUNDATION.md](./P1-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P2.1 | **Goods issue voucher** | `POST/GET .../sales-invoices/{id}/goods-issue` — COGS journal `GOODS_ISSUE`, one issue per invoice |
| P2.2 | **COGS decoupled from SI approve** | Invoice approve posts revenue/AR only; stock relief via goods issue |
| P2.3 | **Import row processors** | `customers`, `products`, `bank_payments` via `import_handlers.py` + outbox worker |
| P2.4 | **Import job payload** | `POST .../import-jobs` accepts `rows[]`; stored in `import_jobs.payload` |
| P2.5 | **Report SQL catalog (partial)** | `ReportQueryService` — IDs `028`, `029`, `035`, `047`, `048`, `067`, `071`, `078`, `148`, `300` |
| P2.6 | **PDC present / clear** | `POST .../pdc-received/{id}/present`, `/clear`; `POST .../pdc-issued/{id}/present`, `/clear` |

## Migration

```bash
cd Backend
python -m prisma migrate deploy
python -m prisma generate
```

Folder: `prisma/migrations/20260521180000_p2_foundation/`

## Goods issue flow

1. Create and **approve** sales invoice (draft → posted GL for revenue).
2. `POST .../sales-invoices/{id}/goods-issue` — posts COGS / inventory relief when stock lines have `product.cost > 0`.
3. Requires Smart Settings: `cogsNominalCode`, `inventoryNominalCode`.

## Import jobs

```json
POST /api/v1/companies/{id}/import-jobs
{
  "jobType": "customers",
  "rows": [{ "code": "C001", "name": "Acme Ltd" }]
}
```

Supported `jobType` values: `customers`, `products`, `bank_payments`.

## PDC lifecycle

| Step | Received (PDCR) | Issued (PDCI) |
|------|-----------------|---------------|
| Register | `POST /pdc-received` | `POST /pdc-issued` |
| Present | `POST .../present` | `POST .../present` |
| Clear | `POST .../clear` + `bankAccountId` → sales receipt + GL + FIFO alloc | `POST .../clear` → supplier payment + GL + FIFO alloc |

Generic `PUT .../status` remains for bounced/cancelled.

## Report runs

Outbox worker now calls `ReportQueryService` for all enqueued report IDs listed above.

## Next (P3)

- Excel file upload parser (not just JSON rows)
- Full report catalog + export formats
- GRNI, assembly, FX, approval engine runtime
- Nominal code FK on journal lines
- Frontend: goods issue + PDC clear + import UI
