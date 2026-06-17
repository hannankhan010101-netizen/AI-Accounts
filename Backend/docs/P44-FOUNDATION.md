# P44 — Transfer audit, log bookmarks, names-only export (implemented)

Builds on [P43-FOUNDATION.md](./P43-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P44.1 | **Bank transfer audit** | `BANK_TRANSFER` row on `POST /bank-transfers` |
| P44.2 | **User log bookmark** | Copy bookmark link + shareable URL from current filters |
| P44.3 | **Names-only role export** | `GET /roles/export?stripIds=true` + **Names only** checkbox |

## Bank transfer audit

After a transfer is created, the user log records:

- `transactionType`: `BANK_TRANSFER`
- `transactionId`: transfer id
- `details`: voucher, amount, posted flag

Audit **View** links to `/bank/transfers/{id}` (P43).

## User log bookmark

- **Apply** updates the browser URL with the active filters (unchanged).
- **Copy bookmark link** copies the full URL and navigates to it so the query string can be shared or saved.
- The current bookmark path is shown under the filter actions.

## Names-only role export

```http
GET /roles/export?stripIds=true
```

Returns `{ roles: [{ name, permissions }], namesOnly: true }` for use with **Clone from export JSON** (name resolution — P43).

On **Roles**, enable **Names only** before **Export JSON** to download a file without role ids.

## Next (P45)

See [P45-FOUNDATION.md](./P45-FOUNDATION.md) (implemented).
