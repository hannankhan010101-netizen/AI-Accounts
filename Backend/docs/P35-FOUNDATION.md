# P35 — Bulk user ops, import job audit, Users UI actions (implemented)

Builds on [P34-FOUNDATION.md](./P34-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P35.1 | **Bulk assign role** | `POST /users/bulk-assign-role` |
| P35.2 | **Bulk revoke** | `POST /users/bulk-revoke` |
| P35.3 | **Import job audit** | `ROLE_IMPORT_JOB` when async role import completes |
| P35.4 | **Users UI** | Invite form, row actions, bulk selection |

## Bulk operations

```http
POST /users/bulk-assign-role
{ "userIds": ["..."], "roleId": "..." }
```

Requires `settings.roles.manage`. Returns `{ succeeded, failed, roleId }`. Audit: `USER_BULK_ASSIGN_ROLE`.

```http
POST /users/bulk-revoke
{ "userIds": ["..."] }
```

Requires `settings.users.invite`. Per-user errors collected (self-revoke, last admin, etc.). Audit: `USER_BULK_REVOKE`.

Max **100** user IDs per request.

## Role import job audit

Async role imports store `requestedByUserId` in the job payload. When the outbox worker finishes `jobType=roles`, it appends:

- `transactionType`: `ROLE_IMPORT_JOB`
- `transactionId`: import job id
- `details`: file name + `created=/skipped=/errors=` summary

## Users UI

`/settings/users` now includes:

- **Invite user** form (email, name, role)
- Search and status filters (unchanged)
- Row checkboxes + bulk assign / bulk revoke
- Per-row: assign first role, revoke, deactivate / reactivate

## Next (P36)

See [P36-FOUNDATION.md](./P36-FOUNDATION.md).
