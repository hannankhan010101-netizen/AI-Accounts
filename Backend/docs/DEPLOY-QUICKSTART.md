# Deploy quickstart — Nafy-Pharma

**Tenant:** `cmpfm1nst0001lhq3rz09938z` · **Go-live status:** **GO** (see [GO-LIVE-SIGNOFF-LATEST.md](./GO-LIVE-SIGNOFF-LATEST.md))

Use this checklist the first time you ship to production. Full detail: [PRODUCTION-DEPLOYMENT.md](./PRODUCTION-DEPLOYMENT.md). After deploy: [DAY-1-OPERATIONS.md](./DAY-1-OPERATIONS.md).

---

## 0. Push to GitHub (if not already)

```powershell
git init
git add .
git commit -m "AI-Accounts Nafy go-live baseline"
git remote add origin https://github.com/your-org/AI-Accounts.git
git push -u origin main
```

Railway and Vercel deploy from this repo. Do **not** commit `.env`, `.env.production.local`, or secrets.

---

## Before you push

**Validate tenant (prod DB, dev `.env` OK):**

```powershell
.\scripts\release-check.ps1 -SkipEnvStrict
```

**Validate production env (before Railway deploy):**

```powershell
copy Backend\.env.production.example Backend\.env.production.local
# Edit .env.production.local with real prod values (gitignored)
.\scripts\deploy-preflight.ps1 -Strict -EnvFile Backend\.env.production.local
```

**Full gate (prod env file + DB + go-live):**

```powershell
.\scripts\release-check.ps1 -EnvFile Backend\.env.production.local
```

**Readiness dashboard (no DB):**

```powershell
.\scripts\nafy-release-readiness.ps1
```

**Single deploy command:**

```powershell
.\scripts\nafy-deploy.ps1                              # pre-deploy only
.\scripts\nafy-deploy.ps1 -ApiUrl https://<api> -FrontendUrl https://<app> -RunGoLive
```

| Step | Pass? |
|------|-------|
| `ci-local.ps1` — pytest, typecheck, lint, build | |
| `deploy-preflight.ps1 -Strict` — prod env + DB Smart Settings | |
| GitHub Actions green on your branch | |

---

## 1. Supabase (already done for Nafy)

- [ ] Runtime URL on **6543** with `pgbouncer=true` → Railway `DATABASE_URL`
- [ ] Session URL on **5432** → Railway `DIRECT_URL` (release migrations only)

---

## 2. Railway (API)

1. New project → **Deploy from GitHub** → set **Root Directory** to `Backend/`
2. Uses [`Backend/Dockerfile`](../Dockerfile) + [`railway.toml`](../railway.toml) (release runs `migrate_deploy.py`)
3. Paste variables from [`Backend/.env.production.example`](../.env.production.example):

| Variable | Example |
|----------|---------|
| `DATABASE_URL` | `postgresql://...@...pooler.supabase.com:6543/postgres?pgbouncer=true&connection_limit=1&sslmode=require` |
| `DIRECT_URL` | `postgresql://...@...pooler.supabase.com:5432/postgres?sslmode=require` |
| `JWT_SECRET_KEY` | Random 64+ chars (not dev default) |
| `CORS_ORIGINS` | `https://app.yourdomain.com` |
| `APP_PUBLIC_URL` | `https://app.yourdomain.com` |
| `BREVO_API_KEY` / `BREVO_SENDER_EMAIL` | Verified Brevo sender |
| `OUTBOX_POLL_ENABLED` | `1` |

4. Deploy → confirm `GET https://<railway-host>/health` returns `{"status":"ok"}`

```powershell
python scripts/_post_deploy_smoke.py --api-url https://<railway-host>
# or: .\scripts\post-deploy.ps1 -ApiUrl https://<railway-host>
```

---

## 3. Vercel (Frontend)

1. Import repo → **Root Directory** `Frontend/`
2. Environment (Production):

```
NEXT_PUBLIC_API_BASE_URL=https://<railway-host>
```

(no trailing slash)

3. Deploy → open `/login` → test OTP email (Brevo)

---

## 4. Post-deploy sign-off

```powershell
# HTTP smoke (API + optional Vercel /login + CORS)
.\scripts\nafy-prod-handoff.ps1 -ApiUrl https://<railway-host> -FrontendUrl https://app.yourdomain.com

# When Backend/.env points at production DB — full data + parity gates
.\scripts\nafy-prod-handoff.ps1 -ApiUrl https://<railway-host> -FrontendUrl https://app.yourdomain.com -RunGoLive
```

Open [GO-LIVE-SIGNOFF-LATEST.md](./GO-LIVE-SIGNOFF-LATEST.md) and [NAFY-IN-SCOPE-SIGNOFF-LATEST.md](./NAFY-IN-SCOPE-SIGNOFF-LATEST.md).

**Required before business handoff:** complete [NAFY-UAT-CHECKLIST.md](./NAFY-UAT-CHECKLIST.md), then `.\scripts\record-uat-signoff.ps1` (writes [NAFY-UAT-SIGNOFF-LATEST.md](./NAFY-UAT-SIGNOFF-LATEST.md)).

Then follow [DAY-1-OPERATIONS.md](./DAY-1-OPERATIONS.md) for first login and month-end.

Optional UI smoke:

```powershell
cd Frontend
npx playwright test e2e/parity/smoke.spec.ts
```

---

## 5. Day-one operations

| Task | Where |
|------|--------|
| Draft SI/VI (~47 + ~17) | Approve in UI when they should post — **do not** bulk-post on summary GL |
| Import with GL | Settings → Import jobs → **Post to GL** |
| FBR (later) | Leave `FBR_PRAL_ENABLED=false` until credentials; stub mode works for UAT |
| Integrations status | Settings → Integration status |
| Month-end | TB, P&L, BS, statements, activity lists — in scope |

---

## Rollback

1. Redeploy previous Railway + Vercel builds.
2. Do not revert DB migrations without backup and a written plan ([MIGRATIONS.md](./MIGRATIONS.md)).
3. Re-run `go-live.ps1` after any data fix.

---

## GitHub Actions secrets

Add under **Settings → Secrets and variables → Actions** before running manual workflows:

| Secret | Used by |
|--------|---------|
| `DATABASE_URL` | Go-live verification, Production env check |
| `DIRECT_URL` | Go-live verification, Production env check, Railway release |
| `JWT_SECRET_KEY` | Production env check |
| `CORS_ORIGINS` | Production env check |
| `APP_PUBLIC_URL` | Production env check |
| `BREVO_API_KEY` / `BREVO_SENDER_EMAIL` | Production env check |
| `OUTBOX_POLL_ENABLED` | Production env check (`1`) |

Workflows: **Go-live verification** · **Production env check**

---

## Related

| Doc | Purpose |
|-----|---------|
| [GO-LIVE-RUNBOOK.md](./GO-LIVE-RUNBOOK.md) | Tenant verification detail |
| [PRODUCTION-DEPLOYMENT.md](./PRODUCTION-DEPLOYMENT.md) | Architecture, security, CI |
| [AI-ACCOUNTS-PARITY-STATUS.md](./AI-ACCOUNTS-PARITY-STATUS.md) | Parity tracker |
