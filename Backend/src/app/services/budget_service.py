"""Budget orchestration."""

from __future__ import annotations

from app.models.requests.budget_requests import BudgetLineInput
from app.repositories.budget_repository import BudgetRepository


class BudgetService:
    def __init__(self, *, budget_repository: BudgetRepository) -> None:
        self._repo = budget_repository

    async def list_budgets(self, *, company_id: str):
        return await self._repo.list_budgets(company_id=company_id)

    async def get_budget(self, *, company_id: str, budget_id: str):
        return await self._repo.get_budget(company_id=company_id, budget_id=budget_id)

    async def create_budget(
        self,
        *,
        company_id: str,
        code: str,
        name: str,
        fiscal_year: int,
        lines: list[BudgetLineInput],
    ):
        return await self._repo.create_budget(
            company_id=company_id,
            code=code,
            name=name,
            fiscal_year=fiscal_year,
            lines=[
                {
                    "nominal_code": ln.nominal_code,
                    "period": ln.period,
                    "amount": ln.amount,
                }
                for ln in lines
            ],
        )

    async def update_budget(
        self,
        *,
        company_id: str,
        budget_id: str,
        name: str | None,
        is_active: bool | None,
    ):
        return await self._repo.update_budget(
            company_id=company_id,
            budget_id=budget_id,
            name=name,
            is_active=is_active,
        )
