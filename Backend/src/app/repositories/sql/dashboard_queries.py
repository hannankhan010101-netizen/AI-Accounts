"""Dashboard aggregate SQL (Phase 1 performance)."""

from __future__ import annotations

DASHBOARD_SUMMARY_SQL = """
SELECT
  (SELECT COUNT(*)::int FROM customers WHERE company_id = $1) AS customers,
  (SELECT COUNT(*)::int FROM suppliers WHERE company_id = $1) AS suppliers,
  (SELECT COUNT(*)::int FROM products WHERE company_id = $1) AS products,
  (SELECT COUNT(*)::int FROM bank_accounts WHERE company_id = $1) AS "bankAccounts",
  (SELECT COUNT(*)::int FROM journals WHERE company_id = $1) AS journals,
  (SELECT COUNT(*)::int FROM sales_invoices WHERE company_id = $1) AS "salesInvoices",
  (SELECT COUNT(*)::int FROM supplier_bills WHERE company_id = $1) AS "supplierBills",
  (SELECT COUNT(*)::int FROM bank_payments WHERE company_id = $1) AS "bankPayments",
  (
    SELECT COALESCE(SUM(total_amount), 0)
    FROM sales_invoices
    WHERE company_id = $1 AND status = 'posted'
  ) AS "salesAmount",
  (
    SELECT COALESCE(SUM(total_amount), 0)
    FROM supplier_bills
    WHERE company_id = $1 AND status = 'posted'
  ) AS "purchasesAmount",
  (
    SELECT COALESCE(SUM(total_amount), 0)
    FROM bank_payments
    WHERE company_id = $1
  ) AS "bankPaymentsAmount"
"""
