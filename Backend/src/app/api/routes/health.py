"""Process health and observability endpoints."""

from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import PlainTextResponse

from app.core.config import get_settings
from app.core.database import get_prisma_client
from app.core.metrics import get_metrics
from app.models.responses.common import HealthResponse
from app.repositories.outbox_repository import OutboxRepository
from app.services.health_diagnostics_service import HealthDiagnosticsService
from app.services.performance_baseline_service import PerformanceBaselineService

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Liveness probe for orchestrators."""

    return HealthResponse(status="ok")


@router.get("/health/ready", response_model=HealthResponse)
async def health_ready() -> HealthResponse:
    """Readiness: database reachable and outbox backlog within threshold."""

    if os.getenv("SKIP_PRISMA") == "1":
        return HealthResponse(status="ok")

    settings = get_settings()
    prisma = get_prisma_client()
    try:
        await prisma.query_raw("SELECT 1 AS ok")
        pending = await OutboxRepository(prisma).count_pending()
        backlog_max = int(settings.outbox_backlog_max or 10_000)
        if pending > backlog_max:
            raise HTTPException(
                status_code=503,
                detail=f"Outbox backlog too large: {pending} pending events",
            )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database not ready") from exc

    return HealthResponse(status="ok")


@router.get("/health/details")
async def health_details() -> dict:
    """Extended diagnostics for ops (DB, Redis, MVs, catalog coverage, metrics snapshot)."""

    if os.getenv("SKIP_PRISMA") == "1":
        return {"status": "ok", "skipPrisma": True}

    prisma = get_prisma_client()
    return await HealthDiagnosticsService(prisma=prisma).collect()


@router.get("/health/perf")
async def health_performance() -> dict:
    """Latency percentiles and optional ``pg_stat_statements`` top queries."""

    if os.getenv("SKIP_PRISMA") == "1":
        from app.core.metrics import get_metrics

        return {"httpLatencyMs": get_metrics().latency_percentiles()}

    settings = get_settings()
    prisma = get_prisma_client()
    return await PerformanceBaselineService(prisma=prisma).collect()


@router.get("/metrics")
async def prometheus_metrics() -> Response:
    """Prometheus text exposition (in-process counters/histograms)."""

    settings = get_settings()
    if not settings.metrics_enabled:
        raise HTTPException(status_code=404, detail="Metrics disabled")
    body = get_metrics().render_prometheus()
    return PlainTextResponse(
        content=body,
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )
