# P28 — Invite email, invite permission, role clone (implemented)

Builds on [P27-FOUNDATION.md](./P27-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P28.1 | **Invite email** | Set-password link + OTP after `POST /users/invite` when account needs credentials |
| P28.2 | **`settings.users.invite`** | Separate from `settings.roles.manage` on invite route |
| P28.3 | **Role clone** | `POST /roles/{role_id}/clone` optional `{ "name": "..." }` |
| P28.4 | **Accept invite** | `POST /auth/accept-invite` (same body as reset-password, `purpose=user_invite`) |

## Invite email

After a successful invite, when the user is new **or** not yet email-verified:

1. A `user_invite` OTP is stored.
2. Email is sent (Brevo or SMTP) with:
   - Link: `{APP_PUBLIC_URL}/reset-password?email=...&invite=1`
   - 6-digit code

Response includes `inviteEmailSent: true|false`.

Verified existing users added to another company do not receive a password email.

## Permissions

| Route | Permission |
|-------|------------|
| `POST /users/invite` | `settings.users.invite` |
| `POST /roles/{id}/clone` | `settings.roles.manage` |

Administrator (`*`) includes both. Seed doc updated in [PERMISSION-SEED.md](./PERMISSION-SEED.md).

## Role clone

```http
POST /roles/{role_id}/clone
{ "name": "Sales clerk copy" }   // optional
```

Copies permission JSON. Name defaults to `{source} (Copy)` with numeric suffix if taken. Supports `?strict=true` like role create.

## Accept invite (auth)

```http
POST /auth/accept-invite
{
  "email": "clerk@example.com",
  "otpCode": "123456",
  "newPassword": "secret123"
}
```

Sets password, marks `emailVerified=true`, clears invite OTP. Frontend reset page uses this when `invite=1` is in the query string.

## Next (P29)

See [P29-FOUNDATION.md](./P29-FOUNDATION.md).
