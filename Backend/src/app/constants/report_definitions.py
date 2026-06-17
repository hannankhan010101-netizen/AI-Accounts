"""
Static catalog of report definitions seeded from FAST-ACCOUNTS-FEATURE-CATALOG.md
sections 10.11.1 (Favorites sample), 10.11.2 (Sales and Customer), 10.11.3 (Inventory Products),
and section 10.3 (analytical examples).

Expand with live IDs per docs/PARITY-BACKLOG.md until full parity.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

ReportHub = Literal["standard", "analytical"]


@dataclass(frozen=True, slots=True)
class ReportDefinitionRecord:
    """Single report row for API metadata."""

    report_id: str
    name: str
    category: str
    hub: ReportHub
    filter_schema: dict[str, Any]


def _schema_common() -> dict[str, Any]:
    """Minimal JSON-schema-like hints for runners; refine per report later."""
    return {
        "type": "object",
        "properties": {
            "dateFrom": {"type": "string", "format": "date"},
            "dateTo": {"type": "string", "format": "date"},
            "customerId": {"type": "string"},
            "supplierId": {"type": "string"},
            "productCode": {"type": "string"},
            "status": {"type": "string"},
        },
    }


# --- 10.11.1 Favorites (starred mix) ---
_FAVORITES: tuple[ReportDefinitionRecord, ...] = (
    ReportDefinitionRecord("028", "Sale Invoices/Credits (By Date)", "Favorites", "standard", _schema_common()),
    ReportDefinitionRecord("034", "Customer Statement", "Favorites", "standard", _schema_common()),
    ReportDefinitionRecord("047", "Customers Balances Summary", "Favorites", "standard", _schema_common()),
    ReportDefinitionRecord("141", "Sale Invoices/Credits with Recovery Detail (By Date)", "Favorites", "standard", _schema_common()),
    ReportDefinitionRecord("182", "Customer Performance", "Favorites", "standard", _schema_common()),
    ReportDefinitionRecord("048", "Purchase Bills/Credits (By Date)", "Favorites", "standard", _schema_common()),
    ReportDefinitionRecord("051", "Purchase Bills/Credits Detail (By Supplier)", "Favorites", "standard", _schema_common()),
    ReportDefinitionRecord("054", "Supplier Statement", "Favorites", "standard", _schema_common()),
    ReportDefinitionRecord("067", "Suppliers Balances Summary", "Favorites", "standard", _schema_common()),
    ReportDefinitionRecord("238", "Bills/Credits Detail (By Date/Product/Project)", "Favorites", "standard", _schema_common()),
    ReportDefinitionRecord("071", "Bank Payments", "Favorites", "standard", _schema_common()),
    ReportDefinitionRecord("148", "Stock Valuation", "Favorites", "standard", _schema_common()),
    ReportDefinitionRecord("085", "Product Sale Detail (By Product)", "Favorites", "standard", _schema_common()),
    ReportDefinitionRecord("087", "Product Purchase Detail (By Product)", "Favorites", "standard", _schema_common()),
    ReportDefinitionRecord("162", "Product Performance", "Favorites", "standard", _schema_common()),
)

# --- 10.11.2 Sales → Sales and Customer (complete list from live UI) ---
_SALES_AND_CUSTOMER: tuple[ReportDefinitionRecord, ...] = (
    ReportDefinitionRecord("028", "Sale Invoices/Credits (By Date)", "Sales and Customer", "standard", _schema_common()),
    ReportDefinitionRecord("029", "Sale Invoices/Credits (By Customer)", "Sales and Customer", "standard", _schema_common()),
    ReportDefinitionRecord("030", "Sale Invoices/Credits Details (By Date)", "Sales and Customer", "standard", _schema_common()),
    ReportDefinitionRecord("031", "Sale Invoices/Credits Detail (By Customer)", "Sales and Customer", "standard", _schema_common()),
    ReportDefinitionRecord("032", "Sale Summary (By Date)", "Sales and Customer", "standard", _schema_common()),
    ReportDefinitionRecord("033", "Sale Summary (By Customers)", "Sales and Customer", "standard", _schema_common()),
    ReportDefinitionRecord("034", "Customer Statement", "Sales and Customer", "standard", _schema_common()),
    ReportDefinitionRecord("035", "Customer List", "Sales and Customer", "standard", _schema_common()),
    ReportDefinitionRecord("141", "Sale Invoices/Credits with Recovery Detail (By Date)", "Sales and Customer", "standard", _schema_common()),
    ReportDefinitionRecord("142", "Sale Invoices/Credits with Recovery Detail (By Customer)", "Sales and Customer", "standard", _schema_common()),
    ReportDefinitionRecord("143", "Customer Statement Outstanding Items", "Sales and Customer", "standard", _schema_common()),
    ReportDefinitionRecord("144", "Sale Invoices Statement Detail", "Sales and Customer", "standard", _schema_common()),
    ReportDefinitionRecord("145", "Customer Products", "Sales and Customer", "standard", _schema_common()),
    ReportDefinitionRecord("160", "Customer Statement (Invoice Detail)", "Sales and Customer", "standard", _schema_common()),
    ReportDefinitionRecord("178", "Sale Invoices/Credits Detail (By Customer/Product)", "Sales and Customer", "standard", _schema_common()),
    ReportDefinitionRecord("182", "Customer Performance", "Sales and Customer", "standard", _schema_common()),
    ReportDefinitionRecord("240", "Sales/Credits Detail (By Date/Product/Project)", "Sales and Customer", "standard", _schema_common()),
    ReportDefinitionRecord("241", "Sales/Credits Detail (By Customer/Product/Project)", "Sales and Customer", "standard", _schema_common()),
    ReportDefinitionRecord("243", "Customer Statement (Style One)", "Sales and Customer", "standard", _schema_common()),
    ReportDefinitionRecord("245", "Sales Detail (Statement Style)", "Sales and Customer", "standard", _schema_common()),
    ReportDefinitionRecord("246", "Customer Statement (Style Two)", "Sales and Customer", "standard", _schema_common()),
    ReportDefinitionRecord("311", "Customer Field Activity Summary", "Sales and Customer", "standard", _schema_common()),
)

# --- 10.11.3 Inventory → Products (complete list from live UI) ---
_INVENTORY_PRODUCTS: tuple[ReportDefinitionRecord, ...] = (
    ReportDefinitionRecord("078", "Products List", "Inventory Products", "standard", _schema_common()),
    ReportDefinitionRecord("079", "Price List", "Inventory Products", "standard", _schema_common()),
    ReportDefinitionRecord("080", "Stock Quantity", "Inventory Products", "standard", _schema_common()),
    ReportDefinitionRecord("081", "Product Activity", "Inventory Products", "standard", _schema_common()),
    ReportDefinitionRecord("082", "Out of Stock", "Inventory Products", "standard", _schema_common()),
    ReportDefinitionRecord("083", "Low Stock", "Inventory Products", "standard", _schema_common()),
    ReportDefinitionRecord("084", "Product Sale Detail (By Date)", "Inventory Products", "standard", _schema_common()),
    ReportDefinitionRecord("085", "Product Sale Detail (By Product)", "Inventory Products", "standard", _schema_common()),
    ReportDefinitionRecord("086", "Product Purchase Detail (By Date)", "Inventory Products", "standard", _schema_common()),
    ReportDefinitionRecord("087", "Product Purchase Detail (By Product)", "Inventory Products", "standard", _schema_common()),
    ReportDefinitionRecord("088", "Product Sale Summary", "Inventory Products", "standard", _schema_common()),
    ReportDefinitionRecord("089", "Product Purchase Summary", "Inventory Products", "standard", _schema_common()),
    ReportDefinitionRecord("148", "Stock Valuation", "Inventory Products", "standard", _schema_common()),
    ReportDefinitionRecord("149", "Product Activity Summary", "Inventory Products", "standard", _schema_common()),
    ReportDefinitionRecord("162", "Product Performance", "Inventory Products", "standard", _schema_common()),
    ReportDefinitionRecord("164", "Product Stock (By Location)", "Inventory Products", "standard", _schema_common()),
    ReportDefinitionRecord("173", "Opening Stock", "Inventory Products", "standard", _schema_common()),
    ReportDefinitionRecord("174", "Stock Movement", "Inventory Products", "standard", _schema_common()),
    ReportDefinitionRecord("175", "Advanced Stock Quantity", "Inventory Products", "standard", _schema_common()),
    ReportDefinitionRecord("181", "Multi-Unit Price List", "Inventory Products", "standard", _schema_common()),
    ReportDefinitionRecord("185", "Sale Summary (By Field)", "Inventory Products", "standard", _schema_common()),
    ReportDefinitionRecord("206", "Stock Transfer Detail", "Inventory Products", "standard", _schema_common()),
)

# --- 10.3 analytical examples (numeric IDs) ---
_PURCHASES_AND_SUPPLIERS: tuple[ReportDefinitionRecord, ...] = (
    ReportDefinitionRecord("048", "Purchase Bills/Credits (By Date)", "Purchases and Suppliers", "standard", _schema_common()),
    ReportDefinitionRecord("051", "Purchase Bills/Credits Detail (By Supplier)", "Purchases and Suppliers", "standard", _schema_common()),
    ReportDefinitionRecord("054", "Supplier Statement", "Purchases and Suppliers", "standard", _schema_common()),
    ReportDefinitionRecord("067", "Suppliers Balances Summary", "Purchases and Suppliers", "standard", _schema_common()),
    ReportDefinitionRecord("238", "Bills/Credits Detail (By Date/Product/Project)", "Purchases and Suppliers", "standard", _schema_common()),
    ReportDefinitionRecord("GRNI", "Goods Received Not Invoiced", "Purchases and Suppliers", "standard", _schema_common()),
)

_FINANCIAL: tuple[ReportDefinitionRecord, ...] = (
    ReportDefinitionRecord("TB", "Trial Balance", "Financial", "standard", _schema_common()),
    ReportDefinitionRecord("PNL", "Profit and Loss", "Financial", "standard", _schema_common()),
    ReportDefinitionRecord("BS", "Balance Sheet", "Financial", "standard", _schema_common()),
    ReportDefinitionRecord("GL", "General Ledger", "Financial", "standard", {
        "type": "object",
        "properties": {
            "nominalCode": {"type": "string"},
            "dateFrom": {"type": "string", "format": "date"},
            "dateTo": {"type": "string", "format": "date"},
            "page": {"type": "integer"},
            "pageSize": {"type": "integer"},
        },
        "required": ["nominalCode"],
    }),
)

_BANK: tuple[ReportDefinitionRecord, ...] = (
    ReportDefinitionRecord("071", "Bank Payments", "Bank", "standard", _schema_common()),
    ReportDefinitionRecord("300", "Bank Payment and Receipts Data", "Bank", "analytical", _schema_common()),
    ReportDefinitionRecord("475", "Bank Payment Nominal Summary By Year", "Bank", "analytical", _schema_common()),
    ReportDefinitionRecord("477", "Bank Receipt Nominal Summary By Year", "Bank", "analytical", _schema_common()),
)

_ASSEMBLY: tuple[ReportDefinitionRecord, ...] = (
    ReportDefinitionRecord(
        "ASM_JOB",
        "Job Cost Summary By Finished Product",
        "Assembly",
        "standard",
        _schema_common(),
    ),
    ReportDefinitionRecord(
        "ASM_TPL",
        "Assembly Templates",
        "Assembly",
        "standard",
        _schema_common(),
    ),
)

_PROJECTS: tuple[ReportDefinitionRecord, ...] = (
    ReportDefinitionRecord(
        "PRJ_PAY",
        "Project Payments",
        "Projects",
        "standard",
        _schema_common(),
    ),
)

_BANK_EXTENDED: tuple[ReportDefinitionRecord, ...] = (
    ReportDefinitionRecord(
        "BANK_REC",
        "Bank Receipts",
        "Bank",
        "standard",
        _schema_common(),
    ),
    ReportDefinitionRecord(
        "BANK_XFR",
        "Bank Transfers",
        "Bank",
        "standard",
        _schema_common(),
    ),
    ReportDefinitionRecord(
        "BANK_ACT",
        "Bank Activity Summary",
        "Bank",
        "standard",
        _schema_common(),
    ),
    ReportDefinitionRecord("072", "Bank Receipts", "Bank", "standard", _schema_common()),
    ReportDefinitionRecord("073", "Bank Account Balances", "Bank", "standard", _schema_common()),
    ReportDefinitionRecord("074", "Bank Activity Summary", "Bank", "standard", _schema_common()),
    ReportDefinitionRecord("076", "Bank Transfers", "Bank", "standard", _schema_common()),
    ReportDefinitionRecord("077", "Bank Cash Flow (Monthly)", "Bank", "standard", _schema_common()),
    ReportDefinitionRecord(
        "BANK_BAL",
        "Bank Account Balances",
        "Bank",
        "standard",
        _schema_common(),
    ),
    ReportDefinitionRecord(
        "BANK_CF",
        "Bank Cash Flow (Monthly)",
        "Bank",
        "standard",
        _schema_common(),
    ),
)

_FINANCIAL_EXTENDED: tuple[ReportDefinitionRecord, ...] = (
    ReportDefinitionRecord(
        "FIN_MTB",
        "Monthly Income vs Expense",
        "Financial",
        "standard",
        _schema_common(),
    ),
    ReportDefinitionRecord(
        "BUDGET_VS_ACTUAL",
        "Budget vs Actual",
        "Budget",
        "standard",
        _schema_common(),
    ),
    ReportDefinitionRecord(
        "AR_AGING",
        "Accounts Receivable Aging",
        "Sales and Customer",
        "standard",
        _schema_common(),
    ),
    ReportDefinitionRecord(
        "AP_AGING",
        "Accounts Payable Aging",
        "Purchases and Suppliers",
        "standard",
        _schema_common(),
    ),
    ReportDefinitionRecord(
        "FIN_CMP",
        "Comparative Profit and Loss",
        "Financial",
        "standard",
        _schema_common(),
    ),
    ReportDefinitionRecord(
        "FIN_PNL_CAT",
        "Comparative Profit and Loss by Category",
        "Financial",
        "standard",
        _schema_common(),
    ),
    ReportDefinitionRecord(
        "FIN_TB12",
        "Trial Balance by Month",
        "Financial",
        "standard",
        _schema_common(),
    ),
    ReportDefinitionRecord("203", "Trial Balance", "Financial", "standard", _schema_common()),
    ReportDefinitionRecord("204", "Profit and Loss", "Financial", "standard", _schema_common()),
    ReportDefinitionRecord("205", "Balance Sheet", "Financial", "standard", _schema_common()),
    ReportDefinitionRecord("206", "General Ledger", "Financial", "standard", _schema_common()),
    ReportDefinitionRecord(
        "207",
        "Comparative P&L by Category",
        "Financial",
        "standard",
        _schema_common(),
    ),
    ReportDefinitionRecord(
        "208",
        "Trial Balance by Month",
        "Financial",
        "standard",
        _schema_common(),
    ),
    ReportDefinitionRecord(
        "209",
        "Comparative Profit and Loss",
        "Financial",
        "standard",
        _schema_common(),
    ),
    ReportDefinitionRecord(
        "210",
        "Monthly Income vs Expense",
        "Financial",
        "standard",
        _schema_common(),
    ),
)

_ANALYTICAL_SAMPLES: tuple[ReportDefinitionRecord, ...] = (
    ReportDefinitionRecord("272", "Bills Data", "Favourites", "analytical", _schema_common()),
    ReportDefinitionRecord("300", "Bank Payment and Receipts Data", "Cash and Bank", "analytical", _schema_common()),
    ReportDefinitionRecord("475", "Bank Payment Nominal Summary By Year", "Cash and Bank", "analytical", _schema_common()),
    ReportDefinitionRecord("477", "Bank Receipt Nominal Summary By Year", "Cash and Bank", "analytical", _schema_common()),
)


def all_report_definitions() -> list[ReportDefinitionRecord]:
    """
    Return merged catalog rows.

    Deduplicates by (hub, report_id) so the same numeric ID can appear in Favorites
    and a module list without duplicate API rows for the same hub.
    """

    merged: dict[tuple[str, str], ReportDefinitionRecord] = {}
    for row in (
        *_FAVORITES,
        *_SALES_AND_CUSTOMER,
        *_INVENTORY_PRODUCTS,
        *_PURCHASES_AND_SUPPLIERS,
        *_FINANCIAL,
        *_FINANCIAL_EXTENDED,
        *_BANK,
        *_BANK_EXTENDED,
        *_ASSEMBLY,
        *_PROJECTS,
        *_ANALYTICAL_SAMPLES,
    ):
        merged[(row.hub, row.report_id)] = row
    return list(merged.values())


def favourite_report_ids() -> frozenset[str]:
    """IDs appearing in the Favorites sample (10.11.1) for favouritesOnly filter."""

    return frozenset(r.report_id for r in _FAVORITES)
