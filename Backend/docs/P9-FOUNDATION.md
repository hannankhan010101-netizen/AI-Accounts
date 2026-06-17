# P9 — Secrets vault, catalog registry, FBR backoff, allocation UI, hardening (implemented)

Builds on [P8-FOUNDATION.md](./P8-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P9.1 | **Secrets vault file** | `SECRETS_VAULT_FILE` JSON merged into env at startup (`secrets_resolver.py`) |
| P9.2 | **FBR exponential backoff** | `FBR_MAX_RETRY_COUNT`, `FBR_RETRY_BASE_MINUTES`; status `abandoned` when exceeded |
| P9.3 | **Webhook rate limits** | `RATE_LIMIT_WEBHOOKS_PER_MINUTE` (default 120) |
| P9.4 | **Security audit** | `SecurityAuditService` on PayPro/Kuickpay webhook settle |
| P9.5 | **Explicit payment allocations** | Webhook body `allocations[]` + `autoFifo`; settlement helper |
| P9.6 | **Receipt allocate API** | `POST /sales-receipts/{id}/allocate` |
| P9.7 | **Report catalog registry** | `report_catalog_registry.py` + `GET /reports/catalog-coverage` |
| P9.8 | **Report handlers** | `051` purchase by supplier, `143` customer outstanding items |
| P9.9 | **Frontend** | Receipt detail allocation picker for unallocated balance |

## Environment

| Variable | Default | Purpose |
|----------|---------|---------|
| `SECRETS_VAULT_FILE` | — | Path to JSON `{"FBR_PRAL_API_KEY":"…", …}` |
| `FBR_MAX_RETRY_COUNT` | 5 | Stop retrying; mark `abandoned` |
| `FBR_RETRY_BASE_MINUTES` | 15 | Exponential backoff base (×2 per attempt, cap 24h) |
| `RATE_LIMIT_WEBHOOKS_PER_MINUTE` | 120 | Per-IP webhook throttle |
| `RATE_LIMIT_AUTH_PER_MINUTE` | 30 | Per-IP throttle on `POST /auth/login` |

## Secrets vault example

```json
{
  "FBR_PRAL_API_KEY": "prod-key",
  "PAYPRO_API_KEY": "prod-paypro",
  "PAYPRO_WEBHOOK_SECRET": "whsec-…"
}
```

Mount via K8s secret volume at container start; existing env vars take precedence.

## PayPro webhook with allocations

```json
{
  "merchantRef": "PP-…",
  "autoFifo": false,
  "allocations": [
    { "invoiceId": "inv_1", "amount": "500.00" },
    { "invoiceId": "inv_2", "amount": "250.00" }
  ]
}
```

## Production checklist

See [PRODUCTION-HARDENING.md](./PRODUCTION-HARDENING.md).

## Next

See [P10-FOUNDATION.md](./P10-FOUNDATION.md).
