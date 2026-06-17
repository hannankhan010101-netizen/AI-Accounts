# P39 — User deep link, role export/preview, email preview (implemented)

Builds on [P38-FOUNDATION.md](./P38-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P39.1 | **User deep link** | `GET /users?userId=` + `/settings/users?userId=` |
| P39.2 | **Role export / import preview** | Roles page Export JSON + Preview import (dry run) |
| P39.3 | **Email preview** | `POST /settings/invite-email-template/preview` |

## User filter from audit

```http
GET /users?userId=clxxx
```

Audit **View** links for `USER_*` events use `/settings/users?userId={transactionId}`. The list filters to that member and highlights the row.

## Roles list export / preview

- **Export JSON** — `GET /roles/export` downloaded from the roles page header.
- **Preview import** — `POST /roles/import/upload?dry_run=true` shows `wouldCreate` / `wouldSkip` before upload.

## Invite template preview

```http
POST /settings/invite-email-template/preview
{ "kind": "invite"|"welcome", "subject", "introText", "introHtml" }
```

Renders the draft fields with sample placeholder values (not yet saved to Smart Settings).

## Next (P40)

See [P40-FOUNDATION.md](./P40-FOUNDATION.md).
