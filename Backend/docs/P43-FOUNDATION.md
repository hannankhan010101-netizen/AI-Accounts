# P43 — Bank transfer detail, clone-by-name, user log presets (implemented)

Builds on [P42-FOUNDATION.md](./P42-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P43.1 | **Bank transfer detail** | `GET /bank-transfers/{id}` + `/bank/transfers/{id}` |
| P43.2 | **Clone by role name** | Export JSON without ids resolves `name` → table role |
| P43.3 | **User log presets + CSV** | Quick filters + `typeContains` query; export uses active filters |

## Bank transfer detail

```http
GET /bank-transfers/{transfer_id}
```

Frontend detail at `/bank/transfers/{id}`; list vouchers link through. Audit **View** for `BANK_TRANSFER` + `transactionId` → `/bank/transfers/{id}`.

## Clone by role name

**Clone from export JSON** accepts the standard export shape `{ roles: [{ id, name, permissions }] }`:

- Rows with `id` clone by id (same as P42).
- Rows with only `name` match roles on the current table (case-insensitive).
- Mixed files use id when present, otherwise name.

Selection intersection rules are unchanged from P42.

## User log presets

Preset chips on **User Log**:

- **Last 7 days**
- **RBAC (30 days)**
- **Bank (30 days)** — `GET /audit-log?typeContains=BANK`
- **Sign-in (30 days)** — `transactionType=LOGIN`

**Export CSV (filtered)** downloads CSV for the applied filters (including presets).

## Next (P44)

See [P44-FOUNDATION.md](./P44-FOUNDATION.md) (implemented).
