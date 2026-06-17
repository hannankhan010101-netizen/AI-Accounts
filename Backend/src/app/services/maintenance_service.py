"""Retention and archival for high-volume tables (Phase 3)."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from prisma_generated import Prisma

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class MaintenanceService:
    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def run_retention(self) -> dict[str, int]:
        settings = get_settings()
        outbox_days = max(1, int(settings.outbox_retention_days or 7))
        audit_days = max(30, int(settings.audit_log_retention_days or 365))
        now = datetime.now(timezone.utc)
        outbox_cutoff = now - timedelta(days=outbox_days)
        audit_cutoff = now - timedelta(days=audit_days)

        outbox_deleted = await self._db.execute_raw(
            """
            DELETE FROM outbox_events
            WHERE status = 'completed'
              AND processed_at IS NOT NULL
              AND processed_at < $1
            """,
            outbox_cutoff,
        )
        audit_deleted = await self._db.execute_raw(
            """
            DELETE FROM audit_log_entries
            WHERE created_at < $1
            """,
            audit_cutoff,
        )
        stats = {
            "outboxDeleted": int(outbox_deleted),
            "auditDeleted": int(audit_deleted),
        }
        logger.info("Maintenance retention: %s", stats)
        return stats
