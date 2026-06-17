"""P40 — Business Overview dashboard bundle + posted document void routes."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest


@pytest.mark.asyncio
async def test_openapi_dashboard_overview_route() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    overview = "/api/v1/companies/{company_id}/dashboard/overview"
    assert overview in paths
    assert "get" in paths[overview]


@pytest.mark.asyncio
async def test_openapi_posted_document_void_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    base = "/api/v1/companies/{company_id}"
    assert f"{base}/sales-invoices/{{invoice_id}}/void" in paths
    assert "post" in paths[f"{base}/sales-invoices/{{invoice_id}}/void"]
    assert f"{base}/supplier-bills/{{bill_id}}/void" in paths
    assert "post" in paths[f"{base}/supplier-bills/{{bill_id}}/void"]


def test_document_workflow_void_from_posted() -> None:
    from app.domain import document_workflow as wf

    wf.assert_can_transition(current=wf.POSTED, target=wf.VOIDED)
