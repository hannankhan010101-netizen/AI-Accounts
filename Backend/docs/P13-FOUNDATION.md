# P13 — Bank/Financial numeric IDs, Stripe webhooks, module gates, multi-period P&L (implemented)

Builds on [P12-FOUNDATION.md](./P12-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P13.1 | **Bank/Financial numeric IDs** | `072`–`077`, `300`, `475`, `477` aliased to SQL handlers |
| P13.2 | **Catalog coverage** | `bankFinancialNumericIds` + `unmappedBankFinancialIds` on `/reports/catalog-coverage` |
| P13.3 | **Multi-period comparative P&L** | `FIN_CMP` returns one row per month; `GET /reports/comparative-profit-and-loss` |
| P13.4 | **Stripe webhook** | `POST /billing/webhook/stripe` with `Stripe-Signature` HMAC verification |
| P13.5 | **Extended module gates** | `require_module_access` on receipts, transfers, journals, orders, credits, GRN/GDN, FX, reconciliation |

## Bank / Financial numeric map

| ID | Resolves to | Report |
|----|-------------|--------|
| 072 | BANK_REC | Bank Receipts |
| 073 | BANK_BAL | Account Balances |
| 074 | BANK_ACT | Activity Summary |
| 076 | BANK_XFR | Transfers |
| 077 | BANK_CF | Cash Flow Monthly |
| 300 / 475 / 477 | 300 | Payment & Receipts / Nominal summaries |

## Comparative P&L

```http
GET /reports/comparative-profit-and-loss?periodCount=12
```

Returns `[{ period, totalIncome, totalExpense, netProfit }, …]` for each calendar month.

Report runner: `POST /reports/runs` with `reportId: "FIN_CMP"` and `criteria.periodCount`.

## Stripe webhook

Configure `STRIPE_WEBHOOK_SECRET` (Stripe CLI `whsec_…`).

Metadata on the Stripe subscription object must include:

- `company_id` — tenant company id
- `plan_code` — `starter` | `pro` | `standard`

## Environment

| Variable | Purpose |
|----------|---------|
| `STRIPE_WEBHOOK_SECRET` | Stripe signing secret |
| `BILLING_WEBHOOK_SECRET` | Generic billing stub (P12) |

## Next (P14)

See [P14-FOUNDATION.md](./P14-FOUNDATION.md).
