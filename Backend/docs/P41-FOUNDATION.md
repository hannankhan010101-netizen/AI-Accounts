# P41 — Import toolbar, email lookup, bank receipt detail (implemented)

Builds on [P40-FOUNDATION.md](./P40-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P41.1 | **Import JSON in toolbar** | Roles header **Import JSON** (same upload pipeline) |
| P41.2 | **Reinvite by email** | `GET /users/lookup?email=` + Lookup button |
| P41.3 | **Bank receipt detail** | `GET /bank-receipts/{id}` + `/bank/receipts/{id}` |

## Roles import toolbar

**Import JSON** in the page header accepts `.json` / `.csv` export files (same as the import section below). Supports sync and async thresholds.

## Reinvite email lookup

```http
GET /users/lookup?email=user@example.com
```

Returns `{ userId, email, firstName, lastName, isActive }`. The reinvite form **Lookup** button fills **User ID** from email.

Optional deep link: `/settings/users?reinviteEmail=user@example.com` opens the reinvite panel with email pre-filled.

## Bank receipt detail

```http
GET /bank-receipts/{receipt_id}
```

Frontend detail at `/bank/receipts/{id}`; list vouchers link through. Audit **View** for `BANK_RECEIPT` + `transactionId` → `/bank/receipts/{id}`.

## Next (P42)

See [P42-FOUNDATION.md](./P42-FOUNDATION.md) (implemented).
