# P27 — Known codes, user invite, strict role validation (implemented)

Builds on [P26-FOUNDATION.md](./P26-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P27.1 | **Known permission codes** | `GET /permissions/known-codes` → sorted flat list |
| P27.2 | **Invite user + role** | `POST /users/invite` — create user if new, add membership with `roleId` |
| P27.3 | **Strict role save** | `?strict=true` on `POST /roles` and `PUT /roles/{id}` rejects unknown codes |

## Known codes

```http
GET /permissions/known-codes
```

Returns `{ "result": ["*", "sales.read", ...] }` for autocomplete. JWT tenant only.

## Invite user

```http
POST /users/invite
{
  "email": "clerk@example.com",
  "firstName": "Jane",
  "lastName": "Doe",
  "roleId": "clxxx..."
}
```

Requires `settings.users.invite` (P28; was `settings.roles.manage` in P27).

- Normalizes email to lowercase.
- Creates a user with a random password and `emailVerified=false` when the email is new (`userCreated: true` in the result).
- Fails with 400 if the user is already a member of this company.
- Existing users in other companies are linked without resetting their password.

Invitees should use **Forgot password** (or a future invite-email flow) to set credentials.

## Strict validation

Non-strict (default): role save succeeds; response includes `unknownPermissions` / `permissionWarnings`.

```http
POST /roles?strict=true
PUT /roles/{id}?strict=true
```

When `strict=true` and any permission code is unknown, returns **400** before persisting.

## Next (P28)

See [P28-FOUNDATION.md](./P28-FOUNDATION.md).
