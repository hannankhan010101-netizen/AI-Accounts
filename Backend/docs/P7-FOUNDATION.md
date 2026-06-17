# P7 — Kuickpay, FBR poll, ClickHouse MV, inventory reports, frontend (implemented)

Builds on [P6-FOUNDATION.md](./P6-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P7.1 | **Kuickpay** | `GET/POST /payments/kuickpay/*` — same flow as PayPro, provider `kuickpay` |
| P7.2 | **Settlement + FIFO** | `PaymentSettlementHelper` — auto sales receipt + `allocate_sales_receipt(auto_fifo=True)` |
| P7.3 | **FBR status poll** | `POST /sales-invoices/{id}/fbr/poll` — PRAL GET or stub |
| P7.4 | **ClickHouse MV** | `ClickHouseSchemaService.ensure_schema` — daily aggregate MV; startup + `POST .../platform/clickhouse/ensure-schema` |
| P7.5 | **ClickHouse sync** | `POST .../platform/clickhouse/sync-recent-runs` — re-export last 7 days |
| P7.6 | **Inventory report SQL** | Handlers `079` price list, `082` out of stock, `083` low stock (`lowStockThreshold`) |
| P7.7 | **Frontend** | Invoice FBR panel; Settings → Online payments (PayPro/Kuickpay) |

## Environment

| Variable | Purpose |
|----------|---------|
| `KUICKPAY_ENABLED` | Live Kuickpay checkout |
| `KUICKPAY_API_URL` | Checkout API base |
| `KUICKPAY_MERCHANT_ID` | Merchant id |
| `KUICKPAY_API_KEY` | Bearer token |
| `KUICKPAY_WEBHOOK_SECRET` | `X-Kuickpay-Signature` verification |

Smart Settings `defaults`:

- `payproDefaultBankAccountId`
- `kuickpayDefaultBankAccountId`

## Next

See [P8-FOUNDATION.md](./P8-FOUNDATION.md).
