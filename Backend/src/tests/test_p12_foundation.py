"""P12 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.constants.module_permission_matrix import (
    MODULE_PERMISSION_MATRIX,
    PLAN_MODULE_DEFAULTS,
)
from app.constants.report_module_registry import (
    MODULE_REPORT_IDS,
    module_report_coverage,
)
from app.services.custom_field_service import ALLOWED_FIELD_TYPES
from app.services.permission_service import PermissionService


def test_module_report_coverage_p12_ids() -> None:
    summary = module_report_coverage()
    assert summary["unmappedModuleReportIds"] == []
    assert summary["moduleReportIds"] == len(MODULE_REPORT_IDS)


def test_plan_module_defaults_subset() -> None:
    assert "sales" in PLAN_MODULE_DEFAULTS["starter"]
    assert len(PLAN_MODULE_DEFAULTS["pro"]) >= len(PLAN_MODULE_DEFAULTS["starter"])


def test_matrix_covers_all_modules() -> None:
    assert set(MODULE_PERMISSION_MATRIX.keys()) == {
        "sales",
        "purchases",
        "bank",
        "inventory",
        "assembly",
        "projects",
        "financial",
        "fbr",
        "payments",
    }


@pytest.mark.asyncio
async def test_permission_assert_any_allowed_star() -> None:
    svc = PermissionService(membership_repository=None)  # type: ignore[arg-type]

    async def fake_perms(**_kwargs):
        return ["*"]

    svc.permissions_for = fake_perms  # type: ignore[method-assign]
    await svc.assert_any_allowed(
        company_id="c1", user_id="u1", permissions=("sales.invoices.create",)
    )


@pytest.mark.asyncio
async def test_openapi_p12_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/module-access-matrix" in paths
    assert "/api/v1/companies/{company_id}/billing/status" in paths
    assert "/api/v1/companies/{company_id}/billing/webhook" in paths


def test_picklist_field_types() -> None:
    assert "picklist" in ALLOWED_FIELD_TYPES
