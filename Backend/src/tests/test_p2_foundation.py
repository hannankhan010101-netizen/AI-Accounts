"""P2 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.core.exceptions import ValidationAppError
from app.domain import document_workflow as wf
from app.services.pdc_service import PdcService


@pytest.mark.asyncio
async def test_openapi_p2_routes_registered() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/sales-invoices/{invoice_id}/goods-issue" in paths
    assert "/api/v1/companies/{company_id}/pdc-received/{cheque_id}/clear" in paths
    assert "/api/v1/companies/{company_id}/pdc-issued/{cheque_id}/clear" in paths


def test_goods_issue_source_type_defined() -> None:
    assert wf.SOURCE_GOODS_ISSUE == "GOODS_ISSUE"


def test_pdc_invalid_transition_raises() -> None:
    svc = PdcService(
        pdc_received_repository=None,  # type: ignore[arg-type]
        pdc_issued_repository=None,  # type: ignore[arg-type]
        sales_receipt_repository=None,  # type: ignore[arg-type]
        supplier_payment_repository=None,  # type: ignore[arg-type]
        document_number_service=None,  # type: ignore[arg-type]
        lock_date_service=None,  # type: ignore[arg-type]
        posting_service=None,  # type: ignore[arg-type]
        allocation_service=None,  # type: ignore[arg-type]
    )
    with pytest.raises(ValidationAppError):
        svc._assert_transition("cleared", "presented")  # noqa: SLF001
