# P14 — Stripe Checkout, assembly reports, category P&L, approve/convert gates (implemented)

Builds on [P13-FOUNDATION.md](./P13-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P14.1 | **Stripe Checkout** | `POST /billing/checkout-session` — live Stripe when `STRIPE_SECRET_KEY` set, else dev stub URL |
| P14.2 | **Comparative P&L by category** | `FIN_PNL_CAT` handler; `GET /reports/comparative-pnl-by-category` |
| P14.3 | **Assembly report IDs** | `201`→`ASM_JOB`, `202`→`ASM_WIP`, `ASM_COMP`, `ASM_WIP`; `assemblyReportIds` on catalog coverage |
| P14.4 | **Module gates on workflow** | `require_module_access` on invoice/bill approve, goods issue, document conversions, approval approve |

## Stripe Checkout

```http
POST /billing/checkout-session
{
  "planCode": "starter",
  "successUrl": "https://app.example/settings/module-subscriptions?checkout=success",
  "cancelUrl": "https://app.example/settings/module-subscriptions?checkout=cancel"
}
```

Returns `{ mode, sessionId, url, planCode }`. Subscription metadata on Stripe must include `company_id` and `plan_code` (same as P13 webhook).

## Comparative P&L by category

```http
GET /reports/comparative-pnl-by-category?periodCount=12
```

Returns rows: `{ period, categoryType, categoryName, amount }` for each Income/Expense category per month.

Report runner: `POST /reports/runs` with `reportId: "FIN_PNL_CAT"`.

## Assembly numeric map

| ID | Resolves to | Report |
|----|-------------|--------|
| 201 | ASM_JOB | Job cost summary |
| 202 | ASM_WIP | Open assembly jobs |
| ASM_COMP | ASM_COMP | Component cost lines per job |

## Environment

| Variable | Purpose |
|----------|---------|
| `STRIPE_SECRET_KEY` | Stripe API key for Checkout |
| `STRIPE_PRICE_STARTER` | Price id for starter plan |
| `STRIPE_PRICE_PRO` | Price id for pro plan |
| `APP_PUBLIC_URL` | Default success/cancel URLs (default `http://localhost:3000`) |
| `STRIPE_WEBHOOK_SECRET` | P13 webhook verification |

## Next (P15)

See [P15-FOUNDATION.md](./P15-FOUNDATION.md).
