# P38 — Clone role, invite templates UI, audit navigation (implemented)

Builds on [P37-FOUNDATION.md](./P37-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P38.1 | **Clone from editor** | Edit role → `POST /roles/{id}/clone` |
| P38.2 | **Invite templates UI** | `/settings/invite-templates` |
| P38.3 | **Audit row navigation** | User Log **View** column → Users / Roles / GRN |

## Clone role

On `/settings/roles/{id}`, **Clone role** creates `{name} (copy)` via existing clone endpoint and opens the new role editor.

## Invite templates

- `GET /settings/invite-email-template` — load invite + welcome copy and defaults.
- `PUT /settings/invite-email-template` / `PUT /settings/welcome-email-template` — save (requires `settings.users.invite`).
- Settings menu and Users page link when permitted.

## Audit navigation

`auditNavigationHref()` maps known `transactionType` values:

| Type prefix / code | Target |
|--------------------|--------|
| `USER_*` | `/settings/users` |
| `ROLE_CLONE` + id | `/settings/roles/{id}` |
| `ROLE_*` | `/settings/roles` |
| `GRN_VOID` | `/purchases/grn` |

## Next (P39)

See [P39-FOUNDATION.md](./P39-FOUNDATION.md).
