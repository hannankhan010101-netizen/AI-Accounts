# P37 — Role editor, resend invite, import audit links (implemented)

Builds on [P36-FOUNDATION.md](./P36-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P37.1 | **Role rights-tree editor** | `/settings/roles/new`, `/settings/roles/{id}` |
| P37.2 | **Resend invite** | Users row → `POST /users/{id}/resend-invite` |
| P37.3 | **Import job → audit log** | `transactionId` filter + View log links |

## Role editor

- Permission catalog checkboxes grouped by module (`GET /permissions/catalog`).
- Create: `POST /roles` with optional `?strict=true`.
- Edit: `PUT /roles/{id}`, delete via `DELETE /roles/{id}`.
- Full access (`*`) clears other selections.

## Resend invite

Users with `settings.users.invite` see **Resend email** per row. Sends setup OTP or welcome mail depending on `emailVerified`.

## Audit log deep links

```http
GET /audit-log?transactionType=ROLE_IMPORT_JOB&transactionId={jobId}
```

Export CSV supports the same `transactionId` query param.

Roles import table **View log** links to `/settings/user-log?transactionType=ROLE_IMPORT_JOB&transactionId=…`.

## Next (P38)

See [P38-FOUNDATION.md](./P38-FOUNDATION.md).
