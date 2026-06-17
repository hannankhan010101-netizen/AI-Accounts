"""Bank reconciliation sessions — catalog §4.5."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from prisma_generated import Prisma
from prisma_generated.models import BankReconciliation


class BankReconciliationRepository:
    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_sessions(
        self, *, company_id: str, bank_account_id: str | None = None, take: int = 50
    ) -> list[BankReconciliation]:
        where: dict = {"companyId": company_id}
        if bank_account_id:
            where["bankAccountId"] = bank_account_id
        return await self._db.bankreconciliation.find_many(
            where=where,
            order={"createdAt": "desc"},
            take=take,
            include={"items": True},
        )

    async def get_session(
        self, *, company_id: str, reconciliation_id: str
    ) -> BankReconciliation | None:
        row = await self._db.bankreconciliation.find_unique(
            where={"id": reconciliation_id},
            include={"items": True},
        )
        if row is None or row.companyId != company_id:
            return None
        return row

    async def create_session(
        self,
        *,
        company_id: str,
        bank_account_id: str,
        statement_date: datetime,
        statement_balance: Decimal,
        notes: str | None,
        items: list[dict],
    ) -> BankReconciliation:
        return await self._db.bankreconciliation.create(
            data={
                "companyId": company_id,
                "bankAccountId": bank_account_id,
                "statementDate": statement_date,
                "statementBalance": statement_balance,
                "notes": notes,
                "items": {"create": items},
            },
            include={"items": True},
        )

    async def set_items_cleared(
        self, *, reconciliation_id: str, item_ids: list[str], cleared: bool
    ) -> None:
        if not item_ids:
            return
        await self._db.bankreconciliationitem.update_many(
            where={"id": {"in": item_ids}, "reconciliationId": reconciliation_id},
            data={"isCleared": cleared},
        )

    async def complete_session(
        self, *, reconciliation_id: str, status: str
    ) -> BankReconciliation:
        from datetime import datetime, timezone

        return await self._db.bankreconciliation.update(
            where={"id": reconciliation_id},
            data={
                "status": status,
                "completedAt": datetime.now(timezone.utc),
            },
            include={"items": True},
        )
