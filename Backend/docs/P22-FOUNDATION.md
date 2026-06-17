# P22 — Settings gates, FBR gates, delivery/GI stock guard (implemented)

Builds on [P21-FOUNDATION.md](./P21-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P22.1 | **Settings / COA gates** | COA mutators, smart-settings, lock-date, taxes-year-end, business-info, custom-field definitions → `financial` |
| P22.2 | **FBR poll/retry gates** | `fbr` module on poll, retry, retry-pending |
| P22.3 | **Delivery vs GI stock guard** | `InventoryStockGuardService` + `skipStockMovement` on delivery create and goods-issue query |
| P22.4 | **Admin mutator gates** | report export, approval policy/request, dashboard layout |

## Stock guard

**GDNSI delivery create** (without `skipStockMovement`):

- Rejects if another non-voided GDNSI delivery exists for the invoice.
- Rejects if a non-voided goods issue exists (use `skipStockMovement=true` for document-only delivery).

**Goods issue create** (without `skipStockMovement` query param):

- Rejects if non-voided GDNSI delivery notes exist (void them first or pass `skipStockMovement=true`).

When `skipStockMovement` is true on delivery, batch quantities are not reduced (`stockSkipped: true`).

## Module gates (P22)

| Route group | Module |
|-------------|--------|
| COA category/section/nominal | financial |
| Smart settings, lock-date, taxes-year-end, business info | financial |
| Custom field definitions | financial |
| Report run export / ClickHouse export | financial |
| Approval policy upsert, approval request create | financial |
| FBR poll, retry, retry-pending | fbr |

## Next (P23)

See [P23-FOUNDATION.md](./P23-FOUNDATION.md) and [PLATFORM-WEBHOOK-POLICY.md](./PLATFORM-WEBHOOK-POLICY.md).
