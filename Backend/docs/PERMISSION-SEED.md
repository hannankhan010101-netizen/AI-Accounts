# Permission seed — bootstrap roles and recommended codes

How permissions are seeded for new companies and which codes gates use in the API.

## Company bootstrap (phase 1)

On company create, `CompanyBootstrapRepository.create_phase1_defaults` inserts:

| Artifact | Default |
|----------|---------|
| Role **Administrator** | `permissions: ["*"]` |
| Smart settings | `{}` |
| Lock date / taxes / business info | empty shells |

The founding user receives the Administrator role via `assign_admin_role`.

Users with `*` pass every `require_permission(...)` check.

## Module access vs permissions

`require_module_access("sales")` requires:

1. Module entitlement enabled for the company (subscription / `module-entitlements`).
2. At least one permission from [module_permission_matrix.py](../src/app/constants/module_permission_matrix.py) for that module.

Example: **sales** accepts `sales.invoices.create`, `sales.invoices.approve`, or `sales.*`.

## Operator / platform permissions

| Code | Used on |
|------|---------|
| `settings.platform.process` | `PUT /module-entitlements`, outbox, ClickHouse admin |
| `settings.journals.create` | Manual journals (financial module) |
| `settings.journals.reverse` | Journal reverse |

## Document permissions (representative)

| Code | Typical route |
|------|----------------|
| `sales.invoices.create` | `POST /sales-invoices` |
| `sales.invoices.approve` | Approve / goods issue |
| `purchases.bills.create` | `POST /supplier-bills` |
| `purchases.bills.approve` | Approve supplier bill |
| `bank.payments.create` | Bank payment / receipt |
| `bank.reconciliation.create` | Start reconciliation |
| `inventory.adjustments.create` | Stock adjustment |

## Recommended additional roles (not auto-seeded)

Create via Users & Roles UI or API when ready:

| Role | Suggested permissions |
|------|----------------------|
| **Sales clerk** | `sales.invoices.create`, `sales.*` (subset) |
| **Purchases clerk** | `purchases.bills.create`, `purchases.*` |
| **Accountant** | `settings.journals.create`, `settings.journals.reverse`, `reports.*`, `financial` module |
| **Warehouse** | `inventory.*` |
| **Read-only** | `sales.read`, `purchases.read`, `inventory.read`, `reports.read`, `settings.users.read` (see [P25-FOUNDATION.md](./P25-FOUNDATION.md)) |
| **Role manager** | `settings.roles.manage` |
| **User admin** | `settings.users.invite`, `settings.users.read` |

## Wildcards

- `*` — all permissions (Administrator bootstrap only).
- `sales.*` — any permission starting with `sales.`.

Matching logic: [permission_service.py](../src/app/services/permission_service.py) and [module_access_service.py](../src/app/services/module_access_service.py).

## Related docs

- [PLATFORM-WEBHOOK-POLICY.md](./PLATFORM-WEBHOOK-POLICY.md) — webhooks without RBAC
- [P12-FOUNDATION.md](./P12-FOUNDATION.md) — module entitlement matrix
