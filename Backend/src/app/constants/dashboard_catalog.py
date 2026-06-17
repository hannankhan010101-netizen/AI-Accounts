"""FA §10.9 dashboard widget ids — shared defaults for dashboard management."""

from __future__ import annotations

DASHBOARD_WIDGET_CATALOG: tuple[tuple[str, str], ...] = (
    ("ar-summary", "AR summary (aging buckets)"),
    ("ar-top-10", "AR top 10"),
    ("ar-watchlist", "AR watchlist"),
    ("ap-summary", "AP summary (aging buckets)"),
    ("ap-top-10", "AP top 10"),
    ("ap-watchlist", "AP watchlist"),
    ("bank-balances", "Bank balances"),
    ("bank-balances-watchlist", "Bank balances watchlist"),
    ("bank-cash-flow", "Bank cash flow (12 months)"),
    ("bank-cash-flow-watchlist", "Bank cash flow watchlist"),
    ("monthly-bank-balance", "Monthly bank balance"),
    ("monthly-bank-balance-watchlist", "Monthly bank balance watchlist"),
    ("products-inventory", "Products / inventory strip"),
    ("sales-fy", "Sales (financial year)"),
    ("expenses-fy", "Expenses (financial year)"),
    ("pnl-fy", "P&L (financial year)"),
    ("quick-links", "Quick report links"),
)

DEFAULT_DASHBOARD_WIDGETS: list[str] = [wid for wid, _ in DASHBOARD_WIDGET_CATALOG]
