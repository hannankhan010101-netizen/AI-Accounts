# P3 — Approval runtime, imports, GRNI, reports export (implemented)

Builds on [P2-FOUNDATION.md](./P2-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P3.1 | **Approval engine** | Policy `minAmount` / `requiresApprovalAbove`; blocks SI/VI approve until `POST .../approval-requests` approved |
| P3.2 | **Approval queue** | `GET/POST /approval-requests`, `POST .../{id}/approve`, `POST .../{id}/reject` |
| P3.3 | **Excel/CSV import** | `POST .../import-jobs/upload?jobType=` multipart file; `openpyxl` for `.xlsx` |
| P3.4 | **GRNI report** | `GET /reports/grni` and report run id `GRNI` |
| P3.5 | **Report export** | `POST .../reports/runs/{id}/export` returns inline `content` for `csv` / `json` |
| P3.6 | **More report SQL** | IDs `032`, `080`, `174` in `ReportQueryService` |
| P3.7 | **Journal nominal FK** | `JournalLine.nominalAccountId` set on create when code exists on COA |
| P3.8 | **Frontend** | Goods issue on invoice detail; PDC present/clear; Settings import jobs page |

## Migration

```bash
cd Backend
pip install openpyxl python-multipart
python -m prisma migrate deploy
python -m prisma generate
```

Folder: `prisma/migrations/20260521190000_p3_foundation/`

## Approval policy example

```json
PUT /api/v1/companies/{id}/approval-policies
{
  "entityType": "sales_invoice",
  "rules": { "minAmount": 50000 }
}
```

Flow:

1. Create draft sales invoice ≥ threshold.
2. `POST /approval-requests` with `entityType`, `entityId`, `amount`.
3. Approver calls `POST /approval-requests/{id}/approve`.
4. `POST /sales-invoices/{id}/approve` posts to GL.

Entity types: `sales_invoice`, `supplier_bill`.

## Import upload

```http
POST /api/v1/companies/{id}/import-jobs/upload?jobType=customers
Content-Type: multipart/form-data
file: customers.xlsx
```

## Next (P4)

- Full report catalog parity + PDF export
- Assembly jobs, FX revaluation
- FBR / payment gateway integrations
- Immutable journal line edits blocked at repository layer
- Per-user lock date enforcement on all routes
