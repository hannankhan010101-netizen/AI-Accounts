# P40 — Batch role clone, reinvite UI, audit doc links (implemented)

Builds on [P39-FOUNDATION.md](./P39-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P40.1 | **Batch role clone** | Roles list checkboxes → `POST /roles/clone-batch` |
| P40.2 | **Reinvite UI** | `/settings/users?reinviteUserId=` + reinvite form |
| P40.3 | **Audit document links** | Extended `auditNavigationHref()` for sales/purchases |

## Batch clone

Select roles on `/settings/roles`, optional name suffix (default ` (copy)`), **Clone selected** calls existing batch clone API (max 50 roles).

## Reinvite

Revoked users are not in the member list. **Reinvite user** opens a form (user ID + role) using `POST /users/{id}/reinvite`.

Audit links for `USER_MEMBERSHIP_REVOKE` / `USER_REINVITE` open `/settings/users?reinviteUserId={transactionId}` with the form pre-filled.

## Audit navigation (documents)

View links when `transactionId` is present (or list routes when not):

| Pattern | Target |
|---------|--------|
| Sales invoice types | `/sales/invoices/{id}` |
| Sales receipt | `/sales/receipts/{id}` |
| Sales order / quotation | `/sales/orders/{id}`, `/sales/quotations/{id}` |
| Supplier bill | `/purchases/bills/{id}` |
| Purchase order | `/purchases/orders/{id}` |
| GRN / delivery / bank / journals | Module list pages |

`GRN_VOID` and similar list-only events link to `/purchases/grn` without a detail id.

## Next (P41)

See [P41-FOUNDATION.md](./P41-FOUNDATION.md).
