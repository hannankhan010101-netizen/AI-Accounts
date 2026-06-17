"""P9 foundation unit tests."""

from __future__ import annotations

import json
import os
import tempfile

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.constants.report_catalog_registry import catalog_coverage
from app.core.rate_limit import RateLimiter, reset_for_tests
from app.services.fbr_service import FbrService


@pytest.mark.asyncio
async def test_openapi_p9_routes_registered() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/reports/catalog-coverage" in paths
    assert "/api/v1/companies/{company_id}/sales-receipts/{receipt_id}/allocate" in paths


def test_fbr_retry_delay_exponential() -> None:
    svc = FbrService(
        fbr_repository=None,  # type: ignore[arg-type]
        sales_invoice_repository=None,  # type: ignore[arg-type]
    )
    assert svc._retry_delay_minutes(1) == 15
    assert svc._retry_delay_minutes(2) == 30
    assert svc._retry_delay_minutes(3) == 60


def test_rate_limiter_blocks_over_limit() -> None:
    reset_for_tests()
    limiter = RateLimiter()
    assert limiter.allow(key="t:1.2.3.4", limit=2, window_seconds=60) is True
    assert limiter.allow(key="t:1.2.3.4", limit=2, window_seconds=60) is True
    assert limiter.allow(key="t:1.2.3.4", limit=2, window_seconds=60) is False


def test_secrets_vault_loads_into_environ(monkeypatch) -> None:
    from app.core.config import get_settings
    from app.core.secrets_resolver import load_vault_into_environ

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump({"TEST_VAULT_SECRET_KEY": "from-vault"}, f)
        path = f.name
    monkeypatch.setenv("SECRETS_VAULT_FILE", path)
    monkeypatch.delenv("TEST_VAULT_SECRET_KEY", raising=False)
    applied = load_vault_into_environ()
    assert applied.get("TEST_VAULT_SECRET_KEY") == "from-vault"
    assert os.environ.get("TEST_VAULT_SECRET_KEY") == "from-vault"
    get_settings.cache_clear()


def test_catalog_coverage_structure() -> None:
    summary = catalog_coverage()
    assert summary["catalogIds"] >= 40
    assert "implementedHandlers" in summary
    assert isinstance(summary["unmappedCatalogIds"], list)
