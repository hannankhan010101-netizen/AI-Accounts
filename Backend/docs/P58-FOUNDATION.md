# P58 — Supplier payment workflow tour

Builds on [P57-FOUNDATION.md](./P57-FOUNDATION.md) (tour P10).

## Shipped

| Item | Detail |
|------|--------|
| Tour | `workflow.supplier-payment` — `/purchases/payments` → `/purchases/payments/new` |
| Permission | `purchases.bills.create` (same as supplier bill) |
| Anchors | `supplier-payments-new`, `vp-new-header`, `vp-new-alloc`, `vp-new-summary`, `vp-new-save` |
| Hints | After `workflow.supplier-bill` completed |
| AI | Route hints + LLM schema entry |

## Frontend

- `Frontend/src/config/tours/workflow.supplier-payment.ts`
- `purchases/payments/page.tsx`, `purchases/payments/new/page.tsx`

## Tests

```bash
cd Backend && PYTHONPATH=src SKIP_PRISMA=1 pytest src/tests/test_p58_onboarding.py -q
```
