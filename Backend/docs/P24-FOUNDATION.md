# P24 — GRN void route, permission seed doc, manual GRN guard (implemented)

Builds on [P23-FOUNDATION.md](./P23-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P24.1 | **Standalone GRN void** | `POST /goods-receipt-notes/{id}/void` — stock rollback + status `voided` |
| P24.2 | **Permission seed doc** | [PERMISSION-SEED.md](./PERMISSION-SEED.md) — bootstrap Administrator `*`, operator codes, role templates |
| P24.3 | **Manual GRN duplicate guard** | `assert_grn_receipt_allowed` includes `manual` + `sourceId` |

## GRN void

```http
POST /goods-receipt-notes/{note_id}/void
```

Response `result` includes `goodsReceiptNote`, `voided`, and `stockRollback` (per-line batch adjustments).

Requires **purchases** module access.

## Manual GRN guard

Creating a **manual** GRN with the same `sourceId` as an existing non-voided note is rejected unless `skipStockMovement=true` (document-only duplicate).

## Next (P25)

See [P25-FOUNDATION.md](./P25-FOUNDATION.md).
