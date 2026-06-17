"""Planning document GST lines and journal detail route."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest


@pytest.mark.asyncio
async def test_openapi_supplier_payment_detail_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    detail = "/api/v1/companies/{company_id}/supplier-payments/{payment_id}"
    assert detail in paths
    assert "get" in paths[detail]
    assert "post" in paths[f"{detail}/allocate"]


async def test_openapi_get_journal_route() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    detail = "/api/v1/companies/{company_id}/journals/{journal_id}"
    assert detail in paths
    assert "get" in paths[detail]


def test_sales_credit_create_request_raw_lines() -> None:
    from decimal import Decimal

    from app.models.requests.sales_requests import SalesCreditCreateRequest, SimpleLineRequest

    body = SalesCreditCreateRequest(
        creditDate="2026-05-22T00:00:00Z",
        customerId="cust-1",
        lines=[SimpleLineRequest(productCode="A", quantity=Decimal("1"), rate=Decimal("100"))],
    )
    assert len(body.to_raw_lines()) == 1


def test_quotation_create_request_raw_lines() -> None:
    from decimal import Decimal

    from app.models.requests.sales_requests import QuotationCreateRequest, SimpleLineRequest

    body = QuotationCreateRequest(
        quotationDate="2026-05-22T00:00:00Z",
        customerId="cust-1",
        lines=[
            SimpleLineRequest(
                productCode="SKU1",
                quantity=Decimal("2"),
                rate=Decimal("10"),
                gstCode="GST",
                gstRate=Decimal("15"),
            )
        ],
    )
    raw = body.to_raw_lines()
    assert len(raw) == 1
    assert raw[0]["gstCode"] == "GST"
    assert raw[0]["gstRate"] == Decimal("15")


@pytest.mark.asyncio
async def test_openapi_pdc_detail_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    received = "/api/v1/companies/{company_id}/pdc-received/{cheque_id}"
    issued = "/api/v1/companies/{company_id}/pdc-issued/{cheque_id}"
    assert received in paths
    assert issued in paths
    assert "get" in paths[received]
    assert "get" in paths[issued]
