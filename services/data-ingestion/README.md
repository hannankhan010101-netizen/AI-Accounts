# Data Ingestion Service

Enterprise ERP migration pipeline for AI-Accounts.

## Quick start

```powershell
cd services/data-ingestion
docker compose up -d
cp .env.example .env
npm install
npx prisma generate
npx prisma migrate dev --name init
npm run dev      # API :4100
npm run worker   # BullMQ workers
```

## FastAccounts migration

```powershell
# 1. Create run (via API or UI)
# 2. Point sourceKey at labeled export:
POST /api/v1/companies/{companyId}/migrations/runs
{
  "name": "FastAccounts customers",
  "module": "customers",
  "sourceType": "fastaccounts",
  "sourceSystem": "fastaccounts",
  "sourceKey": "C:/path/to/fastaccounts_labeled_data.json",
  "mappingProfileId": "..."
}

# 3. Start pipeline
POST .../runs/{runId}/start
```

## Pipeline stages

`extract → validate → map → transform → dedupe → reconcile → import → verify → audit`

See [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) for full design.

## Frontend

Migration wizard: `/settings/migrations` (proxied to `:4100` in dev).
