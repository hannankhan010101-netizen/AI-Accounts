# P42 — Bank payment detail, export clone, reinvite by email (implemented)



Builds on [P41-FOUNDATION.md](./P41-FOUNDATION.md).



## Shipped



| ID | Capability | API / code |

|----|------------|------------|

| P42.1 | **Bank payment detail** | `GET /bank-payments/{id}` + `/bank/payments/{id}` |

| P42.2 | **Clone from export JSON** | Parse export `{ roles: [{ id }] }`, intersect with selection or table |

| P42.3 | **Reinvite by email** | `POST /users/reinvite` `{ email, roleId }` — server resolves user id |



## Bank payment detail



```http

GET /bank-payments/{payment_id}

```



Frontend detail at `/bank/payments/{id}`; list vouchers link through. Audit **View** for `BANK_PAYMENT` + `transactionId` → `/bank/payments/{id}`.



## Clone from export JSON



On **Roles**, **Clone from export JSON** reads a prior **Export JSON** file, extracts role `id` values, then:



- If rows are selected: clone only ids in **both** the file and the selection.

- Otherwise: clone only ids that exist on the current roles table.



Uses the same `POST /roles/clone-batch` endpoint as **Clone selected**.



## Reinvite by email



```http

POST /users/reinvite

{ "email": "user@example.com", "roleId": "..." }

```



Resolves the platform user by email, then runs the same membership reinvite + invite email flow as `POST /users/{user_id}/reinvite`.



The Users reinvite form submits email + role only (optional **Verify** still calls `GET /users/lookup`). Deep links: `?reinviteEmail=` or `?reinviteUserId=` (prefills email via user list).



## Next (P43)

See [P43-FOUNDATION.md](./P43-FOUNDATION.md) (implemented).


