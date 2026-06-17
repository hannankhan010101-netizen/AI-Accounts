"""Bank transfer persistence — catalog §4.4."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from prisma_generated import Prisma
from prisma_generated.models import BankTransfer


class BankTransferRepository:
    """Funds between two bank/cash books."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_transfers(self, *, company_id: str, take: int = 50) -> list[BankTransfer]:
        """Recent transfers."""

        return await self._db.banktransfer.find_many(
            where={"companyId": company_id},
            order={"transferDate": "desc"},
            take=take,
        )

    async def get_transfer(
        self, *, company_id: str, transfer_id: str
    ) -> BankTransfer | None:
        """Return transfer when it belongs to the company."""

        row = await self._db.banktransfer.find_unique(where={"id": transfer_id})
        if row is None or row.companyId != company_id:
            return None
        return row

    async def create_transfer(
        self,
        *,
        company_id: str,
        voucher_number: str,
        transfer_date: datetime,
        from_bank_account_id: str,
        to_bank_account_id: str,
        total_amount: Decimal,
        journal_id: str | None = None,
        transfer_id: str | None = None,
        status: str = "posted",
    ) -> BankTransfer:
        """Persist transfer with optional GL journal link."""

        if from_bank_account_id == to_bank_account_id:
            raise ValueError("From and To bank accounts must differ")

        data: dict = {
            "companyId": company_id,
            "voucherNumber": voucher_number,
            "transferDate": transfer_date,
            "fromBankAccountId": from_bank_account_id,
            "toBankAccountId": to_bank_account_id,
            "totalAmount": total_amount,
            "journalId": journal_id,
            "status": status,
        }
        if transfer_id:
            data["id"] = transfer_id
        return await self._db.banktransfer.create(data=data)

    async def link_transfer_journal(
        self,
        *,
        transfer_id: str,
        journal_id: str,
        status: str = "posted",
    ) -> BankTransfer:
        return await self._db.banktransfer.update(
            where={"id": transfer_id},
            data={"journalId": journal_id, "status": status},
        )
