"""Multi-UOM price tiers per product — P11."""

from __future__ import annotations

from decimal import Decimal

from app.core.exceptions import NotFoundError, ValidationAppError
from prisma_generated import Prisma


class ProductUomService:
    def __init__(self, *, prisma: Prisma) -> None:
        self._db = prisma

    async def list_uoms(self, *, company_id: str, product_id: str) -> list[dict]:
        product = await self._db.product.find_first(
            where={"id": product_id, "companyId": company_id}
        )
        if product is None:
            raise NotFoundError("Product not found")
        rows = await self._db.productuom.find_many(
            where={"companyId": company_id, "productId": product_id},
            order={"unitCode": "asc"},
        )
        if not rows:
            return [
                {
                    "unitCode": product.unit,
                    "conversionFactor": "1",
                    "salePrice": str(product.salePrice),
                    "isDefault": True,
                    "synthetic": True,
                }
            ]
        return [
            {
                "id": r.id,
                "unitCode": r.unitCode,
                "conversionFactor": str(r.conversionFactor),
                "salePrice": str(r.salePrice),
                "isDefault": r.isDefault,
            }
            for r in rows
        ]

    async def upsert_uom(
        self,
        *,
        company_id: str,
        product_id: str,
        unit_code: str,
        conversion_factor: Decimal,
        sale_price: Decimal,
        is_default: bool = False,
    ) -> dict:
        product = await self._db.product.find_first(
            where={"id": product_id, "companyId": company_id}
        )
        if product is None:
            raise NotFoundError("Product not found")
        code = unit_code.strip().upper()
        if not code:
            raise ValidationAppError("unitCode is required")
        if is_default:
            await self._db.productuom.update_many(
                where={"companyId": company_id, "productId": product_id},
                data={"isDefault": False},
            )
            await self._db.product.update(
                where={"id": product_id},
                data={"unit": code, "salePrice": sale_price},
            )
        row = await self._db.productuom.upsert(
            where={
                "companyId_productId_unitCode": {
                    "companyId": company_id,
                    "productId": product_id,
                    "unitCode": code,
                }
            },
            data={
                "create": {
                    "companyId": company_id,
                    "productId": product_id,
                    "unitCode": code,
                    "conversionFactor": conversion_factor,
                    "salePrice": sale_price,
                    "isDefault": is_default,
                },
                "update": {
                    "conversionFactor": conversion_factor,
                    "salePrice": sale_price,
                    "isDefault": is_default,
                },
            },
        )
        return {
            "id": row.id,
            "unitCode": row.unitCode,
            "conversionFactor": str(row.conversionFactor),
            "salePrice": str(row.salePrice),
            "isDefault": row.isDefault,
        }
