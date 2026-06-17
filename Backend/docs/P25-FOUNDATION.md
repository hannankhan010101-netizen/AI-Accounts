# P25 — Role CRUD, read permissions, GRN void audit (implemented)

Builds on [P24-FOUNDATION.md](./P24-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P25.1 | **Role CRUD** | `GET/POST /roles`, `GET/PUT/DELETE /roles/{id}`, `GET /permissions/catalog` |
| P25.2 | **Read permission codes** | `permission_catalog.py` + `require_module_list_read` on key list routes |
| P25.3 | **GRN void audit** | `GRN_VOID` entry in audit log on `POST /goods-receipt-notes/{id}/void` |

## Role API

| Method | Path | Guard |
|--------|------|-------|
| GET | `/permissions/catalog` | JWT tenant |
| GET | `/roles` | `financial` list read |
| GET | `/roles/{id}` | `financial` list read |
| POST | `/roles` | `settings.roles.manage` |
| PUT | `/roles/{id}` | `settings.roles.manage` |
| DELETE | `/roles/{id}` | `settings.roles.manage` |

Administrator role cannot be renamed or deleted. Roles with assigned users cannot be deleted.

## List read permissions

Representative `GET` list routes now require module entitlement **and** a read code (or `*`), e.g.:

- `sales.customers.read`, `sales.invoices.read`, `sales.read`, `sales.*`
- `purchases.suppliers.read`, `purchases.bills.read`, …
- `inventory.products.read`, …
- `settings.users.read`, `reports.read`, … for users/roles/audit log

See `MODULE_LIST_READ_PERMISSIONS` in `permission_catalog.py`.

## GRN void audit

Audit row: `transactionType=GRN_VOID`, `transactionId=note_id`, `details=voucher=…`.

## Next (P26)

See [P26-FOUNDATION.md](./P26-FOUNDATION.md).
