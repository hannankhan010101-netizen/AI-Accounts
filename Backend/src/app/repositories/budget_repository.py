"""Budget headers and lines — FA §9.3."""

from __future__ import annotations

from decimal import Decimal

from prisma_generated import Prisma
from prisma_generated.models import Budget


class BudgetRepository:
    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_budgets(self, *, company_id: str) -> list[Budget]:
        return await self._db.budget.find_many(
            where={"companyId": company_id},
            include={"lines": True},
            order={"fiscalYear": "desc"},
        )

    async def get_budget(self, *, company_id: str, budget_id: str) -> Budget | None:
        return await self._db.budget.find_first(
            where={"id": budget_id, "companyId": company_id},
            include={"lines": True},
        )

    async def create_budget(
        self,
        *,
        company_id: str,
        code: str,
        name: str,
        fiscal_year: int,
        lines: list[dict],
    ) -> Budget:
        return await self._db.budget.create(
            data={
                "companyId": company_id,
                "code": code,
                "name": name,
                "fiscalYear": fiscal_year,
                "lines": {
                    "create": [
                        {
                            "nominalCode": ln["nominal_code"],
                            "period": ln.get("period") or "annual",
                            "amount": Decimal(str(ln["amount"])),
                        }
                        for ln in lines
                    ]
                },
            },
            include={"lines": True},
        )

    async def update_budget(
        self,
        *,
        company_id: str,
        budget_id: str,
        name: str | None,
        is_active: bool | None,
    ) -> Budget | None:
        existing = await self.get_budget(company_id=company_id, budget_id=budget_id)
        if existing is None:
            return None
        data: dict = {}
        if name is not None:
            data["name"] = name
        if is_active is not None:
            data["isActive"] = is_active
        if not data:
            return existing
        return await self._db.budget.update(
            where={"id": budget_id},
            data=data,
            include={"lines": True},
        )
