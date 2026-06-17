# Platform and webhook route policy

How tenant API routes are protected. Use this when adding integrations or hardening production.

## Auth patterns

| Pattern | When used | Examples |
|---------|-----------|----------|
| **JWT + tenant** | Normal company users | Most `GET`/`POST` document routes |
| **`require_module_access(module)`** | Subscription module + RBAC matrix | Sales invoice create, GRN create |
| **`require_permission(code)`** | Fine-grained operator/admin | `settings.platform.process`, invoice approve |
| **Shared secret header** | Server-to-server webhooks | `X-Billing-Secret`, PayPro/Kuickpay HMAC |
| **Provider signature** | External SaaS | Stripe `Stripe-Signature` |
| **No app auth** | Public callbacks only if secret/signature verified | Payment webhooks |

## Operator / platform routes

Require permission **`settings.platform.process`** (or `*`):

| Method | Path | Purpose |
|--------|------|---------|
| `PUT` | `/module-entitlements` | Replace enabled modules (P23) |
| `POST` | `/platform/process-outbox` | Drain async outbox |
| `POST` | `/platform/clickhouse/ensure-schema` | ClickHouse DDL |
| `POST` | `/platform/clickhouse/sync-recent-runs` | Backfill report runs |

`GET /module-entitlements` remains JWT tenant auth only (read).

## Billing webhooks

| Method | Path | Guard |
|--------|------|-------|
| `POST` | `/billing/webhook` | Optional `X-Billing-Secret` vs `BILLING_WEBHOOK_SECRET` |
| `POST` | `/billing/webhook/stripe` | `STRIPE_WEBHOOK_SECRET` + signature |

No module gate — company resolved from payload/metadata.

## Payment webhooks

| Method | Path | Guard |
|--------|------|-------|
| `POST` | `/payments/paypro/webhook` | PayPro secret + optional IP allowlist |
| `POST` | `/payments/kuickpay/webhook` | Kuickpay secret |

Initiate routes use `require_module_access("payments")`.

## FBR

| Method | Path | Guard |
|--------|------|-------|
| `POST` | `/sales-invoices/{id}/fbr/submit` | `fbr` module |
| `POST` | `/sales-invoices/{id}/fbr/poll` | `fbr` module |
| `POST` | `/sales-invoices/{id}/fbr/retry` | `fbr` module |
| `POST` | `/fbr/retry-pending` | `fbr` module |

## Stock guards (not auth)

Duplicate stock movement is blocked in `InventoryStockGuardService`:

- **GDNSI** / goods issue — see [P22-FOUNDATION.md](./P22-FOUNDATION.md)
- **GRNPO** / **GRNVI** — see [P23-FOUNDATION.md](./P23-FOUNDATION.md)

Use `skipStockMovement` on create when the document is informational only.

## Adding a new webhook

1. Verify signature or shared secret before side effects.
2. Do not rely on `require_module_access` unless the caller is a logged-in user.
3. Rate-limit at the edge (`rate_limit_webhooks_per_minute` in config).
4. Document the route in this file.
