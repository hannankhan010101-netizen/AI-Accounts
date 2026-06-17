# P6 — PayPro settlement, ClickHouse, report expansion, journal lock spine (implemented)

Builds on [P5-FOUNDATION.md](./P5-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P6.1 | **PayPro live client** | `PayproClient` — `POST {PAYPRO_API_URL}/checkout` when enabled |
| P6.2 | **PayPro → sales receipt** | Webhook settlement auto-creates SR + GL when `bankAccountId` or `payproDefaultBankAccountId` set |
| P6.3 | **ClickHouse export** | Auto after report run in outbox worker; `POST .../reports/runs/{id}/export-clickhouse` |
| P6.4 | **Report pagination** | `page`, `pageSize`, `includePaginationMeta` on all `ReportQueryService` handlers |
| P6.5 | **New report handlers** | `031`, `033`, `054`, `182`, `GL` + expanded aliases (`143`, `160`, `162`, …) |
| P6.6 | **Purchases catalog** | `report_definitions` — Purchases and Suppliers group |
| P6.7 | **Journal lock spine** | `LockDateService` enforced inside `JournalService.create_journal` |
| P6.8 | **Assembly job lock** | `POST /assembly/jobs` checks lock date on `jobDate` |

## Environment

| Variable | Purpose |
|----------|---------|
| `PAYPRO_API_URL` | Live checkout API base |
| `PAYPRO_API_KEY` | Optional bearer token |
| `CLICKHOUSE_URL` | HTTP interface (e.g. `http://localhost:8123`) |
| `CLICKHOUSE_DATABASE` | Target database (default `default`) |
| `CLICKHOUSE_TABLE` | Target table (default `report_runs`) |

## Smart Settings

Add to `defaults` JSON:

```json
{
  "payproDefaultBankAccountId": "<bank-account-cuid>"
}
```

Used when PayPro initiate omits `bankAccountId`.

## PayPro settlement

1. `POST /payments/paypro/initiate` with `customerId`, `amount`, optional `bankAccountId`.
2. Customer pays via checkout URL.
3. `POST /payments/paypro/webhook` with `merchantRef` — creates sales receipt + GL if not already settled.

## ClickHouse table (example)

```sql
CREATE TABLE default.report_runs (
  company_id String,
  report_id String,
  run_id String,
  row_json String
) ENGINE = MergeTree ORDER BY (company_id, report_id, run_id);
```

## Report pagination

```json
{
  "reportId": "028",
  "criteria": {
    "dateFrom": "2026-01-01",
    "dateTo": "2026-05-21",
    "page": 1,
    "pageSize": 500,
    "includePaginationMeta": true
  }
}
```

## Next

See [P7-FOUNDATION.md](./P7-FOUNDATION.md).
