"""Tenant (company) records and memberships."""

from __future__ import annotations

from prisma_generated import Prisma
from prisma_generated.models import Company, CompanyMembership


class CompanyRepository:
    """Company bootstrap and membership wiring."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def create_company(self, *, name: str) -> Company:
        """Create an empty tenant shell."""

        return await self._db.company.create(data={"name": name})

    async def add_membership(
        self,
        *,
        company_id: str,
        user_id: str,
        is_default: bool,
        role_id: str | None = None,
    ) -> CompanyMembership:
        """Link a user to a company."""

        return await self._db.companymembership.create(
            data={
                "companyId": company_id,
                "userId": user_id,
                "isDefault": is_default,
                "roleId": role_id,
            }
        )

    async def list_companies_for_user(self, *, user_id: str) -> list[Company]:
        """Return all tenants the user may switch into."""

        memberships = await self._db.companymembership.find_many(
            where={"userId": user_id},
            include={"company": True},
        )
        return [m.company for m in memberships if m.company is not None]

    async def get_default_company_id_for_user(self, *, user_id: str) -> str | None:
        """Resolve default membership company id if marked."""

        row = await self._db.companymembership.find_first(
            where={"userId": user_id, "isDefault": True},
        )
        if row:
            return row.companyId
        first = await self._db.companymembership.find_first(where={"userId": user_id})
        return first.companyId if first else None

    async def user_belongs_to_company(self, *, user_id: str, company_id: str) -> bool:
        """Return true if membership exists."""

        row = await self._db.companymembership.find_first(
            where={"userId": user_id, "companyId": company_id},
        )
        return row is not None

    async def get_company_name(self, *, company_id: str) -> str:
        """Display name for transactional emails — P28."""

        row = await self._db.company.find_unique(where={"id": company_id})
        return row.name if row is not None else "Fast Accounts"
