# Scripts

## Go-live (Nafy-Pharma / migrated tenant)

| Script | Purpose |
|--------|---------|
| `release-check.ps1` / `release-check.sh` | Full gate: CI + preflight + go-live |
| `deploy-preflight.ps1` / `deploy-preflight.sh` | Prod env check + optional DB preflight |
| `_prod_env_check.py` | API env validation (no DB); use `--strict` before prod |
| `_post_deploy_smoke.py` | HTTP `/health` smoke after deploy |
| `post-deploy.ps1` | Smoke wrapper + next-step hints |
| `go-live.ps1` / `go-live.sh` | Run full verification suite |
| `fastaccounts_migrate/_go_live_check.py` | Preflight + reconcile + TB + health + reports + integrations + AR/AP |
| `fastaccounts_migrate/_preflight_deploy.py` | Env, Smart Settings defaults, bank nominals only |
| `fastaccounts_migrate/_migration_health.py` | Draft/orphan document GL linkage |
| `fastaccounts_migrate/_report_spot_check.py` | Priority report row counts |
| `_generate_feature_matrix.py` | Regenerate `Backend/docs/FA-FEATURE-MATRIX.csv` |
| `_parity_progress.py` | Regenerate `Backend/docs/PARITY-PROGRESS-LATEST.md` (go-live vs full parity signals) |

Output: `Backend/docs/GO-LIVE-SIGNOFF-LATEST.md`

See `Backend/docs/GO-LIVE-RUNBOOK.md`, `Backend/docs/DAY-1-OPERATIONS.md`, and `Backend/docs/PRODUCTION-DEPLOYMENT.md`.

**Tenant override:** `GO_LIVE_COMPANY_ID` or `PREFLIGHT_COMPANY_ID` (default Nafy-Pharma).

**CI:** `.github/workflows/ci.yml` (every PR); `.github/workflows/go-live.yml` (manual, needs `DATABASE_URL` + `DIRECT_URL` secrets).

**Local CI:** `.\scripts\ci-local.ps1` or `./scripts/ci-local.sh` (pytest + typecheck + lint + build).

**Release gate:** `.\scripts\release-check.ps1 -SkipEnvStrict` (tenant/DB) · `-EnvFile Backend\.env.production.local` (prod env)

**GitHub:** Actions → **Production env check** (manual, validates repo secrets with `--strict`).
