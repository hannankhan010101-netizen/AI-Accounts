"""Command center widget catalog and default grid layout."""

from __future__ import annotations

COMMAND_CENTER_WIDGET_CATALOG: tuple[tuple[str, str, str], ...] = (
    ("kpi-cash", "Cash Available", "Executive"),
    ("kpi-bank", "Bank Balance", "Executive"),
    ("kpi-revenue", "Monthly Revenue", "Executive"),
    ("kpi-gross-profit", "Gross Profit", "Executive"),
    ("kpi-net-profit", "Net Profit", "Executive"),
    ("kpi-ar", "Accounts Receivable", "Executive"),
    ("kpi-ap", "Accounts Payable", "Executive"),
    ("kpi-inventory-value", "Inventory Value", "Executive"),
    ("chart-cashflow", "Cashflow Chart", "Cashflow"),
    ("chart-sales-trend", "Sales Trend", "Cashflow"),
    ("health-ar-aging", "AR Aging", "Health"),
    ("health-ap-aging", "AP Aging", "Health"),
    ("health-overdue-invoices", "Overdue Invoices", "Health"),
    ("health-overdue-payments", "Overdue Payments", "Health"),
    ("health-top-customers", "Top Customers", "Health"),
    ("health-top-suppliers", "Top Suppliers", "Health"),
    ("inv-value", "Inventory Value", "Inventory"),
    ("inv-low-stock", "Low Stock Items", "Inventory"),
    ("inv-out-of-stock", "Out of Stock", "Inventory"),
    ("inv-overstock", "Overstocked Items", "Inventory"),
    ("inv-fast-movers", "Fast Moving Products", "Inventory"),
    ("inv-slow-movers", "Slow Moving Products", "Inventory"),
    ("inv-turnover", "Inventory Turnover", "Inventory"),
    ("pnl-snapshot", "P&L Snapshot", "Profitability"),
    ("chart-expense-breakdown", "Expense Breakdown", "Profitability"),
    ("chart-revenue-breakdown", "Revenue Breakdown", "Profitability"),
    ("chart-margin-analysis", "Margin Analysis", "Profitability"),
    ("activity-recent-tx", "Recent Transactions", "Activity"),
    ("activity-invoices", "Latest Invoices", "Activity"),
    ("activity-payments", "Latest Payments", "Activity"),
    ("activity-stock-adj", "Stock Adjustments", "Activity"),
    ("activity-audit", "Audit Activities", "Activity"),
    ("insights-panel", "Alerts & Insights", "Insights"),
)

DEFAULT_COMMAND_CENTER_WIDGETS: list[str] = [wid for wid, _, _ in COMMAND_CENTER_WIDGET_CATALOG]

# react-grid-layout: 12 cols, default positions (x, y, w, h)
DEFAULT_COMMAND_CENTER_LAYOUT: list[dict[str, int | str]] = [
    {"i": "chart-cashflow", "x": 0, "y": 0, "w": 6, "h": 4, "minW": 4, "minH": 3},
    {"i": "chart-sales-trend", "x": 6, "y": 0, "w": 6, "h": 4, "minW": 4, "minH": 3},
    {"i": "health-ar-aging", "x": 0, "y": 4, "w": 4, "h": 3, "minW": 3, "minH": 2},
    {"i": "health-ap-aging", "x": 4, "y": 4, "w": 4, "h": 3, "minW": 3, "minH": 2},
    {"i": "health-overdue-invoices", "x": 8, "y": 4, "w": 2, "h": 3, "minW": 2, "minH": 2},
    {"i": "health-overdue-payments", "x": 10, "y": 4, "w": 2, "h": 3, "minW": 2, "minH": 2},
    {"i": "health-top-customers", "x": 0, "y": 7, "w": 6, "h": 3, "minW": 3, "minH": 2},
    {"i": "health-top-suppliers", "x": 6, "y": 7, "w": 6, "h": 3, "minW": 3, "minH": 2},
    {"i": "inv-value", "x": 0, "y": 10, "w": 3, "h": 3, "minW": 2, "minH": 3},
    {"i": "inv-turnover", "x": 3, "y": 10, "w": 3, "h": 3, "minW": 2, "minH": 3},
    {"i": "inv-low-stock", "x": 6, "y": 10, "w": 3, "h": 3, "minW": 2, "minH": 2},
    {"i": "inv-out-of-stock", "x": 9, "y": 10, "w": 3, "h": 3, "minW": 2, "minH": 2},
    {"i": "inv-overstock", "x": 0, "y": 13, "w": 4, "h": 3, "minW": 2, "minH": 2},
    {"i": "inv-fast-movers", "x": 4, "y": 13, "w": 4, "h": 3, "minW": 2, "minH": 2},
    {"i": "inv-slow-movers", "x": 8, "y": 13, "w": 4, "h": 3, "minW": 2, "minH": 2},
    {"i": "pnl-snapshot", "x": 0, "y": 16, "w": 3, "h": 3, "minW": 2, "minH": 2},
    {"i": "chart-margin-analysis", "x": 3, "y": 16, "w": 3, "h": 3, "minW": 2, "minH": 2},
    {"i": "chart-expense-breakdown", "x": 6, "y": 16, "w": 3, "h": 3, "minW": 2, "minH": 2},
    {"i": "chart-revenue-breakdown", "x": 9, "y": 16, "w": 3, "h": 3, "minW": 2, "minH": 2},
    {"i": "activity-recent-tx", "x": 0, "y": 19, "w": 6, "h": 3, "minW": 3, "minH": 2},
    {"i": "activity-invoices", "x": 6, "y": 19, "w": 3, "h": 3, "minW": 2, "minH": 2},
    {"i": "activity-payments", "x": 9, "y": 19, "w": 3, "h": 3, "minW": 2, "minH": 2},
    {"i": "activity-stock-adj", "x": 0, "y": 22, "w": 6, "h": 3, "minW": 2, "minH": 2},
    {"i": "activity-audit", "x": 6, "y": 22, "w": 6, "h": 3, "minW": 2, "minH": 2},
    {"i": "insights-panel", "x": 0, "y": 25, "w": 12, "h": 3, "minW": 6, "minH": 2},
]

DEFAULT_DASHBOARD_VIEW = {
    "id": "default",
    "name": "Executive",
    "isDefault": True,
    "rolePreset": "owner",
    "layout": DEFAULT_COMMAND_CENTER_LAYOUT,
}

LEGACY_WIDGET_MAP: dict[str, list[str]] = {
    "ar-summary": ["kpi-ar", "health-ar-aging"],
    "ap-summary": ["kpi-ap", "health-ap-aging"],
    "bank-balances": ["kpi-bank", "kpi-cash"],
    "bank-cash-flow": ["chart-cashflow"],
    "sales-fy": ["chart-sales-trend", "kpi-revenue"],
    "expenses-fy": ["chart-expense-breakdown"],
    "pnl-fy": ["pnl-snapshot", "kpi-net-profit", "kpi-gross-profit"],
    "products-inventory": ["inv-value", "inv-low-stock", "inv-out-of-stock"],
    "ar-top-10": ["health-top-customers"],
    "ap-top-10": ["health-top-suppliers"],
    "quick-links": [],
}
