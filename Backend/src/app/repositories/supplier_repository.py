"""Accounts payable party master."""

from __future__ import annotations

from prisma_generated import Prisma
from prisma_generated.models import Supplier


class SupplierRepository:
    """Supplier list backing purchase documents."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_suppliers(self, *, company_id: str, take: int = 200) -> list[Supplier]:
        """Return suppliers for AP screens."""

        return await self._db.supplier.find_many(
            where={"companyId": company_id},
            order={"name": "asc"},
            take=take,
        )

    async def create_supplier(
        self,
        *,
        company_id: str,
        code: str,
        name: str,
        email: str | None,
        phone: str | None,
    ) -> Supplier:
        """Create a supplier master record."""

        return await self._db.supplier.create(
            data={
                "companyId": company_id,
                "code": code,
                "name": name,
                "email": email,
                "phone": phone,
            },
        )

    async def find_by_code(
        self, *, company_id: str, code: str
    ) -> Supplier | None:
        return await self._db.supplier.find_first(
            where={"companyId": company_id, "code": code}
        )
