"""AR/AP aging SQL using denormalized open balances (Phase 3) + merged CTEs (Step 1)."""

from __future__ import annotations

# Legacy single-purpose queries (kept for reference / MV helpers).
AR_OPEN_BY_CUSTOMER_SQL = """
SELECT
  si.customer_id AS "customerId",
  SUM(si.remaining_amount) AS "openBalance",
  MIN(si.invoice_date) FILTER (WHERE si.remaining_amount > 0) AS "oldestOpenDate",
  COUNT(*) FILTER (WHERE si.remaining_amount > 0)::int AS "openInvoiceCount",
  SUM(si.total_amount) AS "invoicesTotal"
FROM sales_invoices si
WHERE si.company_id = $1
  AND si.status = 'posted'
  AND si.invoice_date <= $2::timestamptz
GROUP BY si.customer_id
HAVING SUM(si.remaining_amount) > 0
   OR SUM(si.total_amount) > 0
"""

AR_RECEIPT_UNALLOCATED_SQL = """
SELECT
  sr.customer_id AS "customerId",
  SUM(sr.total_amount - COALESCE(a.allocated, 0)) AS "unallocatedReceipts"
FROM sales_receipts sr
LEFT JOIN (
  SELECT sales_receipt_id, SUM(amount) AS allocated
  FROM sales_receipt_allocations
  GROUP BY sales_receipt_id
) a ON a.sales_receipt_id = sr.id
WHERE sr.company_id = $1
  AND sr.receipt_date <= $2::timestamptz
GROUP BY sr.customer_id
HAVING SUM(sr.total_amount - COALESCE(a.allocated, 0)) > 0
"""

AP_OPEN_BY_SUPPLIER_SQL = """
SELECT
  sb.supplier_id AS "supplierId",
  SUM(sb.remaining_amount) AS "openBalance",
  MIN(sb.bill_date) FILTER (WHERE sb.remaining_amount > 0) AS "oldestOpenDate",
  COUNT(*) FILTER (WHERE sb.remaining_amount > 0)::int AS "openBillCount",
  SUM(sb.total_amount) AS "billsTotal"
FROM supplier_bills sb
WHERE sb.company_id = $1
  AND sb.status = 'posted'
  AND sb.bill_date <= $2::timestamptz
GROUP BY sb.supplier_id
HAVING SUM(sb.remaining_amount) > 0
   OR SUM(sb.total_amount) > 0
"""

AP_PAYMENT_UNALLOCATED_SQL = """
SELECT
  sp.supplier_id AS "supplierId",
  SUM(sp.total_amount - COALESCE(a.allocated, 0)) AS "unallocatedPayments"
FROM supplier_payments sp
LEFT JOIN (
  SELECT supplier_payment_id, SUM(amount) AS allocated
  FROM supplier_payment_allocations
  GROUP BY supplier_payment_id
) a ON a.supplier_payment_id = sp.id
WHERE sp.company_id = $1
  AND sp.payment_date <= $2::timestamptz
GROUP BY sp.supplier_id
HAVING SUM(sp.total_amount - COALESCE(a.allocated, 0)) > 0
"""

