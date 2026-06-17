# P57 — Sales receipt workflow, learning settings, completion toast

## Scope

| Item | Detail |
|------|--------|
| Tour | `workflow.sales-receipt` — `/sales/receipts` → `/sales/receipts/new` |
| Anchors | `sales-receipts-new`, `sr-new-header`, `sr-new-alloc`, `sr-new-summary`, `sr-new-save` |
| UI | `TourCompletionToast`, `/settings/learning` |
| API | `GET /me/onboarding?attemptDigest=true` — optional auto digest on load |

## Frontend

- `Frontend/src/config/tours/workflow.sales-receipt.ts`
- Registry, `route-tours.ts`, `feature-hints.ts`, command palette
- `Frontend/src/app/(app)/settings/learning/page.tsx`
- `Frontend/src/components/tour/tour-completion-toast.tsx`

## Backend

- `onboarding_digest_service.digest_sent_today` / `digest_is_due`
- `get_my_onboarding` — when digest due and mail configured, sends and updates `preferences.lastDigestSentAt`
- `onboarding_suggestion_service` route hints for `/sales/receipts` and `/sales/receipts/new`
- LLM schema includes `workflow.sales-receipt`

## Tests

```bash
cd Backend && PYTHONPATH=src SKIP_PRISMA=1 pytest src/tests/test_p57_onboarding.py -q
```
