"""Bank receipt (IR) persistence — catalog §4.3."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from prisma_generated import Prisma
from prisma_generated.models import BankReceipt


class BankReceiptRepository:
    """Money-in voucher distinct from customer receipts (refunds, capital, etc.)."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_receipts(self, *, company_id: str, take: int = 50) -> list[BankReceipt]:
        """Recent bank receipts."""

        return await self._db.bankreceipt.find_many(
            where={"companyId": company_id},
            order={"receiptDate": "desc"},
            take=take,
        )

    async def get_receipt(
        self, *, company_id: str, receipt_id: str
    ) -> BankReceipt | None:
        """Return receipt when it belongs to the company."""

        row = await self._db.bankreceipt.find_unique(where={"id": receipt_id})
        if row is None or row.companyId != company_id:
            return None
        return row

    async def create_receipt(
        self,
        *,
        company_id: str,
        voucher_number: str,
        receipt_date: datetime,
        bank_account_id: str,
        total_amount: Decimal,
        nominal_code: str | None = None,
        journal_id: str | None = None,
        custom_fields: dict | None = None,
        receipt_id: str | None = None,
        status: str = "posted",
    ) -> BankReceipt:
        """Insert receipt with optional counterpart nominal + GL journal link."""

        data: dict = {
                "companyId": company_id,
                "voucherNumber": voucher_number,
                "receiptDate": receipt_date,
                "bankAccountId": bank_account_id,
                "totalAmount": total_amount,
                "nominalCode": nominal_code,
                "journalId": journal_id,
                "status": status,
            }
        if receipt_id:
            data["id"] = receipt_id
        if custom_fields:
            data["customFields"] = custom_fields
        return await self._db.bankreceipt.create(
            data=data,
        )

    async def link_receipt_journal(
        self,
        *,
        receipt_id: str,
        journal_id: str,
        status: str = "posted",
    ) -> BankReceipt:
        return await self._db.bankreceipt.update(
            where={"id": receipt_id},
            data={"journalId": journal_id, "status": status},
        )
