# P16 — Checkout customer sync, document voids, pivot CSV, financial numeric map (implemented)

Builds on [P15-FOUNDATION.md](./P15-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P16.1 | **Stripe checkout.completed** | `parse_stripe_webhook_event` routes `checkout.session.completed` → `apply_checkout_completed` (persists `externalCustomerId`) |
| P16.2 | **Financial numeric map (extended)** | `207`–`210` alias module reports; `203`–`206` remain core statement aliases |
| P16.3 | **Credit void + SA reverse** | `POST …/sales-credits/{id}/void`, `supplier-credits/{id}/void`, `stock-adjustments/{id}/reverse` with GL storno |
| P16.4 | **Module gates on voids** | `require_module_access` on all three reversal routes |
| P16.5 | **Pivot CSV export** | `GET /reports/comparative-pnl-by-category/pivot/export` |

## Stripe checkout webhook

On `checkout.session.completed`, metadata must include `company_id` and `plan_code`. The handler stores `customer` on `SubscriptionRecord.externalCustomerId` so **Manage billing** (Customer Portal) works.

## Document void / reverse

```http
POST /sales-credits/{credit_id}/void
POST /supplier-credits/{credit_id}/void
POST /stock-adjustments/{adjustment_id}/reverse
{ "reversalDate": "2026-05-21T00:00:00Z" }  // optional
```

Posted documents transition to `voided` (credits) or `reversed` (stock adjustment). When a `journalId` exists, a storno journal is created via `JournalService.reverse_journal`.

## Financial numeric map

| ID | Resolves to | Report |
|----|-------------|--------|
| 203 | TB | Trial Balance |
| 204 | PNL | Profit and Loss |
| 205 | BS | Balance Sheet |
| 206 | GL | General Ledger |
| 207 | FIN_PNL_CAT | Comparative P&L by Category |
| 208 | FIN_TB12 | Trial Balance by Month |
| 209 | FIN_CMP | Comparative P&L |
| 210 | FIN_MTB | Monthly Income vs Expense |

## Pivot CSV

```http
GET /reports/comparative-pnl-by-category/pivot/export?periodCount=12
```

Returns `text/csv` attachment `comparative-pnl-by-category.csv`.

## Next (P17)

See [P17-FOUNDATION.md](./P17-FOUNDATION.md).
