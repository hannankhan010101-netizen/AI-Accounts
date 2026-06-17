"""Dashboard overview SQL — sales trend, stock counts, bank balances (Step 1)."""

from __future__ import annotations

SALES_BY_MONTH_SQL = """
SELECT
  to_char(si.invoice_date AT TIME ZONE 'UTC', 'YYYY-MM') AS month,
  SUM(si.total_amount) AS total_sales
FROM sales_invoices si
WHERE si.company_id = $1
  AND si.status = 'posted'
  AND si.invoice_date >= $2::timestamptz
  AND si.invoice_date <= $3::timestamptz
GROUP BY 1
ORDER BY 1
"""

STOCK_COUNTS_SQL = """
WITH qty_by_code AS (
  SELECT
    COALESCE(pb.product_code, '') AS product_code,
    SUM(pb.quantity_on_hand) AS qty
  FROM product_batches pb
  WHERE pb.company_id = $1
  GROUP BY 1
),
classified AS (
  SELECT
    CASE
      WHEN qty < 0 THEN 'oversold'
      WHEN qty = 0 THEN 'outOfStock'
      WHEN qty <= $2::numeric THEN 'lowStock'
      ELSE 'inStock'
    END AS bucket,
    COUNT(*)::int AS cnt
  FROM qty_by_code
  WHERE product_code <> ''
  GROUP BY 1
)
SELECT bucket, cnt FROM classified
"""

BANK_ACCOUNT_BALANCES_SQL = """
SELECT
  ba.id AS "bankAccountId",
  ba.name,
  ba.nominal_code AS "nominalCode",
  ba.currency,
  COALESCE(mv.balance, 0) AS balance
FROM bank_accounts ba
LEFT JOIN mv_nominal_balances mv
  ON mv.company_id = ba.company_id
  AND mv.nominal_code = ba.nominal_code
WHERE ba.company_id = $1
  AND ba.is_active = true
ORDER BY ba.name
"""
