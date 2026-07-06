"""FastAPI application factory and router registration."""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from app.api.routes import auth, companies, health, tenant
from app.core.config import get_settings
from app.core.config import get_settings as _get_settings
from app.core.database import get_prisma_client, get_read_prisma_client
from app.core.logging_config import configure_logging
from app.core.tracing import setup_tracing
from app.middleware.db_concurrency import db_concurrency_middleware
from app.middleware.observability import observability_middleware

configure_logging()
setup_tracing()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Connect Prisma using ``DATABASE_URL`` from settings, then disconnect."""

    if os.getenv("SKIP_PRISMA") == "1":
        logger.warning("SKIP_PRISMA=1 — database client not connected (tests only)")
        yield
        return

    from app.core.secrets_resolver import bootstrap_secrets

    bootstrap_secrets()
    get_settings.cache_clear()

    settings = get_settings()
    if settings.jwt_secret_key == "dev-secret-change-me-min-32-characters-long":
        logger.warning(
            "JWT_SECRET_KEY is the built-in dev default — tokens are forgeable. "
            "Set JWT_SECRET_KEY before exposing this API."
        )
    os.environ["DATABASE_URL"] = settings.database_url
    prisma = get_prisma_client()
    try:
        await prisma.connect()
    except Exception:
        logger.exception(
            "Prisma could not connect — check DATABASE_URL and that the database is reachable"
        )
        raise
    logger.info("Prisma connected")

    read_prisma = None
    if (_get_settings().database_read_url or "").strip():
        read_prisma = get_read_prisma_client()
        await read_prisma.connect()
        logger.info("Prisma read replica connected")

    app_mode = (settings.app_mode or "all").strip().lower()
    is_api_only = app_mode == "api"
    is_worker_capable = app_mode in {"worker", "all"}

    if is_worker_capable and (_get_settings().clickhouse_url or "").strip():
        from app.services.clickhouse_schema_service import ClickHouseSchemaService

        schema_result = await ClickHouseSchemaService().ensure_schema()
        logger.info("ClickHouse schema ensure: %s", schema_result.get("ok"))

    async def _outbox_poll_loop() -> None:
        from app.repositories.audit_log_repository import AuditLogRepository
        from app.repositories.import_job_repository import ImportJobRepository
        from app.repositories.outbox_repository import OutboxRepository
        from app.repositories.report_run_repository import ReportRunRepository
        from app.services.outbox_worker_service import OutboxWorkerService

        worker = OutboxWorkerService(
            outbox_repository=OutboxRepository(prisma),
            import_job_repository=ImportJobRepository(prisma),
            report_run_repository=ReportRunRepository(prisma),
            audit_log_repository=AuditLogRepository(prisma),
            prisma=prisma,
            read_prisma=read_prisma,
        )
        import asyncio

        while True:
            try:
                await worker.process_batch(limit=10)
            except Exception:  # noqa: BLE001
                logger.exception("Outbox poll failed")
            await asyncio.sleep(15)

    from app.core.redis_client import close_redis

    poll_task = None
    clickhouse_task = None
    fbr_retry_task = None
    warm_task = None
    outbox_default = "0" if is_api_only else "1"
    outbox_enabled = os.getenv("OUTBOX_POLL_ENABLED", outbox_default)
    if outbox_enabled == "1" and is_worker_capable:
        import asyncio

        poll_task = asyncio.create_task(_outbox_poll_loop())
        logger.info("Outbox background poll enabled (15s interval)")

    if is_worker_capable and (_get_settings().clickhouse_url or "").strip():
        import asyncio
        from app.services.clickhouse_sync_service import ClickHouseSyncService

        interval = max(60, int(_get_settings().clickhouse_sync_interval_seconds or 3600))

        async def _clickhouse_sync_loop() -> None:
            sync = ClickHouseSyncService(prisma=prisma)
            while True:
                try:
                    await sync.sync_recent_runs()
                except Exception:  # noqa: BLE001
                    logger.exception("ClickHouse scheduled sync failed")
                await asyncio.sleep(interval)

        clickhouse_task = asyncio.create_task(_clickhouse_sync_loop())
        logger.info("ClickHouse scheduled sync enabled (%ss interval)", interval)

    if is_worker_capable and _get_settings().fbr_retry_enabled:
        import asyncio
        from app.repositories.fbr_repository import FbrRepository
        from app.repositories.outbox_repository import OutboxRepository
        from app.repositories.sales_invoice_repository import SalesInvoiceRepository
        from app.services.fbr_service import FbrService

        async def _fbr_retry_loop() -> None:
            fbr = FbrService(
                fbr_repository=FbrRepository(prisma),
                sales_invoice_repository=SalesInvoiceRepository(prisma),
                outbox_repository=OutboxRepository(prisma),
            )
            while True:
                try:
                    rows = await FbrRepository(prisma).list_due_retries(take=10)
                    for row in rows:
                        try:
                            await fbr.process_retry_event(
                                company_id=row.companyId,
                                sales_invoice_id=row.salesInvoiceId,
                            )
                        except Exception:  # noqa: BLE001
                            logger.exception(
                                "FBR retry failed for invoice %s", row.salesInvoiceId
                            )
                except Exception:  # noqa: BLE001
                    logger.exception("FBR retry loop failed")
                await asyncio.sleep(300)

        fbr_retry_task = asyncio.create_task(_fbr_retry_loop())
        logger.info("FBR retry loop enabled (300s interval)")

    if settings.cache_warm_on_startup and (settings.cache_warm_company_ids or "").strip():
        import asyncio
        from app.services.cache_warmup_service import CacheWarmupService

        async def _cache_warm_loop() -> None:
            warm = CacheWarmupService(prisma=prisma, read_prisma=read_prisma)
            results = await warm.warm_configured_companies()
            logger.info("Startup cache warmup finished: %s", results)

        warm_task = asyncio.create_task(_cache_warm_loop())

    yield

    for task in (poll_task, clickhouse_task, fbr_retry_task, warm_task):
        if task is not None:
            task.cancel()
    await close_redis()
    await prisma.disconnect()
    if read_prisma is not None:
        await read_prisma.disconnect()
    logger.info("Prisma disconnected")


def _expand_cors_origins(origins: list[str]) -> list[str]:
    """Mirror localhost <-> 127.0.0.1 so dev preflight matches the browser URL."""

    expanded: list[str] = []
    seen: set[str] = set()
    for origin in origins:
        for candidate in (origin, origin.replace("://localhost:", "://127.0.0.1:")):
            if candidate and candidate not in seen:
                seen.add(candidate)
                expanded.append(candidate)
    return expanded


def create_app() -> FastAPI:
    """Build FastAPI instance with routes and CORS."""

    settings = get_settings()
    application = FastAPI(title="Fast Accounts API", lifespan=lifespan)
    application.middleware("http")(observability_middleware)
    application.middleware("http")(db_concurrency_middleware)
    application.add_middleware(GZipMiddleware, minimum_size=1000)
    origins = _expand_cors_origins(
        [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    )
    if not origins:
        # A wildcard origin with credentials is invalid (browsers reject it) and
        # unsafe. Refuse to fall back to "*"; block cross-origin until configured.
        logger.warning(
            "CORS_ORIGINS is empty; cross-origin browser requests are blocked. "
            "Set CORS_ORIGINS to your frontend URL(s)."
        )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(health.router)
    application.include_router(auth.router)
    application.include_router(companies.router)
    application.include_router(tenant.router)
    return application


app = create_app()
