"""Dashboard aggregate queries — avoids loading full master/document lists."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from app.repositories.sql import dashboard_queries as dq
from prisma_generated import Prisma


def _as_decimal(value: Any) -> Decimal:
    if value is None:
        return Decimal(0)
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


class DashboardRepository:
    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def summary(self, *, company_id: str) -> dict[str, Any]:
        rows = await self._db.query_raw(dq.DASHBOARD_SUMMARY_SQL, company_id)
        if not rows:
            return {
                "counts": {
                    "customers": 0,
                    "suppliers": 0,
                    "products": 0,
                    "bankAccounts": 0,
                    "journals": 0,
                    "salesInvoices": 0,
                    "supplierBills": 0,
                    "bankPayments": 0,
                },
                "totals": {
                    "salesAmount": "0",
                    "purchasesAmount": "0",
                    "bankPaymentsAmount": "0",
                },
            }
        row = rows[0]
        return {
            "counts": {
                "customers": int(row.get("customers") or 0),
                "suppliers": int(row.get("suppliers") or 0),
                "products": int(row.get("products") or 0),
                "bankAccounts": int(row.get("bankAccounts") or 0),
                "journals": int(row.get("journals") or 0),
                "salesInvoices": int(row.get("salesInvoices") or 0),
                "supplierBills": int(row.get("supplierBills") or 0),
                "bankPayments": int(row.get("bankPayments") or 0),
            },
            "totals": {
                "salesAmount": str(_as_decimal(row.get("salesAmount"))),
                "purchasesAmount": str(_as_decimal(row.get("purchasesAmount"))),
                "bankPaymentsAmount": str(_as_decimal(row.get("bankPaymentsAmount"))),
            },
        }
