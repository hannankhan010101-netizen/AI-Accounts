# P20 — Delivery void hooks, COGS repost, module gates (implemented)

Builds on [P19-FOUNDATION.md](./P19-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P20.1 | **GDNSI void on invoice void** | `void_sales_invoice` voids linked `GDNSI` delivery notes (`deliveryNotesVoided`) |
| P20.2 | **GDNSO void on SO cancel** | `PUT /sales-orders/{id}/status` with `cancelled` voids `GDNSO` notes |
| P20.3 | **Delivery note void** | `POST /delivery-notes/{id}/void` |
| P20.4 | **Repost remaining COGS** | `POST /sales-invoices/{id}/goods-issue/repost-remaining-cogs` — reverses header GI journal and posts sum of active lines |
| P20.5 | **Module gates** | `require_module_access` on quotation/SO status, receipt allocate, customer/supplier/product creates |

## Delivery note void hooks

- **GDNSI:** `sourceKind=GDNSI`, `sourceId=invoice_id` — voided when the sales invoice is voided.
- **GDNSO:** voided when the sales order status becomes `cancelled` (response includes `deliveryNotesVoided`).
- Standalone void for any delivery note via `POST /delivery-notes/{note_id}/void`.

Delivery notes do not move stock; void is status-only.

## Repost remaining COGS

After partial line voids (P19), call:

```http
POST /sales-invoices/{invoice_id}/goods-issue/repost-remaining-cogs
{ "reversalDate": "..." }
```

Reverses the current goods-issue COGS journal (if any) and posts a new journal for `sum(quantity × unitCost)` on lines with `quantity > 0`. Updates `goodsIssue.journalId`.

Use when partial line stornos exist and the header COGS journal should match remaining lines only.

## Module gates (P20)

| Route | Module |
|-------|--------|
| `PUT /quotations/{id}/status` | sales |
| `PUT /sales-orders/{id}/status` | sales |
| `POST /sales-receipts/{id}/allocate` | sales |
| `POST /customers` | sales |
| `POST /suppliers` | purchases |
| `POST /products` | inventory |

## Next (P21)

See [P21-FOUNDATION.md](./P21-FOUNDATION.md).
