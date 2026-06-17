# P36 — Role picker, import job status, permission-gated UI (implemented)



Builds on [P35-FOUNDATION.md](./P35-FOUNDATION.md).



## Shipped



| ID | Capability | API / code |

|----|------------|------------|

| P36.1 | **My permissions** | `GET /permissions/mine` |

| P36.2 | **Per-row role picker** | Users table `Select` → `PATCH /users/{id}/role` |

| P36.3 | **Roles import status** | Roles page upload + job poll + recent jobs list |

| P36.4 | **Permission-gated UI** | Buttons/forms hidden without invite or roles.manage |



## My permissions



```http

GET /permissions/mine

```



Returns `{ permissions: string[] }` from the active company membership role (includes `*` when applicable). Used by the frontend `hasPermission()` helper.



## Users UI



- Role column is a dropdown when `settings.roles.manage` is granted; read-only label otherwise.

- Invite, revoke, deactivate, bulk actions, and checkboxes require the matching permission codes.

- View-only users see a short notice when they lack both invite and role manage.



## Roles UI



- Import section (file upload, sync/async feedback) when `settings.roles.manage`.

- Polls `GET /roles/import/jobs/{id}` for async uploads.

- Shows recent `jobType=roles` rows from `GET /import-jobs`.



## Next (P37)

See [P37-FOUNDATION.md](./P37-FOUNDATION.md).


