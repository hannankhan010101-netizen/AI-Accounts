# P30 — Role import, invite templates, RBAC audit (implemented)

Builds on [P29-FOUNDATION.md](./P29-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P30.1 | **Role import** | `POST /roles/import` from export-shaped JSON |
| P30.2 | **Invite email templates** | `GET/PUT /settings/invite-email-template` (Smart Settings keys) |
| P30.3 | **RBAC audit** | `USER_INVITE`, `USER_INVITE_RESEND`, `ROLE_CLONE`, `ROLE_CLONE_BATCH`, `ROLE_IMPORT` |

## Role import

```http
POST /roles/import
{
  "roles": [
    { "name": "Sales clerk", "permissions": ["sales.read", "sales.invoices.create"] }
  ],
  "skipExisting": true
}
```

Requires `settings.roles.manage`. Returns `{ created: [...], skipped: [...] }`. Skips reserved name **Administrator**. Optional `?strict=true` rejects unknown permission codes before any insert.

Import body matches `GET /roles/export` role entries (name + permissions; `id` is ignored).

## Invite email templates

Stored under Smart Settings payload keys:

- `inviteEmailTemplate` — `{ subject, introText, introHtml }`
- `welcomeEmailTemplate` — same shape for welcome mail

Placeholders:

| Template | Tokens |
|----------|--------|
| Invite | `{companyName}`, `{resetLink}`, `{code}`, `{ttlMinutes}` |
| Welcome | `{companyName}`, `{loginUrl}` |

```http
GET /settings/invite-email-template
PUT /settings/invite-email-template
{ "subject": "Join {companyName}", "introText": "...", "introHtml": "..." }
```

`PUT` requires `settings.users.invite`. `GET` uses financial list read.

## Audit log types

| Type | When |
|------|------|
| `USER_INVITE` | After successful `POST /users/invite` |
| `USER_INVITE_RESEND` | After `POST /users/{id}/resend-invite` |
| `ROLE_CLONE` | After `POST /roles/{id}/clone` |
| `ROLE_CLONE_BATCH` | After `POST /roles/clone-batch` |
| `ROLE_IMPORT` | After `POST /roles/import` |

Visible in Settings → User Log (`GET /audit-log`).

## Next (P31)

See [P31-FOUNDATION.md](./P31-FOUNDATION.md).
