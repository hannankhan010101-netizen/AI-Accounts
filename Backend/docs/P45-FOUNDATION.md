# P45 — Bank payment/receipt audit, saved log presets, names-only import (implemented)

Builds on [P44-FOUNDATION.md](./P44-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P45.1 | **Bank payment / receipt audit** | `BANK_PAYMENT` / `BANK_RECEIPT` on create |
| P45.2 | **Saved user log presets** | `localStorage` named filters on User Log |
| P45.3 | **Names-only role import** | Parser accepts P44 export JSON (`namesOnly` / no ids) |

## Bank payment & receipt audit

After create:

- **Payment** — `transactionType=BANK_PAYMENT`, payment id, voucher/amount/posted
- **Receipt** — `transactionType=BANK_RECEIPT`, receipt id, voucher/amount/posted

Audit **View** links use P41/P42 detail routes.

## Saved user log presets

On **User Log**:

- Enter a name and **Save current filters** (stored in browser `localStorage`)
- Saved presets appear as chips next to built-in presets
- **×** removes a saved preset

Shareable URLs still use **Copy bookmark link** (P44).

## Names-only role import

`parse_role_import_file` accepts:

- `{ "roles": [{ "name", "permissions" }], "namesOnly": true }` (P44 export)
- Standard full export with ids
- CSV with `name` column

Empty role names are rejected with a row index error.

## Next (P46)

See [P46-FOUNDATION.md](./P46-FOUNDATION.md) (implemented).
