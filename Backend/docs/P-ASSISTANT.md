# Enterprise AI Assistant (Groq)

Server-side AI copilot for Fast Accounts ERP. Groq API keys **must** live only on the backend.

## Environment variables

Set in `Backend/.env` (see `.env.example`):

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Groq API key (required for AI) |
| `GROQ_ENABLED` | `true` / `false` (default true) |
| `GROQ_MODEL` | e.g. `llama-3.3-70b-versatile` |
| `GROQ_MAX_TOKENS` | Max completion tokens |
| `ASSISTANT_RATE_LIMIT_PER_MINUTE` | Per-user limit (default 30) |
| `ASSISTANT_MAX_MESSAGE_CHARS` | User message cap |
| `ASSISTANT_MEMORY_TURNS` | History turns loaded per thread |

## Database

```bash
cd Backend
prisma migrate dev --name assistant_threads
```

Models: `assistant_threads`, `assistant_messages`.

## API (tenant-scoped, JWT)

Base: `/api/v1/companies/{company_id}`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/me/assistant/chat/stream` | SSE: `thread`, `token`, `tool_call`, `done`, `error` |
| POST | `/me/assistant/chat/tool-result` | Resume after client tool |
| GET | `/me/assistant/threads/{id}/messages` | Thread history |
| DELETE | `/me/assistant/threads/{id}` | Delete thread |
| GET | `/me/assistant/suggestions?pathname=` | Quick actions (rules + optional LLM) |

Legacy onboarding endpoints remain:

- `POST /me/onboarding/assistant` — uses Groq when configured

## Tools

**Client** (browser executes): `navigate`, `openModal`, `highlightElement`, `startTour`, `explainScreen`

**Server** (RBAC): `helpUser`, `searchInvoices`, `createInvoice`, `fetchReports`, `searchInventory`, `explainAuditEntry`

## Security

- No `NEXT_PUBLIC_*` Groq keys
- Rate limit per `user_id`
- Prompt sanitization and length caps
- Audit types: `assistant.query`, `assistant.tool.{name}`
- Rotate any key exposed in chat or tickets

## Frontend

- Floating copilot FAB + drawer (`CopilotRoot`)
- Shortcut: **Ctrl/Cmd+.**
- Command palette: AI commands (`ai://open`, etc.)
- Learning assistant opens the same copilot in onboarding mode
