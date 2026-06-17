# P10 — Full catalog SQL parity, external secrets, PayPro rotation (implemented)

Builds on [P9-FOUNDATION.md](./P9-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P10.1 | **Last catalog handlers** | Reports `175`, `181`, `185`, `311` in `ReportQueryService` |
| P10.2 | **Catalog coverage 100%** | `unmappedCatalogIds` empty for §10.11 registry set |
| P10.3 | **AWS Secrets Manager** | `SECRETS_AWS_SECRET_ARN` + optional `boto3` extra |
| P10.4 | **HashiCorp Vault KV** | `VAULT_ADDR`, `VAULT_TOKEN`, `VAULT_SECRET_PATH` |
| P10.5 | **Unified bootstrap** | `bootstrap_secrets()` at startup (file → AWS → Vault) |
| P10.6 | **Extended report routes** | GET `/reports/advanced-stock-quantity`, `multi-unit-price-list`, `sale-summary-by-field`, `customer-field-activity` |
| P10.7 | **PayPro rotation runbook** | [PAYPRO-CREDENTIAL-ROTATION.md](./PAYPRO-CREDENTIAL-ROTATION.md) |
| P10.8 | **Frontend** | Reports hub links + Settings → Report catalog coverage |

## Report handlers (final four)

| ID | Name | Notes |
|----|------|-------|
| 175 | Advanced Stock Quantity | Batches aggregated per product + valuation |
| 181 | Multi-Unit Price List | Uses product cost as list price until UOM schema |
| 185 | Sale Summary (By Field) | `groupByField` criteria (default `productCode`) |
| 311 | Customer Field Activity Summary | Invoice count and sales per customer in range |

## Environment

| Variable | Purpose |
|----------|---------|
| `SECRETS_VAULT_FILE` | JSON file overlay (P9) |
| `SECRETS_AWS_SECRET_ARN` or `SECRETS_AWS_SECRET_ID` | AWS SM JSON secret |
| `SECRETS_AWS_REGION` | AWS region (default `us-east-1`) |
| `VAULT_ADDR` | e.g. `https://vault.example.com` |
| `VAULT_TOKEN` | Vault token with read on path |
| `VAULT_SECRET_PATH` | KV v2 path, e.g. `secret/data/fast-accounts/prod` |

Install AWS support: `pip install -e ".[secrets-aws]"`

## Next

See [P11-FOUNDATION.md](./P11-FOUNDATION.md).
