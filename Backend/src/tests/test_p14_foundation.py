"""P14 foundation unit tests."""

from __future__ import annotations

import inspect
import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.constants.report_aliases import resolve_report_handler_id
from app.constants.report_assembly_registry import assembly_report_coverage
from app.services.subscription_billing_service import SubscriptionBillingService


def test_assembly_report_aliases() -> None:
    assert resolve_report_handler_id("201") == "ASM_JOB"
    assert resolve_report_handler_id("202") == "ASM_WIP"
    assert resolve_report_handler_id("FIN_PNL_CAT") == "FIN_PNL_CAT"
    summary = assembly_report_coverage()
    assert summary["unmappedAssemblyReportIds"] == []


def test_fin_pnl_cat_handler_present() -> None:
    from app.repositories.journal_repository import JournalRepository
    from app.services.report_query_service import ReportQueryService

    src = inspect.getsource(ReportQueryService._financial_comparative_pnl_by_category)
    assert "monthly_classified_pnl_by_category" in src
    assert "period_count" in src.lower() or "periodCount" in src
    repo_src = inspect.getsource(JournalRepository.monthly_classified_pnl_by_category)
    assert "categoryName" in repo_src


@pytest.mark.asyncio
async def test_checkout_session_stub_mode() -> None:
    from unittest.mock import MagicMock

    billing = SubscriptionBillingService(
        prisma=MagicMock(),
        module_service=MagicMock(),
    )
    result = await billing.create_checkout_session(
        company_id="co_test",
        plan_code="starter",
    )
    assert result["mode"] == "stub"
    assert result["sessionId"].startswith("stub_cs_")


@pytest.mark.asyncio
async def test_openapi_p14_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/billing/checkout-session" in paths
    assert "/api/v1/companies/{company_id}/reports/comparative-pnl-by-category" in paths
