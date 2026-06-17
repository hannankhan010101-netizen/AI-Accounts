"""Grouped report aggregates (Phase 4/5 — avoid loading full document sets)."""

from __future__ import annotations

SALE_SUMMARY_BY_DATE_SQL = """
SELECT
  si.invoice_date::date AS "invoiceDate",
  SUM(si.total_amount) AS "totalSales"
FROM sales_invoices si
WHERE si.company_id = $1
  AND ($2::text IS NULL OR si.status = $2)
  AND ($3::timestamptz IS NULL OR si.invoice_date >= $3::timestamptz)
  AND ($4::timestamptz IS NULL OR si.invoice_date <= $4::timestamptz)
  AND ($5 IS NULL OR si.customer_id = $5)
GROUP BY 1
ORDER BY 1
"""

SALE_SUMMARY_BY_CUSTOMER_SQL = """
SELECT
  si.customer_id AS "customerId",
  SUM(si.total_amount) AS "totalSales"
FROM sales_invoices si
WHERE si.company_id = $1
  AND ($2::text IS NULL OR si.status = $2)
  AND ($3::timestamptz IS NULL OR si.invoice_date >= $3::timestamptz)
  AND ($4::timestamptz IS NULL OR si.invoice_date <= $4::timestamptz)
GROUP BY 1
ORDER BY 2 DESC
"""

PURCHASE_SUMMARY_BY_SUPPLIER_SQL = """
SELECT
  sb.supplier_id AS "supplierId",
  SUM(sb.total_amount) AS "totalPurchases"
FROM supplier_bills sb
WHERE sb.company_id = $1
  AND ($2::text IS NULL OR sb.status = $2)
  AND ($3::timestamptz IS NULL OR sb.bill_date >= $3::timestamptz)
  AND ($4::timestamptz IS NULL OR sb.bill_date <= $4::timestamptz)
GROUP BY 1
ORDER BY 2 DESC
"""

PRODUCT_SALES_BY_PRODUCT_SQL = """
SELECT
  COALESCE(sil.product_code, '—') AS "productCode",
  SUM(sil.line_total) AS "totalSales"
FROM sales_invoice_lines sil
INNER JOIN sales_invoices si ON si.id = sil.sales_invoice_id
WHERE si.company_id = $1
  AND ($2::text IS NULL OR si.status = $2)
  AND ($3::timestamptz IS NULL OR si.invoice_date >= $3::timestamptz)
  AND ($4::timestamptz IS NULL OR si.invoice_date <= $4::timestamptz)
  AND ($5::text IS NULL OR sil.product_code = $5)
GROUP BY 1
ORDER BY 2 DESC
"""

PRODUCT_PURCHASES_BY_PRODUCT_SQL = """
SELECT
  COALESCE(sbl.product_code, '—') AS "productCode",
  SUM(sbl.line_total) AS "totalPurchases"
FROM supplier_bill_lines sbl
INNER JOIN supplier_bills sb ON sb.id = sbl.supplier_bill_id
WHERE sb.company_id = $1
  AND ($2::text IS NULL OR sb.status = $2)
  AND ($3::timestamptz IS NULL OR sb.bill_date >= $3::timestamptz)
  AND ($4::timestamptz IS NULL OR sb.bill_date <= $4::timestamptz)
  AND ($5::text IS NULL OR sbl.product_code = $5)
GROUP BY 1
ORDER BY 2 DESC
"""

PROJECT_PAYMENTS_BY_CODE_SQL = """
SELECT
  jl.project_code AS "projectCode",
  SUM(jl.debit) AS "totalPayments"
FROM journal_lines jl
INNER JOIN journals j ON j.id = jl.journal_id
WHERE j.company_id = $1
  AND j.status = 'posted'
  AND jl.project_code IS NOT NULL
  AND jl.project_code <> ''
  AND ($2::timestamptz IS NULL OR j.journal_date >= $2::timestamptz)
  AND ($3::timestamptz IS NULL OR j.journal_date <= $3::timestamptz)
GROUP BY 1
ORDER BY 2 DESC
"""

STOCK_BATCH_QUANTITY_SQL = """
SELECT
  pb.product_code AS "productCode",
  pb.batch_number AS "batchNumber",
  pb.quantity_on_hand AS "quantityOnHand"
FROM product_batches pb
WHERE pb.company_id = $1
  AND ($2::text IS NULL OR pb.product_code = $2)
ORDER BY pb.product_code, pb.batch_number
LIMIT 10000
"""

STOCK_VALUATION_SQL = """
SELECT
  pb.product_code AS "productCode",
  pb.batch_number AS "batchNumber",
  pb.quantity_on_hand AS "quantityOnHand",
  COALESCE(p.cost, 0) AS "unitCost",
  (pb.quantity_on_hand * COALESCE(p.cost, 0)) AS "value"
FROM product_batches pb
LEFT JOIN products p
  ON p.company_id = pb.company_id AND p.code = pb.product_code
WHERE pb.company_id = $1
  AND ($2::text IS NULL OR pb.product_code = $2)
ORDER BY pb.product_code, pb.batch_number
LIMIT 10000
"""

