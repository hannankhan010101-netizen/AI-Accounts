# E2E (Playwright)

## Unauthenticated (default)

```bash
cd Frontend
npx playwright test
```

Runs login smoke and responsive checks. Starts `npm run dev` unless `CI` is set.

## Authenticated parity

1. Backend on `http://127.0.0.1:8000` (or set `PLAYWRIGHT_API_URL`).
2. Valid user with access to tenant `cmpfm1nst0001lhq3rz09938z` (Nafy-Pharma).

```bash
cd Frontend
set PLAYWRIGHT_EMAIL=your@email
set PLAYWRIGHT_PASSWORD=your-password
set PLAYWRIGHT_COMPANY_ID=cmpfm1nst0001lhq3rz09938z
npx playwright test e2e/auth.setup.ts --project=setup

set PLAYWRIGHT_AUTH_READY=1
npx playwright test e2e/parity/authenticated.spec.ts --project=authenticated
```

`e2e/.auth/user.json` is gitignored; regenerate when tokens expire.

## Environment

| Variable | Purpose |
|----------|---------|
| `PLAYWRIGHT_BASE_URL` | Frontend (default `http://127.0.0.1:3000`) |
| `PLAYWRIGHT_SMOKE_ONLY` | `1` to run only `e2e/parity/smoke.spec.ts` (CI uses this) |
| `PLAYWRIGHT_API_URL` | Backend for login setup (default `http://127.0.0.1:8000`) |
| `PLAYWRIGHT_EMAIL` / `PLAYWRIGHT_PASSWORD` | Credentials for setup |
| `PLAYWRIGHT_COMPANY_ID` | Tenant id in localStorage |
| `PLAYWRIGHT_AUTH_READY` | `1` to run authenticated specs |
