# P11 — Module gates, custom fields, multi-UOM, Bank/Assembly reports (implemented)

Builds on [P10-FOUNDATION.md](./P10-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P11.1 | **Module entitlements** | `GET/PUT /module-entitlements` — per-company license flags |
| P11.2 | **Module gates** | `require_module()` on assembly create/finish, FBR submit, PayPro/Kuickpay initiate |
| P11.3 | **Custom field definitions** | `GET/POST /custom-field-definitions` |
| P11.4 | **Entity custom values** | `PATCH /customers/{id}/custom-fields`, `PATCH /products/{id}/custom-fields` |
| P11.5 | **Multi-UOM tiers** | `GET/POST /products/{id}/uoms` + product `unit`, `salePrice`, `category` |
| P11.6 | **Report 185 by custom field** | `groupByField=customFields.{key}` on runner |
| P11.7 | **Module reports** | `BANK_BAL`, `BANK_CF`, `ASM_JOB`, `PRJ_PAY`, `FIN_MTB` |
| P11.8 | **Migration** | `20260522000000_p11_foundation` |

## Module codes

`sales`, `purchases`, `bank`, `inventory`, `assembly`, `projects`, `financial`, `fbr`, `payments`

When no entitlement rows exist, **all modules default to enabled** (backward compatible).

## Custom fields example

```json
POST /custom-field-definitions
{
  "entityType": "customer",
  "fieldKey": "region",
  "label": "Sales region"
}

PATCH /customers/{id}/custom-fields
{ "customFields": { "region": "North" } }
```

Report **185** criteria: `{ "groupByField": "customFields.region" }`

## Multi-UOM example

```json
POST /products/{id}/uoms
{
  "unitCode": "CTN",
  "conversionFactor": "12",
  "salePrice": "1200",
  "isDefault": false
}
```

Report **181** lists all tiers per product.

## Module report routes

| ID | GET route |
|----|-----------|
| BANK_BAL | `/reports/bank-account-balances` |
| BANK_CF | `/reports/bank-cash-flow-monthly` |
| ASM_JOB | `/reports/assembly-job-cost-summary` |
| PRJ_PAY | `/reports/project-payments` |

`GET /reports/catalog-coverage` now includes `moduleReportIds` and `unmappedModuleReportIds`.

## Next

See [P12-FOUNDATION.md](./P12-FOUNDATION.md).
