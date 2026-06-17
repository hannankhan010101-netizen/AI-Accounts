"""Bank master and payment shells."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from prisma_generated import Prisma
from prisma_generated.models import BankAccount, BankPayment


class BankRepository:
    """Bank account and EP voucher persistence."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_accounts(self, *, company_id: str) -> list[BankAccount]:
        """Return books for bank module."""

        return await self._db.bankaccount.find_many(
            where={"companyId": company_id},
            order={"name": "asc"},
        )

    async def create_account(
        self,
        *,
        company_id: str,
        name: str,
        nominal_code: str | None,
        currency: str,
    ) -> BankAccount:
        """Create a bank / cash account."""

        return await self._db.bankaccount.create(
            data={
                "companyId": company_id,
                "name": name,
                "nominalCode": nominal_code,
                "currency": currency,
            },
        )

    async def list_payments(self, *, company_id: str, take: int = 50) -> list[BankPayment]:
        """Return recent bank payments."""

        return await self._db.bankpayment.find_many(
            where={"companyId": company_id},
            order={"paymentDate": "desc"},
            take=take,
        )

    async def get_payment(
        self, *, company_id: str, payment_id: str
    ) -> BankPayment | None:
        """Return payment when it belongs to the company."""

        row = await self._db.bankpayment.find_unique(where={"id": payment_id})
        if row is None or row.companyId != company_id:
            return None
        return row

    async def create_payment(
        self,
        *,
        company_id: str,
        bank_account_id: str,
        payment_date: datetime,
        voucher_number: str,
        total_amount: Decimal,
        nominal_code: str | None = None,
        journal_id: str | None = None,
        custom_fields: dict | None = None,
        payment_id: str | None = None,
        status: str = "posted",
    ) -> BankPayment:
        """Insert a single-line bank payment with optional GL journal link."""

        data: dict = {
                "companyId": company_id,
                "bankAccountId": bank_account_id,
                "paymentDate": payment_date,
                "voucherNumber": voucher_number,
                "totalAmount": total_amount,
                "nominalCode": nominal_code,
                "journalId": journal_id,
                "status": status,
            }
        if payment_id:
            data["id"] = payment_id
        if custom_fields:
            data["customFields"] = custom_fields
        return await self._db.bankpayment.create(data=data)

    async def link_payment_journal(
        self,
        *,
        payment_id: str,
        journal_id: str,
        status: str = "posted",
    ) -> BankPayment:
        return await self._db.bankpayment.update(
            where={"id": payment_id},
            data={"journalId": journal_id, "status": status},
        )
