# P0 — Accounting foundation (implemented)

Enterprise audit follow-up: closes the highest-severity ledger integrity and security gaps.

## What shipped

| ID | Capability | Location |
|----|------------|----------|
| P0.1 | **Draft → approve → post** for SI and VI | `POST .../sales-invoices` (draft), `POST .../sales-invoices/{id}/approve`, same for supplier bills |
| P0.2 | **PostingEngine** central orchestration | `app/services/posting_engine.py` |
| P0.3 | **RBAC deny-by-default** (no empty role) | `permission_service.py`, all tenant routes via `resolve_tenant` |
| P0.4 | **Posting prerequisites** (defaults + COA codes exist) | `posting_prerequisites_service.py` |
| P0.5 | **Stock adjustment → GL** | `POST .../stock-adjustments` posts DR/CR inventory/variance |
| — | **Journal traceability** | `journals.source_type`, `source_id`, `correlation_id` |
| — | **Workflow constants** | `app/domain/document_workflow.py` |

## Migration

```bash
cd Backend
prisma migrate deploy
# or: prisma migrate dev --name p0_foundation
```

Migration folder: `prisma/migrations/20260521160000_p0_foundation/`

## Smart Settings defaults required

### Sales invoice / supplier bill approve

- `receivablesNominalCode`, `salesNominalCode` (+ optional `gstOutputNominalCode`)
- `purchasesNominalCode`, `payablesNominalCode` (+ optional `gstInputNominalCode`)

Codes must exist on the company **Chart of Account**.

### Stock adjustment

- `inventoryNominalCode`
- `stockAdjustmentNominalCode` (stock variance / adjustment clearing)

## Permissions

| Action | Permission code |
|--------|-----------------|
| Create SI | `sales.invoices.create` |
| Approve SI | `sales.invoices.approve` (or `sales.*`, `*`) |
| Create VI | `purchases.bills.create` |
| Approve VI | `purchases.bills.approve` |
| Stock adjustment | `inventory.adjustments.create` |

Bootstrap **Administrator** role includes `*`.

## Breaking API change

- `POST /sales-invoices` and `POST /supplier-bills` no longer post to GL immediately; response `posted: false` with draft status.
- Clients must call **approve** endpoints (or SO/PO conversion which auto-approves when prerequisites pass).

## Next (P1)

- Outbox + workers for imports/reports
- Bank reconciliation
- AR/AP control account tie-out
- Immutable journal edits (reversal-only)
- COGS on sales invoice / goods issue
