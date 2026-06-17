"""Sidebar module definitions for FastAccounts export (FAST-ACCOUNTS-FEATURE-CATALOG §2.1)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModuleDef:
    """One export target: sidebar navigation path + metadata."""

    key: str
    label: str
    path: tuple[str, ...]
    critical: bool = False
    category: str = "operational"
    direct_path: str = ""


# direct_path values verified from live FastAccounts sidebar (discover_links.py).
MODULES: tuple[ModuleDef, ...] = (
    ModuleDef("dashboard", "Dashboard", ("Dashboard",), category="overview", direct_path="administrator/control"),
    ModuleDef("bank_account_balances", "Account Balances", ("Bank", "Account Balances"), category="bank", direct_path="index.php/bank/control/bank_accounts"),
    ModuleDef("bank_payments", "Bank Payments", ("Bank", "Bank Payments"), category="bank", direct_path="index.php/bank/control/payments"),
    ModuleDef("bank_receipts", "Bank Receipts", ("Bank", "Bank Receipts"), category="bank", direct_path="index.php/bank/control/ipayments"),
    ModuleDef("bank_transfers", "Transfers", ("Bank", "Transfers"), category="bank", direct_path="index.php/bank/control/transfer"),
    ModuleDef("bank_reconciliation", "Reconciliation", ("Bank", "Reconciliation"), category="bank", direct_path="index.php/bank/control/reconcile_management"),
    ModuleDef("bank_import_statement", "Import Statement", ("Bank", "Import Statement"), category="bank", direct_path="index.php/bank/statementfeed/manage"),
    ModuleDef("sales_invoices", "Invoices", ("Sales", "Invoices"), critical=True, category="sales", direct_path="index.php/income/control/sales_invoice"),
    ModuleDef("sales_receipts", "Receipts", ("Sales", "Receipts"), category="sales", direct_path="index.php/income/control/payments"),
    ModuleDef("pdc_received", "Post Dated Cheque Received", ("Sales", "Post Dated Cheque Received"), category="sales", direct_path="index.php/income/pdcr/management"),
    ModuleDef("sales_all", "Sales All", ("Sales", "Sales All"), category="sales", direct_path="index.php/income/control/all_inv_receipts"),
    ModuleDef("sales_orders", "Orders", ("Sales", "Orders"), category="sales", direct_path="index.php/income/sales/quotations"),
    ModuleDef("customers", "Customers", ("Sales", "Customers"), critical=True, category="sales", direct_path="index.php/income/control/customer_management"),
    ModuleDef("purchase_bills", "Bills", ("Purchases", "Bills"), critical=True, category="purchases", direct_path="index.php/expenses/control/management"),
    ModuleDef("purchase_payments", "Payments", ("Purchases", "Payments"), category="purchases", direct_path="index.php/expenses/control/payments"),
    ModuleDef("pdc_issued", "Post Dated Cheque Issued", ("Purchases", "Post Dated Cheque Issued"), category="purchases", direct_path="index.php/expenses/pdci/management"),
    ModuleDef("purchases_all", "Purchases All", ("Purchases", "Purchases All"), category="purchases", direct_path="index.php/expenses/control/all_bills_payments"),
    ModuleDef("purchase_orders", "PO", ("Purchases", "PO"), category="purchases", direct_path="index.php/po/control/management"),
    ModuleDef("suppliers", "Suppliers", ("Purchases", "Suppliers"), critical=True, category="purchases", direct_path="index.php/expenses/control/supplier_management"),
    ModuleDef("products", "Products", ("Inventory", "Products"), critical=True, category="inventory", direct_path="index.php/products/control/list_management"),
    ModuleDef("stock_adjustment", "Stock Adjustment", ("Inventory", "Stock Adjustment"), category="inventory", direct_path="index.php/stockadjustment/control/management"),
    ModuleDef("stock_transfer", "Stock Transfer", ("Inventory", "Stock Transfer"), category="inventory", direct_path="index.php/stocktransfer/control/management"),
    ModuleDef("reports", "Reports", ("Reports",), category="reports", direct_path="index.php/reports/control"),
    ModuleDef("analytical_reports", "Analytical Reports", ("Analytical Reports",), category="reports", direct_path="index.php/analytical/control"),
)

SETTINGS_MODULES: tuple[ModuleDef, ...] = (
    ModuleDef("settings_business_info", "Business Information", ("Business Information",), category="settings", direct_path="index.php/administrator/control/business_info"),
    ModuleDef("settings_smart_settings", "Smart Settings", ("Smart Settings",), category="settings", direct_path="index.php/administrator/control/invoice_filters"),
    ModuleDef("settings_taxes", "Taxes and Year End", ("Taxes and Year End",), category="settings", direct_path="index.php/administrator/tax_settings/manage_settings"),
    ModuleDef("settings_coa", "Chart of Account", ("Chart of Account",), category="settings", direct_path="index.php/administrator/control/coa_management"),
    ModuleDef("settings_nominals", "Nominal Codes", ("Nominal Codes",), category="settings", direct_path="index.php/administrator/control/coa_management"),
    ModuleDef("settings_journals", "Journals", ("Journals",), category="settings", direct_path="index.php/journal/control/listing"),
    ModuleDef("settings_users", "Users Management", ("Users Management",), category="settings", direct_path="index.php/administrator/control/users_management"),
    ModuleDef("settings_roles", "Roles Management", ("Roles Management",), category="settings", direct_path="index.php/administrator/control/roles_management"),
    ModuleDef("settings_lock_date", "Lock Date", ("Lock Date",), category="settings", direct_path="index.php/administrator/control/lock_date"),
)

CRITICAL_MODULE_KEYS: frozenset[str] = frozenset(
    m.key for m in (*MODULES, *SETTINGS_MODULES) if m.critical
)

ALL_MODULES: tuple[ModuleDef, ...] = (*MODULES, *SETTINGS_MODULES)


def get_modules(filter_keys: set[str] | None = None) -> list[ModuleDef]:
    if not filter_keys:
        return list(MODULES)
    return [m for m in MODULES if m.key in filter_keys]


def get_settings_modules(filter_keys: set[str] | None = None) -> list[ModuleDef]:
    if not filter_keys:
        return list(SETTINGS_MODULES)
    return [m for m in SETTINGS_MODULES if m.key in filter_keys]
