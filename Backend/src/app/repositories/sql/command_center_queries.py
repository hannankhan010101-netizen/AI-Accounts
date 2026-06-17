"""Command center dashboard SQL — sales granularity, inventory, movers, overdue."""

from __future__ import annotations

SALES_BY_DAY_SQL = """
SELECT
  to_char(si.invoice_date AT TIME ZONE 'UTC', 'YYYY-MM-DD') AS label,
  SUM(si.total_amount) AS total_sales
FROM sales_invoices si
WHERE si.company_id = $1
  AND si.status = 'posted'
  AND si.invoice_date >= $2::timestamptz
  AND si.invoice_date <= $3::timestamptz
GROUP BY 1
ORDER BY 1
"""

SALES_BY_WEEK_SQL = """
SELECT
  to_char(date_trunc('week', si.invoice_date AT TIME ZONE 'UTC'), 'IYYY-"W"IW') AS label,
  SUM(si.total_amount) AS total_sales
FROM sales_invoices si
WHERE si.company_id = $1
  AND si.status = 'posted'
  AND si.invoice_date >= $2::timestamptz
  AND si.invoice_date <= $3::timestamptz
GROUP BY 1
ORDER BY 1
"""

SALES_BY_MONTH_PERIOD_SQL = """
SELECT
  to_char(si.invoice_date AT TIME ZONE 'UTC', 'YYYY-MM') AS label,
  SUM(si.total_amount) AS total_sales
FROM sales_invoices si
WHERE si.company_id = $1
  AND si.status = 'posted'
  AND si.invoice_date >= $2::timestamptz
  AND si.invoice_date <= $3::timestamptz
GROUP BY 1
ORDER BY 1
"""

MONTHLY_REVENUE_SQL = """
SELECT COALESCE(SUM(si.total_amount), 0) AS total
FROM sales_invoices si
WHERE si.company_id = $1
  AND si.status = 'posted'
  AND si.invoice_date >= $2::timestamptz
  AND si.invoice_date <= $3::timestamptz
"""

INVENTORY_VALUE_SQL = """
SELECT COALESCE(SUM(pb.quantity_on_hand * COALESCE(p.cost, 0)), 0) AS total_value
FROM product_batches pb
LEFT JOIN products p
  ON p.company_id = pb.company_id AND p.code = pb.product_code
WHERE pb.company_id = $1
"""

INVENTORY_STOCK_ROWS_SQL = """
WITH qty_by_product AS (
  SELECT
    pb.product_code,
    COALESCE(p.name, pb.product_code) AS product_name,
    SUM(pb.quantity_on_hand) AS qty,
    COALESCE(p.cost, 0) AS unit_cost
  FROM product_batches pb
  LEFT JOIN products p
    ON p.company_id = pb.company_id AND p.code = pb.product_code
  WHERE pb.company_id = $1
    AND pb.product_code <> ''
  GROUP BY 1, 2, 4
)
SELECT
  product_code AS "productCode",
  product_name AS "productName",
  qty AS quantity,
  (qty * unit_cost) AS value
FROM qty_by_product
WHERE qty <= $2::numeric
ORDER BY qty ASC, product_code
LIMIT 15
"""

INVENTORY_OUT_OF_STOCK_SQL = """
WITH qty_by_product AS (
  SELECT
    pb.product_code,
    COALESCE(p.name, pb.product_code) AS product_name,
    SUM(pb.quantity_on_hand) AS qty
  FROM product_batches pb
  LEFT JOIN products p
    ON p.company_id = pb.company_id AND p.code = pb.product_code
  WHERE pb.company_id = $1
    AND pb.product_code <> ''
  GROUP BY 1, 2
)
SELECT
  product_code AS "productCode",
  product_name AS "productName",
  qty AS quantity,
  0 AS value
FROM qty_by_product
WHERE qty <= 0
ORDER BY product_code
LIMIT 15
"""

