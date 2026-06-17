# P19 — GRNPO cancel, partial GI void, Stripe hard lock, GRN stock on create (implemented)

Builds on [P18-FOUNDATION.md](./P18-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P19.1 | **GRNPO void on PO cancel** | `PUT /purchase-orders/{id}/status` with `status: cancelled` voids linked `GRNPO` notes and rolls back batch qty |
| P19.2 | **Partial goods issue void** | `POST /sales-invoices/{id}/goods-issue/lines/{line_id}/void` — line COGS storno + stock restore; full GI void when all lines zeroed |
| P19.3 | **Stripe subscription deleted** | `customer.subscription.deleted` → plan `cancelled` with **no** modules enabled |
| P19.4 | **GRN stock on create** | `POST /goods-receipt-notes` applies `apply_grn_receipt_lines` after create (`stockApplied` in response) |

## Purchase order cancel + GRNPO

When status is set to `cancelled`, the response wraps the order and includes:

- `grnVoided` — voucher numbers voided
- `grnStockRollback` — per-line batch adjustments

Non-cancelled status transitions return the order row only (unchanged shape).

## Partial goods issue void

```http
POST /sales-invoices/{invoice_id}/goods-issue/lines/{line_id}/void
{ "reversalDate": "..." }
```

Posts a partial journal (DR inventory, CR COGS), restores stock for that line, zeros line quantity. When every line is zero, the goods issue header is marked `voided`.

## Stripe hard lock

`PLAN_MODULE_DEFAULTS["cancelled"]` is empty. `customer.subscription.deleted` and `subscription.cancelled` sync entitlements to that plan (distinct from `past_due`, which keeps `financial`).

## GRN create stock

Creating a goods receipt note increases `ProductBatch` quantities for each line with positive qty. Void paths (`reverse_grn_receipt_lines`) remain the inverse.

## Next (P20)

See [P20-FOUNDATION.md](./P20-FOUNDATION.md).
