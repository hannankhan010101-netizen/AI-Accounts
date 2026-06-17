# P17 — Invoice voids, stock rollback, Stripe subscription period (implemented)

Builds on [P16-FOUNDATION.md](./P16-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P17.1 | **Void posted sales invoice** | `POST /sales-invoices/{id}/void` — reverses AR + COGS/GI journals, restores batch qty |
| P17.2 | **Void posted supplier bill** | `POST /supplier-bills/{id}/void` |
| P17.3 | **Stock adjustment rollback** | Reverse SA applies `-quantityDelta` to `ProductBatch`; create SA applies `+delta` on post |
| P17.4 | **Stripe subscription period** | Checkout webhook fetches `current_period_end` via Stripe API when `subscription` id present |
| P17.5 | **Financial ID capture doc** | [FINANCIAL-REPORT-IDS.md](./FINANCIAL-REPORT-IDS.md) + `financialIdSource` on catalog coverage |

## Void sales invoice

```http
POST /sales-invoices/{invoice_id}/void
{ "reversalDate": "2026-05-21T00:00:00Z" }
```

If a goods issue exists: reverses COGS journal, restores stock to `ProductBatch` (`MAIN` batch), voids GI. Always reverses invoice AR journal when posted.

## Stock quantity

- **On post:** `PostingEngine.post_stock_adjustment` updates batch quantities from line `quantityDelta`.
- **On reverse:** `DocumentReversalService.reverse_stock_adjustment` negates those deltas before GL storno.

## Stripe

`checkout.session.completed` with `subscription` on the session object triggers `GET /v1/subscriptions/{id}` to set `SubscriptionRecord.currentPeriodEnd`. Metadata stores `stripeSubscriptionId`.

`customer.subscription.updated` continues to sync period end via existing `apply_stripe_event`.

## Next (P18)

See [P18-FOUNDATION.md](./P18-FOUNDATION.md).