CUSTOMER_PERFORMANCE_SQL = """
SELECT
  si.customer_id AS "customerId",
  c.code AS "customerCode",
  c.name AS "customerName",
  COALESCE(SUM(si.total_amount), 0) AS "totalSales"
FROM sales_invoices si
LEFT JOIN customers c ON c.id = si.customer_id AND c.company_id = si.company_id
WHERE si.company_id = $1
  AND ($2::text IS NULL OR si.status = $2)
  AND ($3::timestamptz IS NULL OR si.invoice_date >= $3::timestamptz)
  AND ($4::timestamptz IS NULL OR si.invoice_date <= $4::timestamptz)
GROUP BY si.customer_id, c.code, c.name
HAVING COALESCE(SUM(si.total_amount), 0) > 0
ORDER BY 4 DESC
"""

BANK_CASH_FLOW_MONTHLY_SQL = """
SELECT
  month,
  SUM(inflow) AS "inflow",
  SUM(outflow) AS "outflow"
FROM (
  SELECT
    to_char(br.receipt_date, 'YYYY-MM') AS month,
    br.total_amount AS inflow,
    0::numeric AS outflow
  FROM bank_receipts br
  WHERE br.company_id = $1
    AND ($2::timestamptz IS NULL OR br.receipt_date >= $2::timestamptz)
    AND ($3::timestamptz IS NULL OR br.receipt_date <= $3::timestamptz)
  UNION ALL
  SELECT
    to_char(bp.payment_date, 'YYYY-MM'),
    0::numeric,
    bp.total_amount
  FROM bank_payments bp
  WHERE bp.company_id = $1
    AND ($2::timestamptz IS NULL OR bp.payment_date >= $2::timestamptz)
    AND ($3::timestamptz IS NULL OR bp.payment_date <= $3::timestamptz)
) flows
GROUP BY month
ORDER BY month
"""

ASSEMBLY_JOB_LINE_COSTS_SQL = """
SELECT
  ajl.job_id AS "jobId",
  SUM(ajl.quantity * ajl.unit_cost) AS "totalComponentCost"
FROM assembly_job_lines ajl
WHERE ajl.job_id = ANY($1::text[])
GROUP BY ajl.job_id
"""

ADVANCED_STOCK_BY_PRODUCT_SQL = """
SELECT
  pb.product_code AS "productCode",
  SUM(pb.quantity_on_hand) AS "quantityOnHand",
  COUNT(*)::int AS "batchCount",
  MIN(pb.expiry_date) AS "nearestExpiry"
FROM product_batches pb
WHERE pb.company_id = $1
  AND ($2::text IS NULL OR pb.product_code = $2)
GROUP BY pb.product_code
ORDER BY pb.product_code
"""

CUSTOMER_SALES_ACTIVITY_SQL = """
SELECT
  si.customer_id AS "customerId",
  MAX(si.customer_code) AS "customerCode",
  MAX(si.customer_name) AS "customerName",
  COUNT(si.id)::int AS "invoiceCount",
  SUM(si.total_amount) AS "totalSales",
  MAX(si.invoice_date) AS "lastInvoiceDate"
FROM sales_invoices si
WHERE si.company_id = $1
  AND ($2::text IS NULL OR si.status = $2)
  AND ($3::timestamptz IS NULL OR si.invoice_date >= $3::timestamptz)
  AND ($4::timestamptz IS NULL OR si.invoice_date <= $4::timestamptz)
GROUP BY si.customer_id
ORDER BY 5 DESC
"""

SALE_SUMMARY_BY_CUSTOM_FIELD_SQL = """
SELECT
  COALESCE(c.custom_fields ->> $5, '—') AS "fieldValue",
  COUNT(si.id)::int AS "invoiceCount",
  SUM(si.total_amount) AS "totalSales"
FROM sales_invoices si
INNER JOIN customers c ON c.id = si.customer_id AND c.company_id = si.company_id
WHERE si.company_id = $1
  AND ($2::text IS NULL OR si.status = $2)
  AND ($3::timestamptz IS NULL OR si.invoice_date >= $3::timestamptz)
  AND ($4::timestamptz IS NULL OR si.invoice_date <= $4::timestamptz)
GROUP BY 1
ORDER BY 3 DESC
"""

BUDGET_ACTUAL_BY_NOMINAL_SQL = """
SELECT
  jl.nominal_code AS "nominalCode",
  SUM(jl.debit - jl.credit) AS "actual"
FROM journal_lines jl
INNER JOIN journals j ON j.id = jl.journal_id
WHERE j.company_id = $1
  AND j.status = 'posted'
  AND ($2::timestamptz IS NULL OR j.journal_date >= $2::timestamptz)
  AND ($3::timestamptz IS NULL OR j.journal_date <= $3::timestamptz)
GROUP BY jl.nominal_code
"""

