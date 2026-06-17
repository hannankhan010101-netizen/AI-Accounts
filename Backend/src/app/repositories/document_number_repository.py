"""Atomic document number sequences per company."""

from __future__ import annotations

from prisma_generated import Prisma


class DocumentNumberRepository:
    """Reserve monotonic numbers for voucher types (SI, EP, journal, ...)."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def reserve_next(self, *, company_id: str, sequence_key: str) -> int:
        """
        Return the next issued integer for ``sequence_key`` and persist the counter.

        First allocation starts at **1**. Not fully race-safe without serializable tx;
        upgrade to ``$queryRaw`` or serializable isolation for high concurrency.
        """

        existing = await self._db.documentnumbersequence.find_unique(
            where={"companyId_key": {"companyId": company_id, "key": sequence_key}}
        )
        if existing is None:
            await self._db.documentnumbersequence.create(
                data={
                    "companyId": company_id,
                    "key": sequence_key,
                    "nextValue": 2,
                }
            )
            return 1
        current = existing.nextValue
        await self._db.documentnumbersequence.update(
            where={"id": existing.id},
            data={"nextValue": current + 1},
        )
        return current

    async def peek_next(self, *, company_id: str, sequence_key: str) -> int | None:
        """Return the next value that would be issued, without incrementing."""

        existing = await self._db.documentnumbersequence.find_unique(
            where={"companyId_key": {"companyId": company_id, "key": sequence_key}}
        )
        if existing is None:
            return None
        return existing.nextValue

    async def seed_sequence(
        self, *, company_id: str, sequence_key: str, next_value: int
    ) -> None:
        """Initialize a sequence counter (used by auto-code start serial)."""

        await self._db.documentnumbersequence.create(
            data={
                "companyId": company_id,
                "key": sequence_key,
                "nextValue": next_value,
            }
        )
