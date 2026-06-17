"""Inventory product master."""

from __future__ import annotations

from prisma_generated import Prisma
from prisma_generated.models import Product


class ProductRepository:
    """Product selection for documents and stock."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_products(self, *, company_id: str, take: int = 500) -> list[Product]:
        """Return active catalog slice."""

        return await self._db.product.find_many(
            where={"companyId": company_id, "isArchived": False},
            order={"code": "asc"},
            take=take,
        )

    async def get_by_codes(
        self, *, company_id: str, codes: list[str]
    ) -> list[Product]:
        if not codes:
            return []
        return await self._db.product.find_many(
            where={"companyId": company_id, "code": {"in": codes}},
        )

    async def create_product(
        self,
        *,
        company_id: str,
        code: str,
        name: str,
        is_stock: bool,
    ) -> Product:
        """Create a product master record."""

        return await self._db.product.create(
            data={
                "companyId": company_id,
                "code": code,
                "name": name,
                "isStock": is_stock,
            },
        )
