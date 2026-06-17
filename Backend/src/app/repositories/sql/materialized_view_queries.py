"""Read paths against Postgres materialized views (Phase 3)."""

from __future__ import annotations

TRIAL_BALANCE_FROM_MV_SQL = """
SELECT
  mv.nominal_code AS "nominalCode",
  COALESCE(na.name, mv.nominal_code) AS name,
  mv.debit,
  mv.credit,
  mv.balance
FROM mv_nominal_balances mv
LEFT JOIN nominal_accounts na ON na.code = mv.nominal_code
LEFT JOIN coa_sections s ON s.id = na.section_id
LEFT JOIN coa_categories c ON c.id = s.category_id AND c.company_id = mv.company_id
WHERE mv.company_id = $1
ORDER BY mv.nominal_code
"""

AR_AGING_FROM_MV_SQL = """
SELECT
  mv.customer_id AS "customerId",
  c.name AS "customerName",
  c.code AS "customerCode",
  mv.open_balance AS balance,
  mv.oldest_open_date AS "oldestOpenDate",
  mv.open_invoice_count AS "openInvoiceCount"
FROM mv_ar_customer_open mv
LEFT JOIN customers c ON c.id = mv.customer_id AND c.company_id = mv.company_id
WHERE mv.company_id = $1
ORDER BY c.code
"""

AP_AGING_FROM_MV_SQL = """
SELECT
  mv.supplier_id AS "supplierId",
  s.name AS "supplierName",
  s.code AS "supplierCode",
  mv.open_balance AS balance,
  mv.oldest_open_date AS "oldestOpenDate",
  mv.open_bill_count AS "openBillCount"
FROM mv_ap_supplier_open mv
LEFT JOIN suppliers s ON s.id = mv.supplier_id AND s.company_id = mv.company_id
WHERE mv.company_id = $1
ORDER BY s.code
"""

REFRESH_MV_NOMINAL = 'REFRESH MATERIALIZED VIEW CONCURRENTLY "mv_nominal_balances"'
REFRESH_MV_AR = 'REFRESH MATERIALIZED VIEW CONCURRENTLY "mv_ar_customer_open"'
REFRESH_MV_AP = 'REFRESH MATERIALIZED VIEW CONCURRENTLY "mv_ap_supplier_open"'
