"""P5 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.constants.report_aliases import resolve_report_handler_id
from app.integrations.pral_client import PralClient
from app.services.paypro_service import PayproService


@pytest.mark.asyncio
async def test_openapi_p5_routes_registered() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/payments/paypro/transactions" in paths
    assert "/api/v1/companies/{company_id}/payments/paypro/initiate" in paths
    assert "/api/v1/companies/{company_id}/payments/paypro/webhook" in paths


def test_report_alias_resolves_catalog_ids() -> None:
    assert resolve_report_handler_id("141") == "028"
    assert resolve_report_handler_id("030") == "030"
    assert resolve_report_handler_id("054") == "054"
    assert resolve_report_handler_id("999") == "999"


def test_pral_client_disabled_by_default() -> None:
    client = PralClient()
    assert client.enabled is False


def _paypro_for_signature_tests() -> PayproService:
    return PayproService(
        payment_gateway_repository=None,  # type: ignore[arg-type]
        sales_receipt_repository=None,  # type: ignore[arg-type]
        document_number_service=None,  # type: ignore[arg-type]
        posting_service=None,  # type: ignore[arg-type]
        lock_date_service=None,  # type: ignore[arg-type]
        smart_settings_repository=None,  # type: ignore[arg-type]
        allocation_service=None,  # type: ignore[arg-type]
    )


def test_paypro_webhook_signature_optional_without_secret() -> None:
    svc = _paypro_for_signature_tests()
    assert svc.verify_webhook_signature(body=b"{}", signature=None) is True


def test_paypro_webhook_rejects_missing_signature_when_secret_set(monkeypatch) -> None:
    from app.core.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("PAYPRO_WEBHOOK_SECRET", "test-secret")
    get_settings.cache_clear()

    svc = _paypro_for_signature_tests()
    assert svc.verify_webhook_signature(body=b"{}", signature=None) is False

    get_settings.cache_clear()
    monkeypatch.delenv("PAYPRO_WEBHOOK_SECRET", raising=False)
    get_settings.cache_clear()
