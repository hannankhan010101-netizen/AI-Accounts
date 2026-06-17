#!/usr/bin/env python3
"""Dedicated outbox / background worker (Phase 2).

Run with ``APP_MODE=worker`` and ``OUTBOX_POLL_ENABLED=1``.
API pods should use ``APP_MODE=api`` so they do not poll the outbox in-process.
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("worker")


async def _run() -> None:
    os.environ.setdefault("APP_MODE", "worker")
    os.environ.setdefault("OUTBOX_POLL_ENABLED", "1")

    from app.core.config import get_settings
    from app.core.database import get_prisma_client, get_read_prisma_client
    from app.core.secrets_resolver import bootstrap_secrets
    from app.repositories.audit_log_repository import AuditLogRepository
    from app.repositories.import_job_repository import ImportJobRepository
    from app.repositories.outbox_repository import OutboxRepository
    from app.repositories.report_run_repository import ReportRunRepository
    from app.services.outbox_worker_service import OutboxWorkerService

    bootstrap_secrets()
    settings = get_settings()
    os.environ["DATABASE_URL"] = settings.database_url

    prisma = get_prisma_client()
    await prisma.connect()
    read_prisma = None
    if (settings.database_read_url or "").strip():
        read_prisma = get_read_prisma_client()
        await read_prisma.connect()

    worker = OutboxWorkerService(
        outbox_repository=OutboxRepository(prisma),
        import_job_repository=ImportJobRepository(prisma),
        report_run_repository=ReportRunRepository(prisma),
        audit_log_repository=AuditLogRepository(prisma),
        prisma=prisma,
        read_prisma=read_prisma,
    )

    from app.services.maintenance_service import MaintenanceService
    from app.services.materialized_view_service import MaterializedViewService

    mv = MaterializedViewService(prisma)
    maintenance = MaintenanceService(prisma)
    mv_interval = max(300, int(settings.mv_refresh_interval_seconds or 3600))
    maint_interval = max(3600, int(settings.maintenance_interval_seconds or 86400))
    mv_counter = 0
    maint_counter = 0

    logger.info(
        "Outbox worker started (15s); MV refresh every %ss; maintenance every %ss",
        mv_interval,
        maint_interval,
    )
    try:
        while True:
            try:
                stats = await worker.process_batch(limit=10)
                if stats.get("processed") or stats.get("failed"):
                    logger.info("Outbox batch: %s", stats)
            except Exception:  # noqa: BLE001
                logger.exception("Outbox batch failed")

            mv_counter += 15
            if mv_counter >= mv_interval:
                mv_counter = 0
                try:
                    mv_result = await mv.refresh_all()
                    logger.info("Materialized view refresh: %s", mv_result)
                except Exception:  # noqa: BLE001
                    logger.exception("MV refresh failed")

            if settings.maintenance_enabled:
                maint_counter += 15
                if maint_counter >= maint_interval:
                    maint_counter = 0
                    try:
                        retention = await maintenance.run_retention()
                        logger.info("Maintenance retention: %s", retention)
                    except Exception:  # noqa: BLE001
                        logger.exception("Maintenance retention failed")

            await asyncio.sleep(15)
    finally:
        from app.core.redis_client import close_redis

        await close_redis()
        await prisma.disconnect()
        if read_prisma is not None:
            await read_prisma.disconnect()


def main() -> None:
    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        logger.info("Worker stopped")
        sys.exit(0)


if __name__ == "__main__":
    main()
