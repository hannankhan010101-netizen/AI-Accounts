# Production hardening checklist

Use before go-live and after each foundation phase (P0–P9).

## Secrets and config

- [ ] `JWT_SECRET_KEY` is a strong random value (≥32 chars), not the dev default
- [ ] Secrets via `SECRETS_VAULT_FILE`, `SECRETS_AWS_SECRET_ARN`, or `VAULT_*` (see P10); PayPro rotation per [PAYPRO-CREDENTIAL-ROTATION.md](./PAYPRO-CREDENTIAL-ROTATION.md)
- [ ] `.env` is not committed; production uses injected env only
- [ ] `AUTH_EXPOSE_OTP_IN_RESPONSE=0` in production

## Network and webhooks

- [ ] `PAYPRO_WEBHOOK_ALLOWED_IPS` and `KUICKPAY_WEBHOOK_ALLOWED_IPS` set to provider egress ranges
- [ ] `PAYPRO_WEBHOOK_SECRET` / `KUICKPAY_WEBHOOK_SECRET` configured and rotated
- [ ] `RATE_LIMIT_WEBHOOKS_PER_MINUTE` tuned for expected traffic
- [ ] TLS terminates at load balancer; HSTS enabled on frontend

## Database

- [ ] `DATABASE_URL` uses least-privilege DB user
- [ ] `DATABASE_READ_URL` points to read replica for report worker (optional)
- [ ] Migrations applied: `python -m prisma migrate deploy`
- [ ] Backups and restore tested

## Background jobs

- [ ] `OUTBOX_POLL_ENABLED=1` for import/report processing
- [ ] `FBR_RETRY_ENABLED=1` with `FBR_MAX_RETRY_COUNT` appropriate for PRAL SLA
- [ ] `CLICKHOUSE_URL` + `CLICKHOUSE_SYNC_INTERVAL_SECONDS` if analytics export required

## Observability

- [ ] Application logs aggregated (structural JSON recommended)
- [ ] Monitor FBR errors: `GET /fbr/submissions/errors`
- [ ] Monitor report catalog gap: `GET /reports/catalog-coverage`
- [ ] Audit log reviewed for `security.*` transaction types

## Functional smoke

- [ ] Sales invoice draft → approve → GL
- [ ] PayPro initiate → webhook → receipt + allocation
- [ ] FBR submit (stub or PRAL) → poll
- [ ] Lock date blocks backdated documents
- [ ] Per-user lock date extension works

## Frontend

- [ ] CORS `CORS_ORIGINS` lists production app URL only
- [ ] Online payments and FBR error pages reachable from Settings menu
