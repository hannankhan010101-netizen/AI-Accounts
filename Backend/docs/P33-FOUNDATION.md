# P33 — Reactivate user, async role import, user list pagination (implemented)

Builds on [P32-FOUNDATION.md](./P32-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P33.1 | **Reactivate user** | `POST /users/{user_id}/reactivate` |
| P33.2 | **Async role import** | `POST /roles/import/jobs`, `GET /roles/import/jobs/{id}` |
| P33.3 | **User list pagination** | `GET /users?page=&pageSize=` |

## Reactivate user

```http
POST /users/{user_id}/reactivate
```

Requires `settings.users.invite`. Sets `User.isActive = true`. User must be a company member.

Audit: `USER_REACTIVATE` (included in RBAC audit filter).

## Async role import

For large JSON/CSV files, queue a background job (outbox worker) instead of blocking on `POST /roles/import/upload`.

```http
POST /roles/import/jobs
multipart file + ?skipExisting=true
→ 202 { result: ImportJob }
```

```http
GET /roles/import/jobs/{job_id}
→ job status: pending | processing | completed | failed
```

`jobType` is `roles`. Payload stores parsed rows and `skipExisting`. Handler reuses role-create rules (skips **Administrator**, duplicate names when `skipExisting`).

Poll until `status=completed`; read `resultSummary` (e.g. `created=N skipped=M errors=K`).

## User list pagination

```http
GET /users?page=1&pageSize=25
```

Response:

```json
{
  "result": {
    "items": [ ... ],
    "page": 1,
    "pageSize": 25,
    "total": 42
  }
}
```

`pageSize` max 100. Financial module list read.

## Next (P34)

See [P34-FOUNDATION.md](./P34-FOUNDATION.md).
