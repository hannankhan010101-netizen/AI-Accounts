# P55 — Workflow tours (journal, bank receipt) + email digest

## Workflow tours (frontend)

| Tour | Routes |
|------|--------|
| `workflow.journal` | `/settings/journals`, `/settings/journals/new` |
| `workflow.bank-receipt` | `/bank/receipts`, `/bank/receipts/new` |

Same **navigate** pattern as P54 sales invoice / supplier bill tours.

## Email digest

| Endpoint | Description |
|----------|-------------|
| `POST /me/onboarding/digest-email` | Sends unread What's New items to the current user's email |

Requires Brevo or SMTP configuration (same as invite mail).

Progress field:

```json
"preferences": { "emailDigestEnabled": true }
```

Included on `GET/PUT /me/onboarding`. Compass menu: opt-in checkbox + **Email N update(s)** when unread items exist.

## Tests

`Backend/src/tests/test_p55_onboarding.py` (`PYTHONPATH=src`, `SKIP_PRISMA=1`)
