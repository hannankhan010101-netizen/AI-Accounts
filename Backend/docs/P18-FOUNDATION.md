# P18 — GRN void on bill, GI-only void, Stripe past_due, financial JSON IDs (implemented)

Builds on [P17-FOUNDATION.md](./P17-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P18.1 | **Financial ID JSON config** | `Backend/config/financial_report_ids.json` + optional `FINANCIAL_REPORT_IDS_FILE` |
| P18.2 | **Void bill + GRN** | `void_supplier_bill` reverses linked `GRNVI` notes and batch quantities |
| P18.3 | **Void goods issue only** | `POST /sales-invoices/{id}/void-goods-issue` — invoice stays posted |
| P18.4 | **Stripe payment failed** | `invoice.payment_failed` → `past_due` status + `past_due` plan (financial module only) |

## Financial report IDs

Override file: `Backend/config/financial_report_ids.json` (loaded by `financial_report_overrides.py`).

Set `FINANCIAL_REPORT_IDS_FILE` in `.env` to point at a tenant-specific capture file when live UI IDs differ.

## Void supplier bill with GRN

When voiding a posted supplier bill, all `GRNVI` goods receipt notes with `sourceId = bill_id` are:

1. Stock reversed on each line (`quantity` removed from `ProductBatch`)
2. Marked `voided`

Response includes `grnVoided` and `grnStockRollback`.

## Void goods issue only

```http
POST /sales-invoices/{invoice_id}/void-goods-issue
{ "reversalDate": "..." }
```

Reverses COGS journal and restores stock; does **not** void the sales invoice.

## Stripe `invoice.payment_failed`

Webhook event type `invoice.payment_failed`:

- Sets subscription `status` to `past_due`
- Syncs module entitlements to plan `past_due` (only `financial` enabled)
- Resolves company via Stripe `customer` id on `SubscriptionRecord` when metadata lacks `company_id`

Re-enable modules when `customer.subscription.updated` returns `active`.

## Environment

| Variable | Purpose |
|----------|---------|
| `FINANCIAL_REPORT_IDS_FILE` | Optional path to JSON numeric ID overrides |

## Next (P19)

See [P19-FOUNDATION.md](./P19-FOUNDATION.md).
