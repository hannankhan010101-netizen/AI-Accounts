# P5 — PRAL, PayPro, report aliases, lock context, read replica (implemented)

Builds on [P4-FOUNDATION.md](./P4-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P5.1 | **PRAL FBR client** | `FbrService` + `PralClient` — live POST when `FBR_PRAL_ENABLED=1`, else stub / fallback |
| P5.2 | **PayPro payments stub** | `GET/POST /payments/paypro/*` — `PaymentGatewayTransaction` table |
| P5.3 | **Report ID aliases** | `report_aliases.py` → `ReportQueryService.execute` |
| P5.4 | **Extended report handlers** | `034` customer statement, `030` invoice lines, `085`/`087` product sale/purchase |
| P5.5 | **Assembly multi-line GL** | Component credit lines per BOM line on `finish` |
| P5.6 | **Lock date via JWT context** | `tenant_context.set_current_user_id` in `resolve_tenant`; `LockDateService` reads context |
| P5.7 | **Read replica for reports** | `DATABASE_READ_URL` — outbox worker uses read Prisma when configured |

## Migration

```bash
cd Backend
python -m prisma migrate deploy
python -m prisma generate
```

Folder: `prisma/migrations/20260521210000_p5_foundation/`

## Environment

| Variable | Purpose |
|----------|---------|
| `DATABASE_READ_URL` | Optional PostgreSQL read replica for report outbox worker |
| `FBR_PRAL_ENABLED` | `1` / `true` to call PRAL HTTP API |
| `FBR_PRAL_API_URL` | Base URL (POST `{url}/invoices`) |
| `FBR_PRAL_API_KEY` | Bearer token |
| `PAYPRO_ENABLED` | Enable checkout URL generation |
| `PAYPRO_MERCHANT_ID` | Merchant id in stub checkout link |
| `PAYPRO_WEBHOOK_SECRET` | HMAC-style SHA256 for `X-Paypro-Signature` |

## PayPro flow

1. `POST /payments/paypro/initiate` with `customerId`, `amount` → `merchantRef`, optional `checkoutUrl`.
2. Provider calls `POST /payments/paypro/webhook` with `merchantRef`, optional `salesReceiptId`.
3. `GET /payments/paypro/transactions` lists gateway rows.

## Report aliases

Catalog IDs such as `141`, `240` map to implemented handlers (`028`, `029`, etc.). Unmapped IDs return a structured “not implemented” row with `resolvedHandler`.

Dedicated handlers (not aliased away): `030`, `034`, `085`, `087`.

## Next

See [P6-FOUNDATION.md](./P6-FOUNDATION.md).
