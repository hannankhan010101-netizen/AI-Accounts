# P26 — Assign role, list read expansion, permission validation (implemented)

Builds on [P25-FOUNDATION.md](./P25-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P26.1 | **Assign user role** | `PATCH /users/{user_id}/role` with `{ "roleId": "..." }` |
| P26.2 | **List route gates** | `require_module_list_read` on bank, sales docs, purchases docs, inventory, assembly, COA, imports, approvals |
| P26.3 | **Permission validation** | `unknownPermissions` + `permissionWarnings` on role create/update |

## Assign role

```http
PATCH /users/{user_id}/role
{ "roleId": "clxxx..." }
```

Requires `settings.roles.manage`. User must already be a company member.

## Permission validation

Role save accepts any codes but returns warnings for codes not in the catalog or module matrix, e.g.:

```json
{
  "result": { "id": "...", "name": "Clerk", "permissions": ["sales.read", "foo.bar"] },
  "unknownPermissions": ["foo.bar"],
  "permissionWarnings": ["Unknown permission code: foo.bar"]
}
```

Saving still succeeds — fix typos using `GET /permissions/catalog`.

## List reads (expanded)

Additional gated list routes include: bank accounts/payments/receipts/transfers/reconciliations, sales receipts, supplier payments, quotations, orders, credits, journals, stock adjustments/transfers, assembly templates/jobs, import jobs, approval requests, module entitlements, COA categories/sections.

## Next (P27)

See [P27-FOUNDATION.md](./P27-FOUNDATION.md).
