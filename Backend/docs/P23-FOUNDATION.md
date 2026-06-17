# P23 — GRN guard, operator entitlements, platform policy (implemented)

Builds on [P22-FOUNDATION.md](./P22-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P23.1 | **GRN duplicate guard** | `assert_grn_receipt_allowed` for `GRNPO` / `GRNVI` + `skipStockMovement` on GRN create |
| P23.2 | **Operator module entitlements** | `PUT /module-entitlements` requires `settings.platform.process` |
| P23.3 | **Platform route policy** | [PLATFORM-WEBHOOK-POLICY.md](./PLATFORM-WEBHOOK-POLICY.md) |
| P23.4 | **ClickHouse platform gates** | ensure-schema + sync-recent-runs → `settings.platform.process` |

## GRN stock guard

**GRN create** (without `skipStockMovement`):

- **GRNPO:** at most one non-voided note per `sourceId` (purchase order).
- **GRNVI:** at most one non-voided note per `sourceId` (supplier bill).

When `skipStockMovement` is true, batch quantities are not increased (`stockSkipped: true`).

## Operator entitlements

Replacing module entitlements is restricted to users with **`settings.platform.process`** (same permission as outbox / ClickHouse admin). Listing entitlements is unchanged for normal tenant users.

## Next (P24)

See [P24-FOUNDATION.md](./P24-FOUNDATION.md) and [PERMISSION-SEED.md](./PERMISSION-SEED.md).
