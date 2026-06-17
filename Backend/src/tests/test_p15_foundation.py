"""P15 foundation unit tests."""

from __future__ import annotations

import inspect
import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.constants.report_aliases import resolve_report_handler_id
from app.constants.report_financial_registry import financial_report_coverage


def test_financial_report_aliases() -> None:
    assert resolve_report_handler_id("203") == "TB"
    assert resolve_report_handler_id("204") == "PNL"
    assert resolve_report_handler_id("FIN_TB12") == "FIN_TB12"
    summary = financial_report_coverage()
    assert summary["unmappedFinancialReportIds"] == []


def test_fin_tb12_handler_present() -> None:
    from app.services.report_query_service import ReportQueryService

    src = inspect.getsource(ReportQueryService._financial_trial_balance_by_month)
    assert "monthly_tb_totals" in src


@pytest.mark.asyncio
async def test_portal_session_stub_mode() -> None:
    from unittest.mock import AsyncMock, MagicMock

    from app.services.subscription_billing_service import SubscriptionBillingService

    prisma = MagicMock()
    prisma.subscriptionrecord.find_unique = AsyncMock(return_value=None)
    billing = SubscriptionBillingService(
        prisma=prisma,
        module_service=MagicMock(),
    )
    result = await billing.create_portal_session(company_id="co_test")
    assert result["mode"] == "stub"


@pytest.mark.asyncio
async def test_openapi_p15_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/billing/portal-session" in paths
    assert (
        "/api/v1/companies/{company_id}/reports/comparative-pnl-by-category/pivot"
        in paths
    )
