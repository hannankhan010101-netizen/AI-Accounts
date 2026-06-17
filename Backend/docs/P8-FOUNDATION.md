# P8 — FBR retry, webhook IP allowlists, ClickHouse cron, receipt allocations (implemented)

Builds on [P7-FOUNDATION.md](./P7-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P8.1 | **Webhook IP allowlists** | `PAYPRO_WEBHOOK_ALLOWED_IPS`, `KUICKPAY_WEBHOOK_ALLOWED_IPS` (comma-separated) |
| P8.2 | **FBR retry queue** | `retry_count`, `last_error`, `next_retry_at` on submissions; outbox `fbr.submission.retry` |
| P8.3 | **FBR error dashboard** | `GET /fbr/submissions/errors`, `POST .../fbr/retry`, `POST /fbr/retry-pending` |
| P8.4 | **FBR background retry** | 300s loop in `main.py` when `FBR_RETRY_ENABLED=1` (default) |
| P8.5 | **ClickHouse scheduled sync** | Background loop every `CLICKHOUSE_SYNC_INTERVAL_SECONDS` (default 3600) |
| P8.6 | **Report 145** | Customer products — dedicated SQL handler |
| P8.7 | **Receipt detail + allocations** | `GET /sales-receipts/{id}`; frontend `/sales/receipts/[id]` |
| P8.8 | **Frontend FBR errors** | Settings → FBR errors; invoice retry button on error status |

## Migration

```bash
cd Backend
python -m prisma migrate deploy
python -m prisma generate
```

Folder: `prisma/migrations/20260521230000_p8_foundation/`

## Environment

| Variable | Default | Purpose |
|----------|---------|---------|
| `PAYPRO_WEBHOOK_ALLOWED_IPS` | empty | Allow all when empty |
| `KUICKPAY_WEBHOOK_ALLOWED_IPS` | empty | Allow all when empty |
| `CLICKHOUSE_SYNC_INTERVAL_SECONDS` | 3600 | Scheduled re-export interval |
| `FBR_RETRY_ENABLED` | true | Background FBR retry loop |

## PRAL failure behaviour

When PRAL is enabled and HTTP submit fails, the submission moves to `status=error`, stores `lastError`, schedules `nextRetryAt`, and enqueues an outbox retry event. Stub mode (PRAL off) still accepts immediately.

## Next

See [P9-FOUNDATION.md](./P9-FOUNDATION.md) and [PRODUCTION-HARDENING.md](./PRODUCTION-HARDENING.md).
