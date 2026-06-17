"""Bank payment (EP) orchestration with GL posting + lock-date guard."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from prisma_generated.models import BankPayment

from app.core.exceptions import ValidationAppError
from app.repositories.bank_repository import BankRepository
from app.services.document_number_service import DocumentNumberService
from app.services.lock_date_service import LockDateService
from app.services.posting_service import PostingService


class BankPaymentService:
    """Reserve voucher numbers, enforce lock date, post journal, persist payment."""

    def __init__(
        self,
        *,
        bank_repository: BankRepository,
        document_number_service: DocumentNumberService,
        lock_date_service: LockDateService,
        posting_service: PostingService,
    ) -> None:
        self._banks = bank_repository
        self._numbers = document_number_service
        self._lock_date = lock_date_service
        self._posting = posting_service

    async def create_payment(
        self,
        *,
        company_id: str,
        bank_account_id: str,
        payment_date: datetime,
        total_amount: Decimal,
        nominal_code: str | None = None,
        nominal_lines: list[tuple[str, Decimal]] | None = None,
        custom_fields: dict | None = None,
        payment_id: str | None = None,
        post_gl: bool = True,
    ) -> BankPayment:
        """
        Lock-date guard → reserve voucher → post journal (if nominals available)
        → persist payment with journal link.
        """

        await self._lock_date.assert_not_locked(
            company_id=company_id,
            document_date=payment_date,
            document_label="bank payment",
        )

        if nominal_lines:
            line_total = sum((amt for _, amt in nominal_lines), Decimal(0))
            if line_total != total_amount:
                raise ValidationAppError(
                    "Nominal line amounts must sum to the payment total."
                )

        seq = await self._numbers.reserve_next(company_id=company_id, sequence_key="EP")
        voucher_number = str(seq)

        journal = None
        if post_gl:
            if nominal_lines:
                if sum((amt for _, amt in nominal_lines), Decimal(0)) == total_amount:
                    journal = await self._posting.post_bank_payment_split(
                        company_id=company_id,
                        payment_date=payment_date,
                        voucher_number=voucher_number,
                        bank_account_id=bank_account_id,
                        nominal_lines=nominal_lines,
                    )
            else:
                journal = await self._posting.post_bank_payment(
                    company_id=company_id,
                    payment_date=payment_date,
                    voucher_number=voucher_number,
                    bank_account_id=bank_account_id,
                    counterpart_nominal_code=nominal_code,
                    total_amount=total_amount,
                )

        doc_status = "posted" if journal else "draft"
        return await self._banks.create_payment(
            company_id=company_id,
            bank_account_id=bank_account_id,
            payment_date=payment_date,
            voucher_number=voucher_number,
            total_amount=total_amount,
            nominal_code=nominal_code,
            journal_id=journal.id if journal else None,
            custom_fields=custom_fields,
            payment_id=payment_id,
            status=doc_status,
        )

    async def post_draft_payment(
        self, *, company_id: str, payment_id: str
    ) -> BankPayment:
        """Post GL for a draft bank payment created under Template/Draft."""

        row = await self._banks.get_payment(
            company_id=company_id, payment_id=payment_id
        )
        if row is None:
            raise ValidationAppError("Bank payment not found")
        if row.journalId:
            raise ValidationAppError("Payment is already posted")
        if row.status != "draft":
            raise ValidationAppError("Only draft payments can be posted")

        await self._lock_date.assert_not_locked(
            company_id=company_id,
            document_date=row.paymentDate,
            document_label="bank payment",
        )

        journal = await self._posting.post_bank_payment(
            company_id=company_id,
            payment_date=row.paymentDate,
            voucher_number=row.voucherNumber,
            bank_account_id=row.bankAccountId,
            counterpart_nominal_code=row.nominalCode,
            total_amount=row.totalAmount,
        )
        if journal is None:
            raise ValidationAppError(
                "Could not post: set counterpart nominal and bank account nominal."
            )
        return await self._banks.link_payment_journal(
            payment_id=payment_id,
            journal_id=journal.id,
        )
