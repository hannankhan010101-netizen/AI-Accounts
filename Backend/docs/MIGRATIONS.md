# Database migrations

Use the **Python Prisma CLI** from the Backend virtualenv — not `npx prisma` (Node Prisma 7 rejects `url` in `schema.prisma`).

```powershell
cd Backend
$env:PYTHONPATH = "src"
.\.venv\Scripts\python scripts/migrate_deploy.py
.\.venv\Scripts\python scripts/migrate_status.py
.\.venv\Scripts\python -m prisma generate
```

`migrate_deploy.py` and `migrate_status.py` copy `DIRECT_URL` → `DATABASE_URL` so CLI commands do not fail on the `:6543` transaction pooler (P1017).

**Do not** run `npx prisma migrate` — Node Prisma 7 rejects `url` in `schema.prisma`.

## Schema drift fixes (2026-05-29)

| Migration | Purpose |
|-----------|---------|
| `20260529130000_document_custom_fields` | `custom_fields` JSONB on SI/VI/SR/VP/bank headers |
| `20260529130100_bank_reconciled_at` | `reconciled_at` on bank payments/receipts/transfers + SR/VP |

## GST line columns (planning docs + credits)

| Migration | Purpose |
|-----------|---------|
| `20260522130000_planning_doc_gst_lines` | `line_subtotal`, `gst_code`, `gst_rate`, `tax_amount` on quotation / sales order / purchase order lines |
| `20260522140000_credit_gst_lines` | Same fields on sales / supplier credit lines |

## Failed migration recovery

If `migrate deploy` stops with P3018:

```powershell
.\.venv\Scripts\python -m prisma migrate resolve --rolled-back <migration_name>
.\.venv\Scripts\python -m prisma migrate deploy
```

## Company table name

The init migration creates `"Company"` (PascalCase). Foundation migrations must reference `"Company"("id")`, not `"companies"`.