INVENTORY_OVERSTOCK_SQL = """
WITH qty_by_product AS (
  SELECT
    pb.product_code,
    COALESCE(p.name, pb.product_code) AS product_name,
    SUM(pb.quantity_on_hand) AS qty,
    COALESCE(p.cost, 0) AS unit_cost
  FROM product_batches pb
  LEFT JOIN products p
    ON p.company_id = pb.company_id AND p.code = pb.product_code
  WHERE pb.company_id = $1
    AND pb.product_code <> ''
  GROUP BY 1, 2, 4
)
SELECT
  product_code AS "productCode",
  product_name AS "productName",
  qty AS quantity,
  (qty * unit_cost) AS value
FROM qty_by_product
WHERE qty > $2::numeric
ORDER BY qty DESC
LIMIT 15
"""

FAST_MOVERS_SQL = """
SELECT
  sil.product_code AS "productCode",
  COALESCE(p.name, sil.product_code) AS "productName",
  SUM(sil.quantity) AS "quantitySold",
  SUM(sil.line_total) AS "revenue"
FROM sales_invoice_lines sil
JOIN sales_invoices si ON si.id = sil.sales_invoice_id
LEFT JOIN products p
  ON p.company_id = si.company_id AND p.code = sil.product_code
WHERE si.company_id = $1
  AND si.status = 'posted'
  AND si.invoice_date >= $2::timestamptz
  AND si.invoice_date <= $3::timestamptz
  AND sil.product_code IS NOT NULL
  AND sil.product_code <> ''
GROUP BY 1, 2
ORDER BY SUM(sil.quantity) DESC
LIMIT 10
"""

SLOW_MOVERS_SQL = """
SELECT
  sil.product_code AS "productCode",
  COALESCE(p.name, sil.product_code) AS "productName",
  SUM(sil.quantity) AS "quantitySold",
  SUM(sil.line_total) AS "revenue"
FROM sales_invoice_lines sil
JOIN sales_invoices si ON si.id = sil.sales_invoice_id
LEFT JOIN products p
  ON p.company_id = si.company_id AND p.code = sil.product_code
WHERE si.company_id = $1
  AND si.status = 'posted'
  AND si.invoice_date >= $2::timestamptz
  AND si.invoice_date <= $3::timestamptz
  AND sil.product_code IS NOT NULL
  AND sil.product_code <> ''
GROUP BY 1, 2
HAVING SUM(sil.quantity) > 0
ORDER BY SUM(sil.quantity) ASC
LIMIT 10
"""

COGS_TOTAL_SQL = """
SELECT COALESCE(SUM(jl.debit - jl.credit), 0) AS cogs
FROM journal_lines jl
INNER JOIN journals j ON j.id = jl.journal_id
LEFT JOIN nominal_accounts na ON na.code = jl.nominal_code
LEFT JOIN coa_sections s ON s.id = na.section_id
LEFT JOIN coa_categories c ON c.id = s.category_id AND c.company_id = j.company_id
WHERE j.company_id = $1
  AND j.status = 'posted'
  AND j.journal_date >= $2::timestamptz
  AND j.journal_date <= $3::timestamptz
  AND c.name ILIKE '%cost of sales%'
"""

REVENUE_BY_CATEGORY_SQL = """
SELECT
  COALESCE(c.name, 'Other') AS label,
  SUM(jl.credit - jl.debit) AS amount
FROM journal_lines jl
INNER JOIN journals j ON j.id = jl.journal_id
LEFT JOIN nominal_accounts na ON na.code = jl.nominal_code
LEFT JOIN coa_sections s ON s.id = na.section_id
LEFT JOIN coa_categories c ON c.id = s.category_id AND c.company_id = j.company_id
WHERE j.company_id = $1
  AND j.status = 'posted'
  AND j.journal_date >= $2::timestamptz
  AND j.journal_date <= $3::timestamptz
  AND c.category_type = 'Income'
GROUP BY 1
HAVING SUM(jl.credit - jl.debit) <> 0
ORDER BY 2 DESC
LIMIT 8
"""
