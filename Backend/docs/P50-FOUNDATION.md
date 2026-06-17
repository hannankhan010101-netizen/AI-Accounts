# P50 — Release feed & onboarding insights (implemented)

Builds on [P49-FOUNDATION.md](./P49-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P50.1 | **Release catalog** | `app/constants/onboarding_releases.py` |
| P50.2 | **Feed in GET me** | `releases[]` on `GET /me/onboarding` (permission-filtered) |
| P50.3 | **Company insights** | `GET /onboarding/insights` (`settings.users.invite`) |
| P50.4 | **Release tours** | `release.invoice-void`, `release.bank-recon` (frontend) |
| P50.5 | **What's New UI** | Unread badges, dismiss, tour CTAs |
| P50.6 | **Admin page** | `/settings/learning-insights` |

## Release item shape

```json
{
  "id": "2026-05-invoice-void",
  "version": "1",
  "title": "Void invoices with replacement",
  "summary": "...",
  "publishedAt": "2026-05-22",
  "tourId": "release.invoice-void",
  "href": "/sales/invoices"
}
```

Unread until dismissed (`release.{id}` in `dismissedHints`) or linked tour completed at version.

## Insights response

`usersWithActivity`, `totalLearners`, `tourCompletion[]`, `topStepViews[]` from aggregated `eventLog` payloads.
