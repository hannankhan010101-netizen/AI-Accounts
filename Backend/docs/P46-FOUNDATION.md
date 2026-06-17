# P46 — Reconciliation audit, preset export, import hint (implemented)

Builds on [P45-FOUNDATION.md](./P45-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P46.1 | **Reconciliation audit + detail** | `BANK_RECONCILIATION` on start/complete; `/bank/reconciliation/{id}` |
| P46.2 | **Export saved presets** | `audit-log-presets.json` from User Log |
| P46.3 | **Import preview hint** | `namesOnly` in dry-run upload response + UI banner |

## Bank reconciliation audit

- **Start** — `BANK_RECONCILIATION`, session id, status `open`
- **Complete** — same type, status `completed`

Detail at `/bank/reconciliation/{id}`; list links from **Bank reconciliation**. Audit **View** → detail when `transactionId` is set.

## Export saved presets

**Export presets JSON** downloads `{ version: 1, presets: [...] }` from browser `localStorage` (saved named filters from P45).

## Names-only import preview

`POST /roles/import/upload?dryRun=true` includes `namesOnly` and `fileFormat` when the file is a names-only export. The Roles import section shows an amber hint before the preview JSON.

## Next (P47)

See [P47-FOUNDATION.md](./P47-FOUNDATION.md) (implemented).
