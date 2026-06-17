# P29 — Resend invite, welcome email, role export & batch clone (implemented)

Builds on [P28-FOUNDATION.md](./P28-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P29.1 | **Resend invite** | `POST /users/{user_id}/resend-invite` |
| P29.2 | **Welcome email** | Sent when a verified user is invited to another company |
| P29.3 | **Role export** | `GET /roles/export` |
| P29.4 | **Batch role clone** | `POST /roles/clone-batch` |

## Resend invite

```http
POST /users/{user_id}/resend-invite
```

Requires `settings.users.invite`. Response:

```json
{
  "result": {
    "emailType": "setup",
    "emailSent": true
  }
}
```

- `emailType: "setup"` — unverified user; new `user_invite` OTP + set-password link.
- `emailType: "welcome"` — verified user; sign-in link only.

## Welcome on invite

`POST /users/invite` now sends a welcome email (no OTP) when linking an **existing verified** account. New or unverified users still receive the set-password invite mail.

## Role export

```http
GET /roles/export
```

Financial module list read. Returns `{ exportedAt, roles: [{ id, name, permissions }] }`.

## Batch clone

```http
POST /roles/clone-batch
{
  "roleIds": ["id1", "id2"],
  "nameSuffix": " (Copy)"
}
```

Requires `settings.roles.manage`. Clones each role; optional `?strict=true` rejects the batch if any source role has unknown permission codes.

Static routes `/roles/export` and `/roles/clone-batch` are registered **before** `/roles/{role_id}`.

## Next (P30)

See [P30-FOUNDATION.md](./P30-FOUNDATION.md).