# Step 1 — single round-trip: open invoices + unallocated receipts + customer names.
AR_AGING_MERGED_SQL = """
WITH open AS (
  SELECT
    si.customer_id AS "customerId",
    SUM(si.remaining_amount) AS "openBalance",
    MIN(si.invoice_date) FILTER (WHERE si.remaining_amount > 0) AS "oldestOpenDate",
    COUNT(*) FILTER (WHERE si.remaining_amount > 0)::int AS "openInvoiceCount",
    SUM(si.total_amount) AS "invoicesTotal"
  FROM sales_invoices si
  WHERE si.company_id = $1
    AND si.status = 'posted'
    AND si.invoice_date <= $2::timestamptz
  GROUP BY si.customer_id
  HAVING SUM(si.remaining_amount) > 0
     OR SUM(si.total_amount) > 0
),
unalloc AS (
  SELECT
    sr.customer_id AS "customerId",
    SUM(sr.total_amount - COALESCE(a.allocated, 0)) AS "unallocatedReceipts"
  FROM sales_receipts sr
  LEFT JOIN (
    SELECT sales_receipt_id, SUM(amount) AS allocated
    FROM sales_receipt_allocations
    GROUP BY sales_receipt_id
  ) a ON a.sales_receipt_id = sr.id
  WHERE sr.company_id = $1
    AND sr.receipt_date <= $2::timestamptz
  GROUP BY sr.customer_id
  HAVING SUM(sr.total_amount - COALESCE(a.allocated, 0)) > 0
),
merged AS (
  SELECT
    COALESCE(o."customerId", u."customerId") AS "partyId",
    COALESCE(o."invoicesTotal", 0) AS "invoicesTotal",
    COALESCE(u."unallocatedReceipts", 0) AS "receiptsTotal",
    COALESCE(o."openBalance", 0) - COALESCE(u."unallocatedReceipts", 0) AS remaining,
    o."oldestOpenDate",
    COALESCE(o."openInvoiceCount", 0) AS "openInvoiceCount"
  FROM open o
  FULL OUTER JOIN unalloc u ON u."customerId" = o."customerId"
),
party AS (
  SELECT
    id AS party_id,
    code AS party_code,
    name AS party_name
  FROM customers
  WHERE company_id = $1
)
SELECT
  m."partyId",
  party.party_name AS "partyName",
  party.party_code AS "partyCode",
  m."invoicesTotal",
  m."receiptsTotal",
  m.remaining,
  m."oldestOpenDate",
  m."openInvoiceCount"
FROM merged m
LEFT JOIN party ON party.party_id = m."partyId"
WHERE m.remaining <> 0 OR m."oldestOpenDate" IS NOT NULL
"""

AP_AGING_MERGED_SQL = """
WITH open AS (
  SELECT
    sb.supplier_id AS "supplierId",
    SUM(sb.remaining_amount) AS "openBalance",
    MIN(sb.bill_date) FILTER (WHERE sb.remaining_amount > 0) AS "oldestOpenDate",
    COUNT(*) FILTER (WHERE sb.remaining_amount > 0)::int AS "openBillCount",
    SUM(sb.total_amount) AS "billsTotal"
  FROM supplier_bills sb
  WHERE sb.company_id = $1
    AND sb.status = 'posted'
    AND sb.bill_date <= $2::timestamptz
  GROUP BY sb.supplier_id
  HAVING SUM(sb.remaining_amount) > 0
     OR SUM(sb.total_amount) > 0
),
unalloc AS (
  SELECT
    sp.supplier_id AS "supplierId",
    SUM(sp.total_amount - COALESCE(a.allocated, 0)) AS "unallocatedPayments"
  FROM supplier_payments sp
  LEFT JOIN (
    SELECT supplier_payment_id, SUM(amount) AS allocated
    FROM supplier_payment_allocations
    GROUP BY supplier_payment_id
  ) a ON a.supplier_payment_id = sp.id
  WHERE sp.company_id = $1
    AND sp.payment_date <= $2::timestamptz
  GROUP BY sp.supplier_id
  HAVING SUM(sp.total_amount - COALESCE(a.allocated, 0)) > 0
),
merged AS (
  SELECT
    COALESCE(o."supplierId", u."supplierId") AS "partyId",
    COALESCE(o."billsTotal", 0) AS "invoicesTotal",
    COALESCE(u."unallocatedPayments", 0) AS "receiptsTotal",
    COALESCE(o."openBalance", 0) - COALESCE(u."unallocatedPayments", 0) AS remaining,
    o."oldestOpenDate",
    COALESCE(o."openBillCount", 0) AS "openInvoiceCount"
  FROM open o
  FULL OUTER JOIN unalloc u ON u."supplierId" = o."supplierId"
),
party AS (
  SELECT
    id AS party_id,
    code AS party_code,
    name AS party_name
  FROM suppliers
  WHERE company_id = $1
)
SELECT
  m."partyId",
  party.party_name AS "partyName",
  party.party_code AS "partyCode",
  m."invoicesTotal",
  m."receiptsTotal",
  m.remaining,
  m."oldestOpenDate",
  m."openInvoiceCount"
FROM merged m
LEFT JOIN party ON party.party_id = m."partyId"
WHERE m.remaining <> 0 OR m."oldestOpenDate" IS NOT NULL
"""

