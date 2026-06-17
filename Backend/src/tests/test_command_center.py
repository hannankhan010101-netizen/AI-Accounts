"""Tests for dashboard insights and period helpers."""

from __future__ import annotations

from app.services.dashboard_insights_service import build_insights
from app.utils.period_range import resolve_period


def test_resolve_period_fy() -> None:
    start, end, prior_start, _prior_end = resolve_period("fy")
    assert start.month == 1
    assert start.day == 1
    assert end >= start
    assert prior_start.year == start.year - 1


def test_build_insights_declining_sales() -> None:
    payload = {
        "executiveKpis": [{"id": "kpi-revenue", "changePct": -15.0}],
        "overdue": {"arCount": 0, "arAmount": "0"},
        "inventoryCommand": {"bucketCounts": {"lowStock": 0, "outOfStock": 0}},
        "bankCashFlow": [],
        "profitability": {"margins": {"grossPct": 30}, "expenseBreakdown": []},
    }
    insights = build_insights(payload)
    assert any(i["id"] == "declining-sales" for i in insights)


def test_build_insights_all_clear_when_healthy() -> None:
    payload = {
        "executiveKpis": [{"id": "kpi-revenue", "changePct": 5.0, "value": "100"}],
        "overdue": {"arCount": 0, "arAmount": "0"},
        "inventoryCommand": {"bucketCounts": {"lowStock": 0, "outOfStock": 0}},
        "bankCashFlow": [{"net": "100"}],
        "profitability": {
            "margins": {"grossPct": 40},
            "expenseBreakdown": [{"label": "Ops", "pct": 30}],
        },
    }
    insights = build_insights(payload)
    assert any(i["id"] == "all-clear" for i in insights)
