"""P6 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.constants.report_aliases import resolve_report_handler_id
from app.integrations.paypro_client import PayproClient
from app.services.clickhouse_export_service import ClickHouseExportService
from app.services.report_query_service import ReportQueryService


@pytest.mark.asyncio
async def test_openapi_p6_routes_registered() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/reports/runs/{run_id}/export-clickhouse" in paths
    assert "/api/v1/companies/{company_id}/reports/export" in paths


def test_report_alias_supplier_statement_and_gl() -> None:
    assert resolve_report_handler_id("054") == "054"
    assert resolve_report_handler_id("143") == "143"
    assert resolve_report_handler_id("GL") == "GL"


def test_report_alias_chains_product_activity_summary() -> None:
    """149 / 081 → PROD_ACT (product activity summary handler)."""
    assert resolve_report_handler_id("149") == "PROD_ACT"
    assert resolve_report_handler_id("081") == "PROD_ACT"


def test_paypro_client_disabled_by_default() -> None:
    assert PayproClient().enabled is False


def test_clickhouse_export_disabled_without_url() -> None:
    svc = ClickHouseExportService()
    assert svc.enabled is False


def test_report_query_pagination_meta() -> None:
    svc = ReportQueryService(prisma=None)  # type: ignore[arg-type]
    rows = [{"a": 1}, {"a": 2}, {"a": 3}]
    out = svc._paginate(rows, {"page": 2, "pageSize": 1, "includePaginationMeta": True})
    assert out[0]["_meta"]["page"] == 2
    assert out[0]["_meta"]["totalRows"] == 3
    assert len(out) == 2
