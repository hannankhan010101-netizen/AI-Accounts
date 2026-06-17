# P51 — AI assistant + release CMS (implemented)

Builds on [P50-FOUNDATION.md](./P50-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P51.1 | **Release CMS table** | `onboarding_release_items` |
| P51.2 | **CRUD** | `GET/POST /onboarding/releases`, `PUT/DELETE …/{id}` |
| P51.3 | **Merged feed** | Tenant rows override platform catalog by `releaseKey` |
| P51.4 | **AI suggestions** | `GET /me/onboarding/suggestions?pathname=` |
| P51.5 | **Frontend assistant** | `TourAiPanel` + compass menu |
| P51.6 | **Hint ranking** | `hint-ranker.ts` (route + progress boosts) |
| P51.7 | **Admin UI** | `/settings/onboarding-releases` |

## Migration

`20260523110000_p51_release_cms`

## Suggestions

Rule-based scores today; response shape ready for LLM swap later.
