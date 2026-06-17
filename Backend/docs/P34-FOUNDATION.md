# P34 — Auto async import, reinvite, user search (implemented)

Builds on [P33-FOUNDATION.md](./P33-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P34.1 | **Auto async import** | `POST /roles/import/upload` queues job when row count ≥ 50 |
| P34.2 | **Reinvite after revoke** | `POST /users/{user_id}/reinvite` |
| P34.3 | **User list filters** | `GET /users?q=&isActive=&roleId=` |

## Auto async import

`ROLE_IMPORT_ASYNC_THRESHOLD` = **50** ([role_import.py](../src/app/constants/role_import.py)).

When `POST /roles/import/upload` parses ≥ 50 roles (and not `dryRun`):

- Returns **202** with `{ mode: "async", job, rowCount, threshold }`
- Same outbox pipeline as `POST /roles/import/jobs`

Force synchronous import: `?forceSync=true`.

Small files still return **200** with `{ mode: "sync", created, skipped }`.

## Reinvite

```http
POST /users/{user_id}/reinvite
{ "roleId": "clxxx..." }
```

For users who were **revoked** from the company (no membership row) but still exist. Does not create a new user record. Sends welcome/setup email when appropriate.

Requires `settings.users.invite`. Audit: `USER_REINVITE`.

## User list search / filter

```http
GET /users?page=1&pageSize=25&q=jane&isActive=true&roleId=clxxx
```

| Param | Description |
|-------|-------------|
| `q` | Case-insensitive match on email, first name, or last name |
| `isActive` | Filter by `User.isActive` |
| `roleId` | Filter by assigned role |

## Next (P35)

See [P35-FOUNDATION.md](./P35-FOUNDATION.md).