STOCK_MOVEMENT_LINES_SQL = """
SELECT
  sa.id AS "id",
  sa.voucher_number AS "voucherNumber",
  sa.adjustment_date AS "movementDate",
  sal.product_code AS "productCode",
  sal.quantity_delta AS "quantityDelta"
FROM stock_adjustments sa
INNER JOIN stock_adjustment_lines sal ON sal.stock_adjustment_id = sa.id
WHERE sa.company_id = $1
  AND ($2::timestamptz IS NULL OR sa.adjustment_date >= $2::timestamptz)
  AND ($3::timestamptz IS NULL OR sa.adjustment_date <= $3::timestamptz)
  AND ($4::text IS NULL OR sal.product_code = $4)
  AND (
    $5::timestamptz IS NULL
    OR (sa.adjustment_date, sa.id) < ($5::timestamptz, $6::text)
  )
ORDER BY sa.adjustment_date DESC, sa.id DESC, sal.id ASC
LIMIT $7
"""

STOCK_TRANSFER_LINES_SQL = """
SELECT
  st.id AS "id",
  st.voucher_number AS "voucherNumber",
  st.transfer_date AS "transferDate",
  st.from_location_code AS "fromLocationCode",
  st.to_location_code AS "toLocationCode",
  stl.product_code AS "productCode",
  stl.quantity AS "quantity",
  stl.unit_cost AS "unitCost",
  (stl.quantity * stl.unit_cost) AS "lineValue"
FROM stock_transfers st
INNER JOIN stock_transfer_lines stl ON stl.stock_transfer_id = st.id
WHERE st.company_id = $1
  AND ($2::timestamptz IS NULL OR st.transfer_date >= $2::timestamptz)
  AND ($3::timestamptz IS NULL OR st.transfer_date <= $3::timestamptz)
  AND ($4::text IS NULL OR stl.product_code = $4)
  AND (
    $5::timestamptz IS NULL
    OR (st.transfer_date, st.id) < ($5::timestamptz, $6::text)
  )
ORDER BY st.transfer_date DESC, st.id DESC, stl.id ASC
LIMIT $7
"""

ASSEMBLY_TEMPLATE_SUMMARY_SQL = """
SELECT
  t.code AS "code",
  t.name AS "name",
  t.finished_product_code AS "finishedProductCode",
  COUNT(tl.id)::int AS "componentCount"
FROM assembly_templates t
LEFT JOIN assembly_template_lines tl ON tl.template_id = t.id
WHERE t.company_id = $1
  AND t.is_active = true
GROUP BY t.id, t.code, t.name, t.finished_product_code
ORDER BY t.code ASC
LIMIT 500
"""

ASSEMBLY_COMPONENT_DETAIL_SQL = """
SELECT
  aj.id AS "jobId",
  aj.job_date AS "jobDate",
  aj.job_number AS "jobNumber",
  aj.finished_product_code AS "finishedProductCode",
  ajl.component_product_code AS "componentProductCode",
  ajl.quantity AS "quantity",
  ajl.unit_cost AS "unitCost",
  (ajl.quantity * ajl.unit_cost) AS "lineCost"
FROM assembly_jobs aj
INNER JOIN assembly_job_lines ajl ON ajl.job_id = aj.id
WHERE aj.company_id = $1
  AND ($2::timestamptz IS NULL OR aj.job_date >= $2::timestamptz)
  AND ($3::timestamptz IS NULL OR aj.job_date <= $3::timestamptz)
  AND (
    $4::timestamptz IS NULL
    OR (aj.job_date, aj.id) < ($4::timestamptz, $5::text)
  )
ORDER BY aj.job_date DESC, aj.id DESC, ajl.id ASC
LIMIT $6
"""

GRNI_BY_PRODUCT_SQL = """
WITH received AS (
  SELECT
    COALESCE(grnl.product_code, '—') AS product_code,
    SUM(grnl.quantity) AS received_qty
  FROM goods_receipt_note_lines grnl
  INNER JOIN goods_receipt_notes grn ON grn.id = grnl.goods_receipt_note_id
  WHERE grn.company_id = $1
  GROUP BY 1
),
billed AS (
  SELECT
    COALESCE(sbl.product_code, '—') AS product_code,
    SUM(sbl.quantity) AS billed_qty
  FROM supplier_bill_lines sbl
  INNER JOIN supplier_bills sb ON sb.id = sbl.supplier_bill_id
  WHERE sb.company_id = $1
    AND sb.status = 'posted'
  GROUP BY 1
),
merged AS (
  SELECT
    COALESCE(r.product_code, b.product_code) AS product_code,
    COALESCE(r.received_qty, 0) AS received_qty,
    COALESCE(b.billed_qty, 0) AS billed_qty,
    COALESCE(r.received_qty, 0) - COALESCE(b.billed_qty, 0) AS grni_qty
  FROM received r
  FULL OUTER JOIN billed b ON b.product_code = r.product_code
)
SELECT
  m.product_code AS "productCode",
  m.received_qty AS "receivedQty",
  m.billed_qty AS "billedQty",
  m.grni_qty AS "grniQty",
  COALESCE(p.cost, 0) AS "unitCost",
  (m.grni_qty * COALESCE(p.cost, 0)) AS "grniValue"
FROM merged m
LEFT JOIN products p ON p.company_id = $1 AND p.code = m.product_code
WHERE m.grni_qty > 0
ORDER BY m.product_code
"""
