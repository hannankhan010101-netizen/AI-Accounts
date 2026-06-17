# P15 — Financial registry, Stripe portal, workflow gates, category pivot (implemented)

Builds on [P14-FOUNDATION.md](./P14-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P15.1 | **Financial report registry** | Slugs `TB`/`PNL`/`BS`/`GL`, `FIN_*`; numeric `203`–`206` aliases; `financialReportIds` on catalog coverage |
| P15.2 | **Trial balance by month** | `FIN_TB12` handler — month-end debit/credit totals |
| P15.3 | **Stripe Customer Portal** | `POST /billing/portal-session` (live Stripe or stub) |
| P15.4 | **Category P&L pivot** | `GET /reports/comparative-pnl-by-category/pivot` → `{ periods, rows[{ amounts }] }` |
| P15.5 | **Extended module gates** | Journal reverse, approval reject, PDC create/status/present/clear (bank) |

## Financial numeric map (provisional)

| ID | Resolves to | Report |
|----|-------------|--------|
| 203 | TB | Trial Balance |
| 204 | PNL | Profit and Loss |
| 205 | BS | Balance Sheet |
| 206 | GL | General Ledger |
| FIN_TB12 | FIN_TB12 | Trial Balance by Month |

Replace `203`–`206` in `report_aliases.py` when live Financial folder IDs are captured from tenant UI.

## Stripe Customer Portal

```http
POST /billing/portal-session
{ "returnUrl": "https://app.example/settings/module-subscriptions" }
```

Requires `externalCustomerId` on `SubscriptionRecord` (set via Checkout + Stripe webhook). Without a customer id, returns stub URL with a warning.

## Category pivot

```http
GET /reports/comparative-pnl-by-category/pivot?periodCount=12
```

```json
{
  "result": {
    "periods": ["2025-06", "2025-07"],
    "rows": [
      {
        "categoryType": "Income",
        "categoryName": "Sales",
        "amounts": { "2025-06": "1000.00", "2025-07": "1200.00" }
      }
    ]
  }
}
```

## Next (P16)

See [P16-FOUNDATION.md](./P16-FOUNDATION.md).
