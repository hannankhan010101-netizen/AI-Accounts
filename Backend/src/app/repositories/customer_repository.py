"""Accounts receivable party master."""

from __future__ import annotations

from prisma_generated import Prisma
from prisma_generated.models import Customer


class CustomerRepository:
    """Customer CRUD backing sales documents."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_customers(self, *, company_id: str, take: int = 200) -> list[Customer]:
        """Return customers for list screens."""

        return await self._db.customer.find_many(
            where={"companyId": company_id},
            order={"name": "asc"},
            take=take,
        )

    async def get_customer(
        self, *, company_id: str, customer_id: str
    ) -> Customer | None:
        row = await self._db.customer.find_unique(where={"id": customer_id})
        if row is None or row.companyId != company_id:
            return None
        return row

    async def create_customer(
        self,
        *,
        company_id: str,
        code: str,
        name: str,
        email: str | None,
        phone: str | None,
    ) -> Customer:
        """Create a customer master record."""

        return await self._db.customer.create(
            data={
                "companyId": company_id,
                "code": code,
                "name": name,
                "email": email,
                "phone": phone,
            },
        )
