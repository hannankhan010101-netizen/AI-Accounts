"""P11 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.constants.module_codes import ALL_MODULE_CODES
from app.constants.report_module_registry import module_report_coverage
from app.services.module_entitlement_service import ModuleEntitlementService


def test_module_report_coverage_full() -> None:
    summary = module_report_coverage()
    assert summary["unmappedModuleReportIds"] == []


def test_all_module_codes_count() -> None:
    assert len(ALL_MODULE_CODES) >= 9


@pytest.mark.asyncio
async def test_openapi_p11_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/module-entitlements" in paths
    assert "/api/v1/companies/{company_id}/custom-field-definitions" in paths
    assert "/api/v1/companies/{company_id}/products/{product_id}/uoms" in paths
    assert "/api/v1/companies/{company_id}/reports/bank-account-balances" in paths


def test_require_module_factory() -> None:
    from app.api.dependencies.deps import require_module

    assert callable(require_module("assembly"))


def test_report_execute_registers_module_handlers() -> None:
    import inspect

    from app.services.report_query_service import ReportQueryService

    src = inspect.getsource(ReportQueryService.execute)
    for rid in ("BANK_BAL", "ASM_JOB", "PRJ_PAY"):
        assert f'"{rid}"' in src
