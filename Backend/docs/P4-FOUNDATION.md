# P4 — Assembly, FX, FBR stub, journal immutability (implemented)

Builds on [P3-FOUNDATION.md](./P3-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P4.1 | **Assembly templates & jobs** | `GET/POST /assembly/templates`, `GET/POST /assembly/jobs`, `POST .../finish` → GL `ASSEMBLY_JOB` |
| P4.2 | **FX revaluation** | `GET/POST /bank/fx-revaluations` — gain/loss journal `FX_REVALUATION` |
| P4.3 | **FBR submit stub** | `GET/POST /sales-invoices/{id}/fbr/submit` — records submission, no live PRAL |
| P4.4 | **Journal immutability** | `JournalRepository.assert_mutable` / `update_line` blocks posted edits |
| P4.5 | **Per-user lock date** | `PUT /lock-date/users/{userId}`; `assert_not_locked(..., user_id=)` on approve routes |
| P4.6 | **Financial report runs** | Report IDs `TB`, `PNL`, `BS` in outbox worker |
| P4.7 | **PDF export** | `POST .../reports/runs/{id}/export` with `format: pdf` → base64 PDF in `content` |

## Migration

```bash
cd Backend
.venv\Scripts\python.exe -m pip install fpdf2
python -m prisma migrate deploy
python -m prisma generate
```

Folder: `prisma/migrations/20260521200000_p4_foundation/`

## Smart Settings (additional defaults)

- `fxGainNominalCode`, `fxLossNominalCode` — required for FX revaluation posting
- Assembly finish reuses `inventoryNominalCode` + `stockAdjustmentNominalCode`

## Assembly flow

1. `POST /assembly/templates` — BOM (component lines + finished product code).
2. `POST /assembly/jobs` — instantiates job from template × quantity.
3. `POST /assembly/jobs/{id}/finish` — posts capitalization journal, status `finished`.

## FX revaluation

```json
POST /bank/fx-revaluations
{
  "bankAccountId": "...",
  "revaluationDate": "2026-05-21T00:00:00Z",
  "foreignBalance": "1000",
  "exchangeRate": "280",
  "bookBalanceBase": "275000"
}
```

`gainLossAmount = foreignBalance × exchangeRate − bookBalanceBase`.

## FBR (stub)

`POST /sales-invoices/{id}/fbr/submit` on a **posted** invoice returns `fbrReference` like `FBR-STUB-…`. Replace `FbrService` with PRAL HTTP client for production.

## Per-user lock date

Users with an **earlier** `extendedLockDate` than the company global lock may post in the period between the two dates. Pass JWT `user_id` into lock checks (wired on approve and assembly/FX routes; extend remaining routes as needed).

## Next

See [P5-FOUNDATION.md](./P5-FOUNDATION.md). Further work: [P6 in P5 doc](./P5-FOUNDATION.md#next-p6).
