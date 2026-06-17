"""P10 foundation unit tests."""

from __future__ import annotations

import json
import os
import tempfile

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.constants.report_catalog_registry import catalog_coverage
from app.constants.report_aliases import resolve_report_handler_id
from app.core.secrets_resolver import bootstrap_secrets, load_vault_into_environ
from app.services.report_query_service import ReportQueryService


def test_catalog_fully_mapped() -> None:
    summary = catalog_coverage()
    assert summary["unmappedCatalogIds"] == []


def test_report_handlers_175_181_185_311() -> None:
    import inspect

    for rid in ("175", "181", "185", "311"):
        assert resolve_report_handler_id(rid) == rid
    source = inspect.getsource(ReportQueryService.execute)
    for rid in ("175", "181", "185", "311"):
        assert f'"{rid}"' in source


def test_bootstrap_secrets_merges_vault(monkeypatch) -> None:
    from app.core.config import get_settings

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump({"P10_TEST_SECRET": "ok"}, f)
        path = f.name
    monkeypatch.setenv("SECRETS_VAULT_FILE", path)
    monkeypatch.delenv("P10_TEST_SECRET", raising=False)
    applied = bootstrap_secrets()
    assert applied.get("P10_TEST_SECRET") == "ok"
    get_settings.cache_clear()


def test_load_vault_still_exported() -> None:
    assert callable(load_vault_into_environ)


@pytest.mark.asyncio
async def test_openapi_p10_report_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/reports/advanced-stock-quantity" in paths
    assert "/api/v1/companies/{company_id}/reports/customer-field-activity" in paths
