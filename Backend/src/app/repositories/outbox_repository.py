"""Durable outbox for async workers."""



from __future__ import annotations



from datetime import datetime, timedelta, timezone

from typing import Any



from app.core.config import get_settings

from app.repositories.sql import outbox_queries as oq

from prisma_generated import Prisma

from prisma_generated.fields import Json

from prisma_generated.models import OutboxEvent





class OutboxRepository:

    def __init__(self, prisma_client: Prisma) -> None:

        self._db = prisma_client



    async def enqueue(

        self,

        *,

        company_id: str,

        event_type: str,

        payload: dict[str, Any],

    ) -> OutboxEvent:

        return await self._db.outboxevent.create(

            data={

                "companyId": company_id,

                "eventType": event_type,

                "payload": Json(payload),

                "status": "pending",

            }

        )



    async def claim_pending(self, *, limit: int = 20) -> list[OutboxEvent]:

        claimed = await self._db.query_raw(oq.CLAIM_PENDING_SQL, limit)

        if not claimed:

            return []

        ids = [row["id"] for row in claimed]

        return await self._db.outboxevent.find_many(

            where={"id": {"in": ids}},

            order={"createdAt": "asc"},

        )



    async def mark_completed(self, *, event_id: str) -> None:

        await self._db.outboxevent.update(

            where={"id": event_id},

            data={

                "status": "completed",

                "processedAt": datetime.now(timezone.utc),

                "lockedAt": None,

                "nextAttemptAt": None,

            },

        )



    async def mark_failed(self, *, event_id: str, error: str) -> None:

        settings = get_settings()

        max_attempts = max(1, int(getattr(settings, "outbox_max_attempts", 5) or 5))

        base_minutes = max(1, int(getattr(settings, "outbox_retry_base_minutes", 15) or 15))



        event = await self._db.outboxevent.find_unique(where={"id": event_id})

        if event is None:

            return



        truncated = error[:2000]

        if event.attempts >= max_attempts:

            await self._db.outboxevent.update(

                where={"id": event_id},

                data={

                    "status": "failed",

                    "lastError": truncated,

                    "lockedAt": None,

                },

            )

            return



        delay_minutes = base_minutes * (2 ** max(0, event.attempts - 1))

        next_at = datetime.now(timezone.utc) + timedelta(minutes=delay_minutes)

        await self._db.outboxevent.update(

            where={"id": event_id},

            data={

                "status": "pending",

                "lastError": truncated,

                "lockedAt": None,

                "nextAttemptAt": next_at,

            },

        )



    async def count_pending(self) -> int:

        rows = await self._db.query_raw(

            """

            SELECT COUNT(*)::int AS cnt

            FROM outbox_events

            WHERE status = 'pending'

              AND (next_attempt_at IS NULL OR next_attempt_at <= NOW())

            """

        )

        return int(rows[0]["cnt"]) if rows else 0

