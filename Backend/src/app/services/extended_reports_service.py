"""Sprint 11 — catalog-named operational reports.

Delegates to ``ReportQueryService`` SQL handlers where available (Step 1).
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from app.services.report_query_service import ReportQueryService
from prisma_generated import Prisma


def _criteria(
    *,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    **extra: Any,
) -> dict[str, Any]:
    criteria: dict[str, Any] = dict(extra)
    if date_from:
        criteria["dateFrom"] = date_from.isoformat()
    if date_to:
        criteria["dateTo"] = date_to.isoformat()
    return criteria


def _amount_total(rows: list[dict], field: str = "totalAmount") -> str:
    return str(sum(Decimal(str(r.get(field, 0))) for r in rows))


async def _amount_total_async(rows: list[dict], field: str = "totalAmount") -> str:
    return await asyncio.to_thread(_amount_total, rows, field)


class ExtendedReportsService:
    """Operational-doc roll-up reports — thin wrapper over SQL report handlers."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client
        self._rpt = ReportQueryService(prisma=prisma_client)

    async def _execute(
        self,
        *,
        company_id: str,
        report_id: str,
        criteria: dict[str, Any] | None = None,
    ) -> list[dict]:
        return await self._rpt.execute(
            company_id=company_id,
            report_id=report_id,
            criteria=criteria or {},
        )

    async def sale_invoices_by_date(
        self,
        *,
        company_id: str,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> dict[str, Any]:
        rows = await self._execute(
            company_id=company_id,
            report_id="028",
            criteria=_criteria(date_from=date_from, date_to=date_to, pageSize=10_000),
        )
        amount = await _amount_total_async(rows)
        return {
            "rows": rows,
            "totals": {"amount": amount, "count": len(rows)},
        }

    async def sale_invoices_by_customer(
        self,
        *,
        company_id: str,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> dict[str, Any]:
        rows = await self._execute(
            company_id=company_id,
            report_id="033",
            criteria=_criteria(date_from=date_from, date_to=date_to, pageSize=10_000),
        )
        mapped = [
            {
                "customerId": r.get("customerId"),
                "customerName": None,
                "count": 1,
                "amount": r.get("totalSales"),
            }
            for r in rows
        ]
        amount = await _amount_total_async(mapped, "amount")
        return {
            "rows": mapped,
            "totals": {"amount": amount, "count": len(mapped)},
        }

    async def sale_summary_by_date(
        self,
        *,
        company_id: str,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> dict[str, Any]:
        rows = await self._execute(
            company_id=company_id,
            report_id="032",
            criteria=_criteria(date_from=date_from, date_to=date_to),
        )
        mapped = [
            {
                "date": (r.get("invoiceDate") or "")[:10],
                "count": 1,
                "amount": r.get("totalSales"),
            }
            for r in rows
        ]
        amount = await _amount_total_async(mapped, "amount")
        return {
            "rows": mapped,
            "totals": {"amount": amount, "count": len(mapped)},
        }

    async def customer_performance(
        self,
        *,
        company_id: str,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> dict[str, Any]:
        rows = await self._execute(
            company_id=company_id,
            report_id="182",
            criteria=_criteria(date_from=date_from, date_to=date_to),
        )
        mapped = [
            {
                "customerId": r.get("customerId"),
                "customerName": r.get("customerName"),
                "customerCode": r.get("customerCode"),
                "invoicesCount": 0,
                "invoicesAmount": r.get("totalSales", "0"),
                "receiptsCount": 0,
                "receiptsAmount": "0",
                "outstanding": r.get("totalSales", "0"),
            }
            for r in rows
        ]
        total_inv = await _amount_total_async(mapped, "invoicesAmount")
        return {
            "rows": mapped,
            "totals": {
                "invoicesAmount": total_inv,
                "receiptsAmount": "0",
                "outstanding": total_inv,
            },
        }

    async def customer_balances(
        self,
        *,
        company_id: str,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> dict[str, Any]:
        rows = await self._execute(
            company_id=company_id,
            report_id="047",
            criteria=_criteria(date_from=date_from, date_to=date_to),
        )
        outstanding = await _amount_total_async(rows, "balance")
        return {
            "rows": rows,
            "totals": {"outstanding": outstanding, "partyCount": len(rows)},
        }

    async def purchase_bills_by_date(
        self,
        *,
        company_id: str,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> dict[str, Any]:
        rows = await self._execute(
            company_id=company_id,
            report_id="048",
            criteria=_criteria(date_from=date_from, date_to=date_to, pageSize=10_000),
        )
        amount = await _amount_total_async(rows)
        return {
            "rows": rows,
            "totals": {"amount": amount, "count": len(rows)},
        }

    async def purchase_bills_by_supplier(
        self,
        *,
        company_id: str,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> dict[str, Any]:
        rows = await self._execute(
            company_id=company_id,
            report_id="051",
            criteria=_criteria(date_from=date_from, date_to=date_to, pageSize=10_000),
        )
        mapped = [
            {
                "supplierId": r.get("supplierId"),
                "supplierName": None,
                "count": 1,
                "amount": r.get("totalPurchases"),
            }
            for r in rows
        ]
        amount = await _amount_total_async(mapped, "amount")
        return {
            "rows": mapped,
            "totals": {"amount": amount, "count": len(mapped)},
        }

    async def product_sale_detail(
        self,
        *,
        company_id: str,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> dict[str, Any]:
        rows = await self._execute(
            company_id=company_id,
            report_id="085",
            criteria=_criteria(date_from=date_from, date_to=date_to),
        )
        mapped = [
            {
                "productCode": r.get("productCode"),
                "quantity": "0",
                "amount": r.get("totalSales"),
                "lineCount": 1,
            }
            for r in rows
        ]
        total_amt = await _amount_total_async(rows, "totalSales")
        return {
            "rows": mapped,
            "totals": {"quantity": "0", "amount": total_amt},
        }

    async def product_purchase_detail(
        self,
        *,
        company_id: str,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> dict[str, Any]:
        rows = await self._execute(
            company_id=company_id,
            report_id="087",
            criteria=_criteria(date_from=date_from, date_to=date_to),
        )
        mapped = [
            {
                "productCode": r.get("productCode"),
                "quantity": "0",
                "amount": r.get("totalPurchases"),
                "lineCount": 1,
            }
            for r in rows
        ]
        total_amt = await _amount_total_async(rows, "totalPurchases")
        return {
            "rows": mapped,
            "totals": {"quantity": "0", "amount": total_amt},
        }

    async def stock_quantity(self, *, company_id: str) -> dict[str, Any]:
        rows = await self._execute(company_id=company_id, report_id="080", criteria={})
        return {"rows": rows, "totals": {"products": len(rows)}}

    async def out_of_stock(self, *, company_id: str) -> dict[str, Any]:
        rows = await self._execute(company_id=company_id, report_id="082", criteria={})
        return {"rows": rows, "totals": {"products": len(rows)}}

    async def bank_payments_report(
        self,
        *,
        company_id: str,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> dict[str, Any]:
        rows = await self._execute(
            company_id=company_id,
            report_id="071",
            criteria=_criteria(date_from=date_from, date_to=date_to, pageSize=10_000),
        )
        amount = await _amount_total_async(rows, "totalAmount")
        return {
            "rows": rows,
            "totals": {"amount": amount, "count": len(rows)},
        }

    async def advanced_stock_quantity(
        self, *, company_id: str
    ) -> dict[str, Any]:
        rows = await self._execute(company_id=company_id, report_id="175", criteria={})
        return {"rows": rows, "totals": {"products": len(rows)}}

    async def multi_unit_price_list(
        self, *, company_id: str
    ) -> dict[str, Any]:
        rows = await self._execute(company_id=company_id, report_id="181", criteria={})
        return {"rows": rows, "totals": {"products": len(rows)}}

    async def sale_summary_by_field(
        self,
        *,
        company_id: str,
        date_from: datetime | None,
        date_to: datetime | None,
        group_by_field: str = "productCode",
    ) -> dict[str, Any]:
        rows = await self._execute(
            company_id=company_id,
            report_id="185",
            criteria=_criteria(
                date_from=date_from,
                date_to=date_to,
                groupByField=group_by_field,
            ),
        )
        total = await _amount_total_async(rows, "totalSales")
        return {"rows": rows, "totals": {"totalSales": total, "groups": len(rows)}}

    async def customer_field_activity_summary(
        self,
        *,
        company_id: str,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> dict[str, Any]:
        rows = await self._execute(
            company_id=company_id,
            report_id="311",
            criteria=_criteria(date_from=date_from, date_to=date_to),
        )
        total = await _amount_total_async(rows, "totalSales")
        return {
            "rows": rows,
            "totals": {"totalSales": total, "customers": len(rows)},
        }
