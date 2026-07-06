# Fast Accounts — Backend

FastAPI + **Prisma Client Python** + PostgreSQL, structured per [`.cursorrules_backend`](.cursorrules_backend).

## Prerequisites

- Python 3.11+
- PostgreSQL (local or Docker)
- [pnpm](https://pnpm.io/) is used at monorepo level where applicable; this package uses **pip** / **pyproject.toml**.

## Setup

```powershell
cd Backend
python -m venv .venv
.\.venv\Scripts\pip install -e ".[dev]"
copy .env.example .env
# Edit .env: set DATABASE_URL (Supabase session pooler URL) and JWT_SECRET_KEY
$env:PYTHONPATH = "src"
.\.venv\Scripts\python -m prisma migrate deploy
.\.venv\Scripts\python -m prisma generate
```

### Supabase `DATABASE_URL`

Use the **Session pooler** connection string from the Supabase dashboard (port **5432**, user `postgres.<project-ref>`). URL-encode special characters in the password (e.g. `@` → `%40`). Direct `db.<ref>.supabase.co` is IPv6-only and often fails on Windows.

Example:

```env
DATABASE_URL="postgresql://postgres.<project-ref>:<url-encoded-password>@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres?schema=public&sslmode=require"
```

Regenerate the Prisma client after schema changes:

```powershell
.\.venv\Scripts\python -m prisma generate
```

The client is generated under `src/prisma_generated/` (see `generator output` in `prisma/schema.prisma`).

### Migrations

Use **`python -m prisma`** from `.venv` (see [docs/MIGRATIONS.md](docs/MIGRATIONS.md)). Do **not** use `npx prisma` — Node Prisma 7 is incompatible with this schema.

| Command | When |
|---------|------|
| `python -m prisma migrate deploy` | Apply pending migrations (CI, Supabase, fresh clone) |
| `python -m prisma migrate dev --name <change>` | Local schema change → new migration SQL |
| `python -m prisma migrate status` | Check drift / pending migrations |

Initial schema lives in `prisma/migrations/20260521143000_init/`. After editing `schema.prisma`, run `migrate dev` to add a new timestamped migration — do **not** use `db push` for shared environments.

### OTP email (Brevo)

Sign-up and password-reset codes are sent via [Brevo](https://app.brevo.com/) transactional API ([docs](https://developers.brevo.com/docs/send-a-transactional-email)).

1. In Brevo: **SMTP & API** → create an **API key** (v3).
2. **Senders** → add and verify the **From** address you will use.
3. In `Backend/.env`:

```env
BREVO_API_KEY="xkeysib-..."
BREVO_SENDER_EMAIL="noreply@your-verified-domain.com"
BREVO_SENDER_NAME="AI-Accounts"
AUTH_EXPOSE_OTP_IN_RESPONSE="false"
```

Restart the API after changing `.env`. If Brevo is not configured, set `AUTH_EXPOSE_OTP_IN_RESPONSE="true"` for local dev (code shown on the verify-email page).

## Local dev (API + database)

### Local dev performance

For **local development**, use the Supabase **session pooler** (port `5432`) with `connection_limit=10` in `DATABASE_URL`. This allows parallel API requests (dashboard load, shell warmup) without queuing behind the global DB gate in [`db_concurrency_middleware`](src/app/middleware/db_concurrency.py). The dashboard command-center fans out ~18 concurrent queries via `asyncio.gather`; a pool of 10 lets them run in ~2 waves instead of ~4, roughly halving the dashboard's DB phase. Keep it ≤ the session pooler's per-client limit (raise cautiously — one uvicorn process only).

| Environment | `DATABASE_URL` |
|-------------|----------------|
| **Local dev** | Session pooler `:5432`, `connection_limit=10` (no `pgbouncer=true`) |
| **Production** | Transaction pooler `:6543`, `pgbouncer=true&connection_limit=1` |

With `connection_limit=1`, every HTTP handler serializes on one Prisma connection — a full page load with 10 parallel fetches can take 15–30s wall time.

- **Migrations** `DIRECT_URL`: session pooler port `5432` — use only for `python scripts/migrate_deploy.py` or `db execute`.
- Run **one** uvicorn process; multiple reload workers exhaust the Supabase session pool.
- If migrations fail on FK names, apply scripts under `scripts/` (e.g. `apply_p48_onboarding_fixed.sql`, `apply_p51_p52_migrations.sql`) using `DIRECT_URL`.

```powershell
$env:PYTHONPATH = "src"
$env:OUTBOX_POLL_ENABLED = "0"
.\.venv\Scripts\uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend dev proxies `/api/v1/*` to port 8000 — do not set `NEXT_PUBLIC_API_BASE_URL` unless bypassing the proxy.

- OpenAPI document: [docs/openapi.yaml](docs/openapi.yaml)
- Parity / gap tickets: [docs/PARITY-BACKLOG.md](docs/PARITY-BACKLOG.md)
- Production deploy: [docs/PRODUCTION-DEPLOYMENT.md](docs/PRODUCTION-DEPLOYMENT.md) (`Dockerfile`, `railway.toml`)
- Go-live verification: [docs/GO-LIVE-RUNBOOK.md](docs/GO-LIVE-RUNBOOK.md)

## Tests (no database)

```powershell
$env:PYTHONPATH = "src"
$env:SKIP_PRISMA = "1"
.\.venv\Scripts\pytest src/tests -q
```

`SKIP_PRISMA=1` skips Prisma connect for smoke tests (e.g. `/health`). Integration tests with a real DB should omit this flag.

## Key paths

| Path | Description |
|------|-------------|
| `docs/openapi.yaml` | Contract grouped by domain |
| `docs/PARITY-BACKLOG.md` | Catalog section 15 follow-ups |
| `src/app/constants/report_definitions.py` | Seeded report IDs (catalog §10.11 / §10.3) |
| `src/app/api/routes/tenant.py` | Tenant-scoped `/api/v1/companies/{company_id}/…` |
| `prisma/schema.prisma` | Phase 1–4 + cross-cutting tables |
