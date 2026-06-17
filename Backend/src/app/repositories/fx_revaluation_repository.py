"""FX revaluation run persistence — P4."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from prisma_generated import Prisma
from prisma_generated.models import FxRevaluationRun


class FxRevaluationRepository:
    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_runs(self, *, company_id: str, take: int = 50) -> list[FxRevaluationRun]:
        return await self._db.fxrevaluationrun.find_many(
            where={"companyId": company_id},
            order={"revaluationDate": "desc"},
            take=take,
        )

    async def create_run(
        self,
        *,
        company_id: str,
        revaluation_date: datetime,
        bank_account_id: str,
        foreign_balance: Decimal,
        exchange_rate: Decimal,
        gain_loss_amount: Decimal,
        journal_id: str | None,
    ) -> FxRevaluationRun:
        return await self._db.fxrevaluationrun.create(
            data={
                "companyId": company_id,
                "revaluationDate": revaluation_date,
                "bankAccountId": bank_account_id,
                "foreignBalance": foreign_balance,
                "exchangeRate": exchange_rate,
                "gainLossAmount": gain_loss_amount,
                "journalId": journal_id,
                "status": "posted" if journal_id else "draft",
            }
        )
