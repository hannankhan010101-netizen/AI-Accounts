"""P8 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.constants.report_aliases import resolve_report_handler_id
from app.core.webhook_guard import _parse_allowlist, client_ip


@pytest.mark.asyncio
async def test_openapi_p8_routes_registered() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/fbr/submissions/errors" in paths
    assert "/api/v1/companies/{company_id}/sales-receipts/{receipt_id}" in paths
    assert "/api/v1/companies/{company_id}/sales-invoices/{invoice_id}/fbr/retry" in paths


def test_webhook_allowlist_parsing() -> None:
    assert _parse_allowlist("127.0.0.1, 10.0.0.5") == {"127.0.0.1", "10.0.0.5"}


def test_report_handler_145() -> None:
    assert resolve_report_handler_id("145") == "145"


def test_fbr_event_constant() -> None:
    from app.services.fbr_service import EVENT_FBR_RETRY
    from app.services.outbox_worker_service import EVENT_FBR_RETRY as OUTBOX_FBR

    assert EVENT_FBR_RETRY == OUTBOX_FBR == "fbr.submission.retry"
