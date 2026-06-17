# P56 — Bank payment workflow, maturity badge, auto digest

## Shipped

| ID | Feature |
|----|---------|
| P56.1 | `workflow.bank-payment` tour (`/bank/payments`, `/bank/payments/new`) |
| P56.2 | **TourMaturityBadge** on dashboard (Starter → Pro by score) |
| P56.3 | **Auto digest** once per day when `emailDigestEnabled` and unread releases exist |
| P56.4 | `lastDigestSentAt` on preferences (set after successful digest email) |

## Auto digest

- Runs after `loadMerged()` in `TourProvider` (client)
- Guarded by `sessionStorage` key per user/company/day **and** server `lastDigestSentAt` same calendar day
- Requires mail configured (Brevo/SMTP)

## Tests

`Backend/src/tests/test_p56_onboarding.py`
