# P12 — Access matrix, field validation, module reports, billing stub (implemented)

Builds on [P11-FOUNDATION.md](./P11-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P12.1 | **Module ↔ permission matrix** | `module_permission_matrix.py` + `GET /module-access-matrix` |
| P12.2 | **require_module_access** | Entitlement + RBAC on sales/purchases/bank/inventory/assembly/FBR/payments |
| P12.3 | **Custom field validation** | `isRequired`, `picklistOptions`, types `text/number/date/picklist` |
| P12.4 | **Extended module reports** | `BANK_REC`, `BANK_XFR`, `BANK_ACT`, `ASM_TPL`, `FIN_CMP` (+ P11 set) |
| P12.5 | **Billing stub** | `SubscriptionRecord`, `GET /billing/status`, `POST /billing/webhook` |
| P12.6 | **Plan → modules** | `starter` / `pro` / `standard` syncs entitlements on webhook |

## Module access matrix

Each module requires the subscription flag **and** at least one permission from the matrix (or `*`).

Example: `sales` → `sales.invoices.create`, `sales.invoices.approve`, or `sales.*`.

## Custom fields

```json
POST /custom-field-definitions
{
  "entityType": "customer",
  "fieldKey": "tier",
  "label": "Customer tier",
  "fieldType": "picklist",
  "isRequired": true,
  "picklistOptions": ["Gold", "Silver", "Bronze"]
}
```

Invalid picklist values return 422 on `PATCH .../custom-fields`.

## Billing webhook (stub)

```http
POST /api/v1/companies/{companyId}/billing/webhook
X-Billing-Secret: <BILLING_WEBHOOK_SECRET>
{
  "companyId": "...",
  "eventType": "subscription.updated",
  "planCode": "starter"
}
```

Sets `SubscriptionRecord` and replaces module entitlements per plan.

## Environment

| Variable | Purpose |
|----------|---------|
| `BILLING_WEBHOOK_SECRET` | Optional HMAC-less shared secret for billing webhook |

## Migration

`20260522120000_p12_foundation`

## Next

See [P13-FOUNDATION.md](./P13-FOUNDATION.md).
