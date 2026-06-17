# P48 — Universal tour server sync (implemented)

Builds on frontend P0 tour scaffold.

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P48.1 | **Tour progress** | `GET/PUT /me/onboarding` |
| P48.2 | **Analytics batch** | `POST /me/onboarding/events` → 204 |
| P48.3 | **Role context** | GET includes `roleName` + `permissions` |
| P48.4 | **Storage** | `user_onboarding_states` JSON payload |

## Progress payload

```json
{
  "tours": { "onboard.core": { "status": "in_progress", "stepIndex": 2, "version": 1 } },
  "maturityScore": 40,
  "dismissedHints": [],
  "lastActiveTourId": "onboard.core"
}
```

Server retains `eventLog` (last 100 analytics events) across PUT.

## Migration

`20260523100000_p48_onboarding`
