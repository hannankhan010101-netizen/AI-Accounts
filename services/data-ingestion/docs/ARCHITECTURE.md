# Data Ingestion & ERP Migration Architecture

Enterprise-grade pipeline for importing accounting, inventory, and business data into AI-Accounts from CSV/XLSX, REST APIs, webhooks, and batch migrations (e.g. FastAccounts).

## Stack

| Layer | Technology |
|-------|------------|
| Runtime | Node.js 20+, TypeScript |
| API | Fastify |
| Pipeline DB | PostgreSQL (Prisma) — `ing_*` tables |
| Target DB | AI-Accounts Backend via REST (`/api/v1/companies/{id}/…`) |
| Queue | Redis + BullMQ |
| Object storage | S3-compatible (uploads, error reports, staging blobs) |
| Streaming parsers | `csv-parse`, `exceljs` (chunked reads) |

## Pipeline Stages

```
┌─────────┐   ┌──────────┐   ┌─────┐   ┌───────────┐   ┌───────┐   ┌────────────┐
│ Extract │ → │ Validate │ → │ Map │ → │ Transform │ → │ Dedupe│ → │ Reconcile  │
└─────────┘   └──────────┘   └─────┘   └───────────┘   └───────┘   └────────────┘
                                                                        │
    ┌─────────┐   ┌────────┐   ┌───────┐                                │
    │  Audit  │ ← │ Verify │ ← │ Import│ ←──────────────────────────────┘
    └─────────┘   └────────┘   └───────┘
```

Each stage is a **BullMQ job** with idempotency key `{migrationRunId}:{stage}:{chunkIndex}`. Failed chunks retry with exponential backoff; completed chunks are skipped on replay.

## Multi-Tenant Isolation

- Every `IngMigrationRun` is scoped to `companyId` (matches Backend `Company.id`).
- JWT from AI-Accounts Backend validates tenant access on every API call.
- S3 keys: `tenants/{companyId}/migrations/{runId}/…`
- Staging rows indexed by `(companyId, migrationRunId)`.
- Workers never process cross-tenant chunks in the same transaction.

## Module Import Order (FK-safe)

Dependencies are enforced by the orchestrator:

1. `chart_of_accounts`, `taxes`, `projects`
2. `customers`, `suppliers`, `products`
3. `invoices`, `bills`
4. `receipts`, `payments`, `bank_transactions`
5. `stock_movements`, `journals`

## Data Integrity Rules

| Rule | Enforcement |
|------|-------------|
| GL balancing | Journals: Σ debits = Σ credits (±0.01 tolerance) |
| Inventory qty | Stock movements reconcile opening + movements = closing |
| Currency | Normalize to company base currency; store FX rate + original |
| Timestamps | Parse as UTC; preserve source `createdAt` in `externalMetadata` |
| FK references | Resolve via `IngExternalIdMap` (sourceSystem + sourceId → targetId) |
| Idempotency | Upsert by `(companyId, sourceSystem, entityType, externalId)` |

## Queue Topology

```
migration-orchestrator   → fans out stage jobs per chunk
migration-extract        → parse file / pull API → staging rows
migration-validate       → row + cross-row rules
migration-map            → apply mapping profile
migration-transform      → types, dates, currency, FK lookup
migration-dedupe         → fingerprint hash within run + against existing
migration-reconcile      → GL / inventory / AR-AP totals
migration-import         → transactional bulk insert via Backend API
migration-verify         → post-import counts + sample checks
migration-audit          → write audit trail + error report to S3
```

Workers scale horizontally; chunk size defaults to 500 rows (configurable per module).

## Storage Layout (S3)

```
tenants/{companyId}/migrations/{runId}/
  source/{filename}           # encrypted at rest (AES-256-GCM)
  staging/chunk-{n}.jsonl     # optional spill for large runs
  errors/chunk-{n}.csv        # downloadable error reports
  preview/sample.json         # first 50 mapped rows
  reconciliation/report.json
```

## API Surface

Base: `http://localhost:4100/api/v1/companies/{companyId}/migrations`

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/runs` | Start migration run |
| GET | `/runs` | List runs + progress |
| GET | `/runs/:id` | Run detail + stage logs |
| POST | `/runs/:id/cancel` | Cancel pending jobs |
| POST | `/runs/:id/retry` | Retry failed chunks |
| POST | `/runs/:id/rollback` | Reverse imported chunk (if supported) |
| POST | `/uploads/presign` | Signed upload URL |
| GET | `/mapping-profiles` | List saved profiles |
| POST | `/mapping-profiles` | Create profile |
| POST | `/mapping-profiles/:id/suggest` | AI-assisted field matching |
| POST | `/preview` | Live validation preview (≤100 rows) |
| POST | `/webhooks/:provider` | Inbound sync webhook |

## Integration with AI-Accounts Backend

The ingestion service **does not duplicate** the Prisma Python client. Target writes go through:

- Existing `POST /import-jobs` for supported types (customers, products, bank_payments)
- New internal bulk endpoints (future) for invoices, bills, journals
- `TargetApiClient` with batching, rate limiting, and correlation IDs

Legacy FastAccounts JSON (`scripts/fastaccounts_export/output/`) is loaded via `FastAccountsAdapter` extractor.

## Performance Targets

| Metric | Target |
|--------|--------|
| Throughput | 10k rows/min per worker (simple entities) |
| Max file size | 500 MB CSV / 1M rows via streaming |
| Memory | ≤256 MB per worker (chunked processing) |
| Parallelism | 4 workers × N chunks (Redis-backed) |

## Security

- RBAC: `settings.import` permission (mirrors Backend)
- Temp files encrypted before S3 upload
- Presigned URLs expire in 15 minutes
- Full audit trail in `IngAuditEntry` + Backend `AuditLogEntry` on import
- Webhook HMAC verification per provider

## Deployment

```bash
cd services/data-ingestion
docker compose up -d redis   # local Redis
cp .env.example .env
npm install
npx prisma migrate dev
npm run dev          # API on :4100
npm run worker       # BullMQ workers
```

Frontend proxies `/api/migrations/*` → ingestion service in dev.
