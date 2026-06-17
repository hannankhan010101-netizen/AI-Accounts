"""Goods received not invoiced — GRNI report (P3)."""

from __future__ import annotations

from decimal import Decimal

from app.repositories.sql.report_aggregate_queries import GRNI_BY_PRODUCT_SQL
from prisma_generated import Prisma


class GrniService:
    def __init__(self, *, prisma: Prisma) -> None:
        self._db = prisma

    async def report(self, *, company_id: str) -> list[dict]:
        """
        Compare received quantities (GRN lines) vs posted supplier bill lines by product.

        Positive ``grniQty`` means stock received but not yet billed at line level.
        """

        raw = await self._db.query_raw(GRNI_BY_PRODUCT_SQL, company_id)
        return [
            {
                "productCode": row["productCode"],
                "receivedQty": str(row.get("receivedQty") or 0),
                "billedQty": str(row.get("billedQty") or 0),
                "grniQty": str(row.get("grniQty") or 0),
                "unitCost": str(Decimal(str(row.get("unitCost") or 0))),
                "grniValue": str(Decimal(str(row.get("grniValue") or 0))),
            }
            for row in raw
        ]
