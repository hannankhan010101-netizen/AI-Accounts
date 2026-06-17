"""Report criteria filter helpers — P4 / FA report runner."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

from app.services.report_query_service import ReportQueryService


def test_criteria_status_defaults_to_posted() -> None:
    svc = ReportQueryService(prisma=None)  # type: ignore[arg-type]
    assert svc._criteria_status({}) == "posted"
    assert svc._criteria_status({"status": "draft"}) == "draft"


def test_criteria_status_all_omits_filter() -> None:
    svc = ReportQueryService(prisma=None)  # type: ignore[arg-type]
    assert svc._criteria_status({"status": "all"}) is None
    assert svc._criteria_status({"status": "*"}, default="posted") is None


def test_apply_document_filters_merges_party_and_status() -> None:
    svc = ReportQueryService(prisma=None)  # type: ignore[arg-type]
    where = svc._apply_document_filters(
        {"companyId": "c1"},
        {
            "status": "draft",
            "customerId": "cust-1",
            "supplierId": "sup-1",
        },
    )
    assert where == {
        "companyId": "c1",
        "status": "draft",
        "customerId": "cust-1",
        "supplierId": "sup-1",
    }


def test_paginate_default_page_size_is_200() -> None:
    svc = ReportQueryService(prisma=None)  # type: ignore[arg-type]
    rows = [{"id": str(i)} for i in range(300)]
    sliced = svc._paginate(rows, {})
    assert len(sliced) == 200


def test_inventory_report_aliases_resolve() -> None:
    from app.constants.report_aliases import resolve_report_handler_id

    assert resolve_report_handler_id("206") == "STOCK_XFR"
    assert resolve_report_handler_id("149") == "PROD_ACT"
    assert resolve_report_handler_id("081") == "PROD_ACT"
