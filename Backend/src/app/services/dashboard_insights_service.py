"""Rule-based dashboard insights for command center Row 7."""

from __future__ import annotations

from decimal import Decimal
from typing import Any


def _dec(v: Any) -> Decimal:
    if v is None:
        return Decimal(0)
    if isinstance(v, Decimal):
        return v
    return Decimal(str(v))


def build_insights(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Return deterministic insight cards from a command-center payload."""

    insights: list[dict[str, Any]] = []
    kpis = {k["id"]: k for k in payload.get("executiveKpis") or [] if isinstance(k, dict)}
    overdue = payload.get("overdue") or {}
    inv = payload.get("inventoryCommand") or {}
    buckets = inv.get("bucketCounts") or {}
    cashflow = payload.get("bankCashFlow") or []
    profitability = payload.get("profitability") or {}
    margins = profitability.get("margins") or {}

    revenue_kpi = kpis.get("kpi-revenue") or {}
    rev_change = revenue_kpi.get("changePct")
    if rev_change is not None and float(rev_change) < -10:
        insights.append(
            {
                "id": "declining-sales",
                "severity": "warn",
                "title": "Declining sales",
                "message": f"Revenue is down {abs(float(rev_change)):.1f}% vs the prior period.",
                "actionHref": "/reports/sale-summary-by-date",
                "actionLabel": "View sales report",
            }
        )
    elif rev_change is not None and float(rev_change) > 15:
        insights.append(
            {
                "id": "growth-opportunity",
                "severity": "good",
                "title": "Strong revenue growth",
                "message": f"Revenue grew {float(rev_change):.1f}% vs the prior period.",
                "actionHref": "/dashboard",
                "actionLabel": "Review trends",
            }
        )

    ar_count = int(overdue.get("arCount") or 0)
    ar_amount = _dec(overdue.get("arAmount"))
    if ar_count > 0 or ar_amount > 0:
        insights.append(
            {
                "id": "overdue-receivables",
                "severity": "critical",
                "title": "Overdue receivables",
                "message": f"{ar_count} aged customer balance(s) totalling {ar_amount:.2f}.",
                "actionHref": "/reports/ar-aging",
                "actionLabel": "Review AR aging",
            }
        )

    low_stock = int(buckets.get("lowStock") or 0)
    out_stock = int(buckets.get("outOfStock") or 0)
    if low_stock > 0 or out_stock > 0:
        insights.append(
            {
                "id": "low-inventory",
                "severity": "warn",
                "title": "Inventory attention needed",
                "message": f"{low_stock} low-stock and {out_stock} out-of-stock SKU(s).",
                "actionHref": "/inventory/products",
                "actionLabel": "View products",
            }
        )

    expiring = inv.get("expiringBatches") or {}
    expired_count = int(expiring.get("expired") or 0)
    expiring_soon_count = int(expiring.get("expiringSoon") or 0)
    if expired_count > 0:
        insights.append(
            {
                "id": "expired-batches",
                "severity": "critical",
                "title": "Expired batches on hand",
                "message": (
                    f"{expired_count} batch(es) have passed expiry with stock still on hand."
                ),
                "actionHref": "/inventory/batches?filter=expired",
                "actionLabel": "Review expired batches",
            }
        )
    if expiring_soon_count > 0:
        insights.append(
            {
                "id": "expiring-batches",
                "severity": "warn",
                "title": "Batches expiring soon",
                "message": (
                    f"{expiring_soon_count} batch(es) expire within "
                    f"{int(expiring.get('windowDays') or 30)} days."
                ),
                "actionHref": "/inventory/batches?filter=expiring",
                "actionLabel": "Review batches",
            }
        )

    net_kpi = kpis.get("kpi-net-profit") or {}
    if _dec(net_kpi.get("value")) < 0:
        insights.append(
            {
                "id": "negative-profit",
                "severity": "critical",
                "title": "Negative net profit",
                "message": "Expenses exceed income for the selected period.",
                "actionHref": "/reports/profit-and-loss",
                "actionLabel": "View P&L",
            }
        )

    gross_pct = margins.get("grossPct")
    if gross_pct is not None and float(gross_pct) < 20:
        insights.append(
            {
                "id": "low-margin",
                "severity": "warn",
                "title": "Low gross margin",
                "message": f"Gross margin is {float(gross_pct):.1f}% — review pricing and COGS.",
                "actionHref": "/reports/profit-and-loss",
                "actionLabel": "Analyze margins",
            }
        )

    negative_months = 0
    for row in cashflow[-3:]:
        if _dec(row.get("net")) < 0:
            negative_months += 1
    if negative_months >= 2:
        insights.append(
            {
                "id": "cashflow-risk",
                "severity": "critical",
                "title": "Cashflow risk",
                "message": "Net cash outflow in multiple recent months.",
                "actionHref": "/bank/balances",
                "actionLabel": "Review bank balances",
            }
        )

    expense_rows = profitability.get("expenseBreakdown") or []
    if expense_rows:
        top = expense_rows[0]
        top_pct = float(top.get("pct") or 0)
        if top_pct > 60:
            insights.append(
                {
                    "id": "expense-concentration",
                    "severity": "warn",
                    "title": "Expense concentration",
                    "message": f"{top.get('label')} accounts for {top_pct:.0f}% of expenses.",
                    "actionHref": "/reports/profit-and-loss",
                    "actionLabel": "Review expenses",
                }
            )

    if not insights:
        insights.append(
            {
                "id": "all-clear",
                "severity": "good",
                "title": "Business health stable",
                "message": "No critical alerts for the selected period.",
                "actionHref": "/dashboard",
                "actionLabel": "Explore dashboard",
            }
        )

    return insights
