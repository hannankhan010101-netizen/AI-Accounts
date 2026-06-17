"""Phase 4 — observability, health diagnostics, COA ETag, SQL sale summary."""

from __future__ import annotations

import os
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("SKIP_PRISMA", "1")

from app.core.metrics import get_metrics, reset_metrics_for_tests
from app.main import create_app
from app.repositories.coa_repository import CoaRepository
from app.services.health_diagnostics_service import HealthDiagnosticsService
from app.services.report_query_service import ReportQueryService


def test_metrics_registry_snapshot() -> None:
    reset_metrics_for_tests()
    metrics = get_metrics()
    metrics.inc("http_requests_total", labels={"method": "GET", "status": "200"})
    metrics.observe("http_request_duration_ms", 42.5, method="GET")
    snap = metrics.snapshot()
    assert snap["counters"]
    assert snap["histograms"]
    prom = metrics.render_prometheus()
    assert "http_requests_total" in prom


def test_coa_tree_etag_stable() -> None:
    assert CoaRepository.tree_etag("rev-1") == CoaRepository.tree_etag("rev-1")
    assert CoaRepository.tree_etag("rev-1") != CoaRepository.tree_etag("rev-2")


@pytest.mark.asyncio
async def test_coa_tree_revision_sql_uses_counts_not_updated_at() -> None:
    db = MagicMock()
    db.query_raw = AsyncMock(return_value=[{"rev": "abc123"}])
    repo = CoaRepository(db)
    rev = await repo.tree_revision_token(company_id="cmp_test")
    assert rev == "abc123"
    sql = db.query_raw.await_args.args[0]
    assert "updated_at" not in sql.lower()
    assert "md5" in sql.lower()
    assert "$1::uuid" not in sql


@pytest.mark.asyncio
async def test_sale_summary_by_date_sql() -> None:
    db = MagicMock()
    db.query_raw = AsyncMock(
        return_value=[
            {"invoiceDate": "2026-01-01", "totalSales": Decimal("150.00")},
        ]
    )
    svc = ReportQueryService(prisma=db)
    rows = await svc._sale_summary_by_date(company_id="co1", criteria={})
    assert rows[0]["totalSales"] == "150.00"
    db.query_raw.assert_awaited_once()


@pytest.mark.asyncio
async def test_health_diagnostics_skip_db_ping() -> None:
    db = MagicMock()
    db.query_raw = AsyncMock(side_effect=[{"ok": 1}, {"ok": 1}, {"ok": 1}, {"ok": 1}])
    with patch(
        "app.services.health_diagnostics_service.OutboxRepository"
    ) as outbox_cls:
        outbox_cls.return_value.count_pending = AsyncMock(return_value=3)
        with patch(
            "app.services.health_diagnostics_service.get_redis",
            AsyncMock(return_value=None),
        ):
            with patch(
                "app.services.health_diagnostics_service.redis_enabled",
                return_value=False,
            ):
                payload = await HealthDiagnosticsService(prisma=db).collect()
    assert payload["outboxPending"] == 3
    assert "reportCatalog" in payload


def test_metrics_endpoint_disabled() -> None:
    app = create_app()
    with patch("app.api.routes.health.get_settings") as gs:
        settings = MagicMock()
        settings.metrics_enabled = False
        gs.return_value = settings
        client = TestClient(app)
        response = client.get("/metrics")
        assert response.status_code == 404


def test_health_details_skip_prisma() -> None:
    app = create_app()
    client = TestClient(app)
    response = client.get("/health/details")
    assert response.status_code == 200
    assert response.json().get("skipPrisma") is True
