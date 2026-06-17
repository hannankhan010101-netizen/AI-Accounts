# P47 — Preset import, reconciliation complete, bank recon filter (implemented)

Builds on [P46-FOUNDATION.md](./P46-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P47.1 | **Import saved presets** | User Log **Import presets JSON** (merge into `localStorage`) |
| P47.2 | **Complete reconciliation** | Detail page **Complete reconciliation** → `POST .../complete` |
| P47.3 | **Bank recon preset chip** | **Reconciliations (30 days)** filters `BANK_RECONCILIATION` |

## Import saved presets

Accepts `{ version: 1, presets: [...] }` or a raw array (same shape as export). Imported presets are merged with existing saved presets (new ids assigned to avoid collisions).

## Complete reconciliation

On `/bank/reconciliation/{id}`, when status is `open`, **Complete reconciliation** calls:

```http
POST /bank-reconciliations/{reconciliation_id}/complete
```

Refreshes detail and list; audit row recorded on complete (P46).

## Bank module preset

Built-in chip **Reconciliations (30 days)** sets `transactionType=BANK_RECONCILIATION` with a 30-day date window. **Bank (30 days)** still matches all `BANK*` types via `typeContains`.

## Next (P48)

- Reconciliation: toggle cleared items on detail page
- User log: link from preset chip to User Log with filters applied in new tab
- Roles: import presets JSON (mirror user log)
