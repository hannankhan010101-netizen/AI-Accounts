"""Inventory product master."""

from __future__ import annotations

from decimal import Decimal

from prisma_generated import Prisma
from prisma_generated.models import Product


class ProductRepository:
    """Product selection for documents and stock."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_products(
        self,
        *,
        company_id: str,
        take: int = 500,
        skip: int = 0,
        active_only: bool = True,
    ) -> list[Product]:
        """Return catalog slice."""

        where: dict = {"companyId": company_id}
        if active_only:
            where["isArchived"] = False
        return await self._db.product.find_many(
            where=where,
            order={"code": "asc"},
            take=take,
            skip=skip,
        )

    async def count_products(
        self,
        *,
        company_id: str,
        active_only: bool = True,
    ) -> int:
        where: dict = {"companyId": company_id}
        if active_only:
            where["isArchived"] = False
        return await self._db.product.count(where=where)

    async def get_by_id(self, *, company_id: str, product_id: str) -> Product | None:
        return await self._db.product.find_first(
            where={"id": product_id, "companyId": company_id},
        )

    async def get_by_codes(
        self, *, company_id: str, codes: list[str]
    ) -> list[Product]:
        if not codes:
            return []
        return await self._db.product.find_many(
            where={"companyId": company_id, "code": {"in": codes}},
        )

    async def code_exists(self, *, company_id: str, code: str) -> bool:
        row = await self._db.product.find_first(
            where={"companyId": company_id, "code": code},
        )
        return row is not None

    async def search_products(
        self,
        *,
        company_id: str,
        query: str,
        limit: int = 20,
        active_only: bool = True,
    ) -> list[Product]:
        q = query.strip()
        if not q:
            return []
        where: dict = {
            "companyId": company_id,
            "OR": [
                {"code": {"contains": q, "mode": "insensitive"}},
                {"name": {"contains": q, "mode": "insensitive"}},
                {"category": {"contains": q, "mode": "insensitive"}},
            ],
        }
        if active_only:
            where["isArchived"] = False
        return await self._db.product.find_many(
            where=where,
            order={"code": "asc"},
            take=min(limit, 100),
        )

    async def create_product(
        self,
        *,
        company_id: str,
        code: str,
        name: str,
        is_stock: bool,
        unit: str = "EA",
        category: str | None = None,
        cost: Decimal | float | int | str | None = None,
        sale_price: Decimal | float | int | str | None = None,
        low_stock_level: Decimal | float | int | str | None = None,
        bin_location: str | None = None,
    ) -> Product:
        """Create a product master record."""

        data: dict[str, object] = {
            "companyId": company_id,
            "code": code,
            "name": name,
            "isStock": is_stock,
            "unit": (unit or "EA").strip().upper()[:16] or "EA",
        }
        if category:
            data["category"] = category.strip()[:64]
        if cost is not None:
            data["cost"] = Decimal(str(cost))
        if sale_price is not None:
            data["salePrice"] = Decimal(str(sale_price))
        if low_stock_level is not None:
            data["lowStockLevel"] = Decimal(str(low_stock_level))
        if bin_location:
            data["binLocation"] = bin_location.strip()[:64]
        return await self._db.product.create(data=data)  # type: ignore[arg-type]

    async def update_product(
        self,
        *,
        product_id: str,
        company_id: str,
        data: dict[str, object],
    ) -> Product:
        existing = await self.get_by_id(company_id=company_id, product_id=product_id)
        if existing is None:
            raise ValueError("Product not found")
        return await self._db.product.update(
            where={"id": product_id},
            data=data,  # type: ignore[arg-type]
        )

    async def set_archived(
        self,
        *,
        product_id: str,
        company_id: str,
        archived: bool,
    ) -> Product:
        existing = await self.get_by_id(company_id=company_id, product_id=product_id)
        if existing is None:
            raise ValueError("Product not found")
        return await self._db.product.update(
            where={"id": product_id},
            data={"isArchived": archived},
        )

    async def set_primary_image(
        self,
        *,
        product_id: str,
        company_id: str,
        attachment_id: str | None,
    ) -> Product:
        existing = await self.get_by_id(company_id=company_id, product_id=product_id)
        if existing is None:
            raise ValueError("Product not found")
        return await self._db.product.update(
            where={"id": product_id},
            data={"primaryImageAttachmentId": attachment_id},
        )
