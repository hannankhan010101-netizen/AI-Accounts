# P31 — Welcome template PUT, import preview, RBAC audit filter (implemented)

Builds on [P30-FOUNDATION.md](./P30-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P31.1 | **Welcome template PUT** | `PUT /settings/welcome-email-template` |
| P31.2 | **Import preview** | `POST /roles/import/preview` dry-run |
| P31.3 | **RBAC audit filter** | `GET /audit-log?rbacOnly=true` and `?transactionType=...` |

## Welcome template

```http
PUT /settings/welcome-email-template
{
  "subject": "Welcome to {companyName}",
  "introText": "...",
  "introHtml": "..."
}
```

Same body shape as invite template. Requires `settings.users.invite`. Placeholders: `{companyName}`, `{loginUrl}`.

## Import preview

```http
POST /roles/import/preview
```

Same body as `POST /roles/import`. Returns:

```json
{
  "result": {
    "wouldCreate": [{ "name": "...", "permissions": [] }],
    "wouldSkip": [{ "name": "...", "reason": "exists" }],
    "permissionWarnings": [{ "name": "...", "unknownPermissions": [] }]
  }
}
```

No database writes. Financial list read. Optional `?strict=true` rejects unknown permission codes.

## Audit log filter

```http
GET /audit-log/rbac-types
```

Lists: `USER_INVITE`, `USER_INVITE_RESEND`, `ROLE_CLONE`, `ROLE_CLONE_BATCH`, `ROLE_IMPORT`.

```http
GET /audit-log?rbacOnly=true
GET /audit-log?transactionType=USER_INVITE
```

Combine with existing `user_id`, `date_from`, `date_to` query params.

## Next (P32)

See [P32-FOUNDATION.md](./P32-FOUNDATION.md).
