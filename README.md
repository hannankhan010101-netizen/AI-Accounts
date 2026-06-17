# AI-Accounts (Fast Accounts parity)

Monorepo for **Nafy-Pharma** go-live and FastAccounts migration parity.

| Area | Path |
|------|------|
| API (FastAPI + Prisma) | [`Backend/`](Backend/) |
| UI (Next.js) | [`Frontend/`](Frontend/) |
| Migration / go-live scripts | [`scripts/`](scripts/) |
| Parity tracker | [`Backend/docs/AI-ACCOUNTS-PARITY-STATUS.md`](Backend/docs/AI-ACCOUNTS-PARITY-STATUS.md) |
| Parity progress (signals) | [`Backend/docs/PARITY-PROGRESS-LATEST.md`](Backend/docs/PARITY-PROGRESS-LATEST.md) |
| Production deploy | [`Backend/docs/PRODUCTION-DEPLOYMENT.md`](Backend/docs/PRODUCTION-DEPLOYMENT.md) |
| Deploy quickstart | [`Backend/docs/DEPLOY-QUICKSTART.md`](Backend/docs/DEPLOY-QUICKSTART.md) |
| Day-1 ops | [`Backend/docs/DAY-1-OPERATIONS.md`](Backend/docs/DAY-1-OPERATIONS.md) |
| Go-live runbook | [`Backend/docs/GO-LIVE-RUNBOOK.md`](Backend/docs/GO-LIVE-RUNBOOK.md) |

## Quick commands

```powershell
# Local API
cd Backend
$env:PYTHONPATH = "src"
python -m uvicorn app.main:app --reload --port 8000

# Local UI
cd Frontend
npm run dev

# Full release gate (CI + tenant DB + go-live; dev .env OK)
.\scripts\release-check.ps1 -SkipEnvStrict

# Go-live verification only (faster)
.\scripts\go-live.ps1

# Local CI gate (mirrors GitHub Actions)
.\scripts\ci-local.ps1

# Before production deploy
.\scripts\deploy-preflight.ps1 -Strict
# Copy env templates: Backend/.env.production.example, Frontend/.env.production.example

# After API is live
python scripts/_post_deploy_smoke.py --api-url https://your-api-host
```

## Deploy

- **API:** `Backend/Dockerfile` + `Backend/railway.toml` (Railway or any Docker host)
- **UI:** `Frontend/vercel.json` (Vercel; set `NEXT_PUBLIC_API_BASE_URL`)
- **CI:** `.github/workflows/ci.yml` · manual go-live: `.github/workflows/go-live.yml`

Tenant (migrated): `cmpfm1nst0001lhq3rz09938z` — go-live **GO** per [`GO-LIVE-SIGNOFF-LATEST.md`](Backend/docs/GO-LIVE-SIGNOFF-LATEST.md).
