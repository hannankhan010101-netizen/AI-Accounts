"""Goods issue vouchers linked to posted sales invoices."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from prisma_generated import Prisma
from prisma_generated.models import GoodsIssue


class GoodsIssueRepository:
    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def get_by_invoice(
        self, *, company_id: str, sales_invoice_id: str
    ) -> GoodsIssue | None:
        return await self._db.goodsissue.find_first(
            where={"companyId": company_id, "salesInvoiceId": sales_invoice_id},
            include={"lines": True},
        )

    async def create_issue(
        self,
        *,
        company_id: str,
        voucher_number: str,
        issue_date: datetime,
        sales_invoice_id: str,
        lines: list[dict],
        journal_id: str | None,
    ) -> GoodsIssue:
        return await self._db.goodsissue.create(
            data={
                "companyId": company_id,
                "voucherNumber": voucher_number,
                "issueDate": issue_date,
                "salesInvoiceId": sales_invoice_id,
                "journalId": journal_id,
                "status": "posted" if journal_id else "draft",
                "lines": {"create": lines},
            },
            include={"lines": True},
        )

    async def update_status(
        self,
        *,
        company_id: str,
        goods_issue_id: str,
        status: str,
    ) -> GoodsIssue:
        row = await self._db.goodsissue.find_unique(where={"id": goods_issue_id})
        if row is None or row.companyId != company_id:
            raise ValueError("Goods issue not found")
        return await self._db.goodsissue.update(
            where={"id": goods_issue_id},
            data={"status": status},
            include={"lines": True},
        )

    async def zero_line_quantity(
        self,
        *,
        company_id: str,
        line_id: str,
    ) -> GoodsIssue | None:
        line = await self._db.goodsissueline.find_unique(
            where={"id": line_id},
            include={"goodsIssue": True},
        )
        if line is None or line.goodsIssue.companyId != company_id:
            return None
        await self._db.goodsissueline.update(
            where={"id": line_id},
            data={"quantity": Decimal(0)},
        )
        return await self.get_by_invoice(
            company_id=company_id,
            sales_invoice_id=line.goodsIssue.salesInvoiceId,
        )

    async def update_journal_id(
        self,
        *,
        company_id: str,
        goods_issue_id: str,
        journal_id: str,
    ) -> GoodsIssue:
        row = await self._db.goodsissue.find_unique(where={"id": goods_issue_id})
        if row is None or row.companyId != company_id:
            raise ValueError("Goods issue not found")
        return await self._db.goodsissue.update(
            where={"id": goods_issue_id},
            data={"journalId": journal_id},
            include={"lines": True},
        )