# MV fast path: materialized open balances + live unallocated receipts + party names.
AR_AGING_FROM_MV_MERGED_SQL = """
WITH unalloc AS (
  SELECT
    sr.customer_id AS "customerId",
    SUM(sr.total_amount - COALESCE(a.allocated, 0)) AS "unallocatedReceipts"
  FROM sales_receipts sr
  LEFT JOIN (
    SELECT sales_receipt_id, SUM(amount) AS allocated
    FROM sales_receipt_allocations
    GROUP BY sales_receipt_id
  ) a ON a.sales_receipt_id = sr.id
  WHERE sr.company_id = $1
  GROUP BY sr.customer_id
  HAVING SUM(sr.total_amount - COALESCE(a.allocated, 0)) > 0
),
merged AS (
  SELECT
    COALESCE(mv.customer_id, u."customerId") AS "partyId",
    COALESCE(mv.open_balance, 0) AS "openBalance",
    COALESCE(u."unallocatedReceipts", 0) AS "receiptsTotal",
    COALESCE(mv.open_balance, 0) - COALESCE(u."unallocatedReceipts", 0) AS remaining,
    mv.oldest_open_date AS "oldestOpenDate",
    COALESCE(mv.open_invoice_count, 0) AS "openInvoiceCount",
    COALESCE(mv.open_balance, 0) AS "invoicesTotal"
  FROM mv_ar_customer_open mv
  FULL OUTER JOIN unalloc u ON u."customerId" = mv.customer_id
  WHERE mv.company_id = $1 OR u."customerId" IS NOT NULL
)
SELECT
  m."partyId",
  c.name AS "partyName",
  c.code AS "partyCode",
  m."invoicesTotal",
  m."receiptsTotal",
  m.remaining,
  m."oldestOpenDate",
  m."openInvoiceCount"
FROM merged m
LEFT JOIN customers c ON c.id = m."partyId" AND c.company_id = $1
WHERE m.remaining <> 0 OR m."oldestOpenDate" IS NOT NULL
"""

AP_AGING_FROM_MV_MERGED_SQL = """
WITH unalloc AS (
  SELECT
    sp.supplier_id AS "supplierId",
    SUM(sp.total_amount - COALESCE(a.allocated, 0)) AS "unallocatedPayments"
  FROM supplier_payments sp
  LEFT JOIN (
    SELECT supplier_payment_id, SUM(amount) AS allocated
    FROM supplier_payment_allocations
    GROUP BY supplier_payment_id
  ) a ON a.supplier_payment_id = sp.id
  WHERE sp.company_id = $1
  GROUP BY sp.supplier_id
  HAVING SUM(sp.total_amount - COALESCE(a.allocated, 0)) > 0
),
merged AS (
  SELECT
    COALESCE(mv.supplier_id, u."supplierId") AS "partyId",
    COALESCE(mv.open_balance, 0) AS "openBalance",
    COALESCE(u."unallocatedPayments", 0) AS "receiptsTotal",
    COALESCE(mv.open_balance, 0) - COALESCE(u."unallocatedPayments", 0) AS remaining,
    mv.oldest_open_date AS "oldestOpenDate",
    COALESCE(mv.open_bill_count, 0) AS "openInvoiceCount",
    COALESCE(mv.open_balance, 0) AS "invoicesTotal"
  FROM mv_ap_supplier_open mv
  FULL OUTER JOIN unalloc u ON u."supplierId" = mv.supplier_id
  WHERE mv.company_id = $1 OR u."supplierId" IS NOT NULL
)
SELECT
  m."partyId",
  s.name AS "partyName",
  s.code AS "partyCode",
  m."invoicesTotal",
  m."receiptsTotal",
  m.remaining,
  m."oldestOpenDate",
  m."openInvoiceCount"
FROM merged m
LEFT JOIN suppliers s ON s.id = m."partyId" AND s.company_id = $1
WHERE m.remaining <> 0 OR m."oldestOpenDate" IS NOT NULL
"""
