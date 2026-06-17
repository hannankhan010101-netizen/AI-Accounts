# P52 — LLM assistant + platform release CMS

## Scope

| Item | Detail |
|------|--------|
| **Platform releases** | `platform_onboarding_releases` table; CRUD under `settings.platform.process` |
| **Merge order** | Platform DB → Python `RELEASE_CATALOG` → tenant CMS (tenant wins on key) |
| **LLM suggestions** | `GET /me/onboarding/suggestions` returns `engine`: `rules` \| `llm` |
| **Assistant chat** | `POST /me/onboarding/assistant` — short reply when LLM configured |

## Config (`.env`)

```env
ONBOARDING_LLM_ENABLED=true
ONBOARDING_LLM_API_KEY=sk-...
ONBOARDING_LLM_BASE_URL=https://api.openai.com/v1
ONBOARDING_LLM_MODEL=gpt-4o-mini
```

When disabled or no API key, suggestions and chat use rule-based fallbacks.

## Migration

`Backend/prisma/migrations/20260523120000_p52_platform_releases`

## Frontend

- `/settings/platform-releases` — operator CMS
- `TourAiPanel` — engine badge, optional question box

## Tests

`Backend/src/tests/test_p52_onboarding.py` (run with `SKIP_PRISMA=1`)
