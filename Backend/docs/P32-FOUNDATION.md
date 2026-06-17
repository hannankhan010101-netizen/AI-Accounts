# P32 — Role file import, audit CSV, revoke / deactivate (implemented)

Builds on [P31-FOUNDATION.md](./P31-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P32.1 | **Role import upload** | `POST /roles/import/upload` (`.json` / `.csv`) |
| P32.2 | **Audit CSV export** | `GET /audit-log/export` |
| P32.3 | **Revoke membership** | `DELETE /users/{user_id}/membership` |
| P32.4 | **Deactivate user** | `POST /users/{user_id}/deactivate` |

## Role import upload

```http
POST /roles/import/upload
Content-Type: multipart/form-data
file: roles.json | roles.csv
```

Query params:

| Param | Default | Meaning |
|-------|---------|---------|
| `skipExisting` | `true` | Skip roles whose name already exists |
| `dryRun` | `false` | Preview only (same shape as `/roles/import/preview`) |
| `strict` | `false` | Reject when unknown permission codes |

**JSON:** `{ "roles": [{ "name": "...", "permissions": [] }] }` or a top-level array.

**CSV:** header `name,permissions` — permissions comma-, pipe-, or semicolon-separated (or JSON array string).

Writes `ROLE_IMPORT` audit on successful import.

## Audit CSV export

```http
GET /audit-log/export
```

Same filters as `GET /audit-log` (`user_id`, `date_from`, `date_to`, `transactionType`, `rbacOnly`). Returns up to 5000 rows as `audit-log.csv`.

## Revoke membership

```http
DELETE /users/{user_id}/membership
```

Requires `settings.users.invite`. Removes the company membership row. Cannot revoke yourself or the last **Administrator**.

Audit: `USER_MEMBERSHIP_REVOKE`.

## Deactivate user

```http
POST /users/{user_id}/deactivate
```

Requires `settings.users.invite`. Sets `User.isActive = false` (blocks login on all companies). User must be a member of this company. Cannot deactivate yourself.

Audit: `USER_DEACTIVATE`.

## Next (P33)

See [P33-FOUNDATION.md](./P33-FOUNDATION.md).
