"""Post-dated cheque lifecycle — present, clear, link to bank receipts/payments."""

from __future__ import annotations

from datetime import datetime
from prisma_generated.models import PostDatedChequeIssued, PostDatedChequeReceived

from app.core.exceptions import ValidationAppError
from app.repositories.pdc_repository import PdcIssuedRepository, PdcReceivedRepository
from app.repositories.sales_receipt_repository import SalesReceiptRepository
from app.repositories.supplier_payment_repository import SupplierPaymentRepository
from app.services.allocation_service import AllocationService
from app.services.document_number_service import DocumentNumberService
from app.services.journal_service import JournalService
from app.services.lock_date_service import LockDateService
from app.services.posting_service import PostingService


_ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "pending": {"presented", "cancelled"},
    "presented": {"cleared", "bounced", "cancelled"},
    "cleared": set(),
    "bounced": set(),
    "cancelled": set(),
}


class PdcService:
    def __init__(
        self,
        *,
        pdc_received_repository: PdcReceivedRepository,
        pdc_issued_repository: PdcIssuedRepository,
        sales_receipt_repository: SalesReceiptRepository,
        supplier_payment_repository: SupplierPaymentRepository,
        document_number_service: DocumentNumberService,
        lock_date_service: LockDateService,
        posting_service: PostingService,
        allocation_service: AllocationService,
        journal_service: JournalService | None = None,
    ) -> None:
        self._received = pdc_received_repository
        self._issued = pdc_issued_repository
        self._receipts = sales_receipt_repository
        self._payments = supplier_payment_repository
        self._numbers = document_number_service
        self._lock_date = lock_date_service
        self._posting = posting_service
        self._allocation = allocation_service
        self._journals = journal_service

    def _assert_transition(self, current: str, target: str) -> None:
        allowed = _ALLOWED_TRANSITIONS.get(current, set())
        if target not in allowed:
            raise ValidationAppError(
                f"Cannot move PDC from '{current}' to '{target}'"
            )

    async def present_received(
        self, *, company_id: str, cheque_id: str
    ) -> PostDatedChequeReceived:
        row = await self._received.get_cheque(company_id=company_id, cheque_id=cheque_id)
        if row is None:
            raise ValidationAppError("PDC received not found")
        self._assert_transition(row.status, "presented")
        return await self._received.update_status(
            company_id=company_id, cheque_id=cheque_id, status="presented"
        )

    async def clear_received(
        self,
        *,
        company_id: str,
        cheque_id: str,
        bank_account_id: str,
        clear_date: datetime,
        auto_fifo: bool = True,
    ) -> dict:
        row = await self._received.get_cheque(company_id=company_id, cheque_id=cheque_id)
        if row is None:
            raise ValidationAppError("PDC received not found")
        if row.linkedReceiptId:
            raise ValidationAppError("PDC is already cleared")
        if row.status not in {"pending", "presented"}:
            raise ValidationAppError(
                f"Only pending/presented PDCs can be cleared (current: {row.status})"
            )

        await self._lock_date.assert_not_locked(
            company_id=company_id,
            document_date=clear_date,
            document_label="PDC clear / sales receipt",
        )

        receipt_number = str(
            await self._numbers.reserve_next(company_id=company_id, sequence_key="SR")
        )
        journal = await self._posting.post_sales_receipt(
            company_id=company_id,
            receipt_date=clear_date,
            receipt_number=receipt_number,
            bank_account_id=bank_account_id,
            total_amount=row.amount,
        )
        receipt = await self._receipts.create_receipt(
            company_id=company_id,
            receipt_number=receipt_number,
            receipt_date=clear_date,
            customer_id=row.customerId,
            bank_account_id=bank_account_id,
            total_amount=row.amount,
            journal_id=journal.id if journal else None,
        )
        alloc = await self._allocation.allocate_sales_receipt(
            company_id=company_id,
            receipt_id=receipt.id,
            customer_id=row.customerId,
            receipt_total=row.amount,
            auto_fifo=auto_fifo,
            explicit=None,
        )
        pdc = await self._received.update_status(
            company_id=company_id,
            cheque_id=cheque_id,
            status="cleared",
            linked_receipt_id=receipt.id,
        )
        return {
            "pdc": pdc,
            "salesReceipt": receipt,
            "posted": journal is not None,
            "allocations": alloc.allocations,
        }

    async def present_issued(
        self, *, company_id: str, cheque_id: str
    ) -> PostDatedChequeIssued:
        row = await self._issued.get_cheque(company_id=company_id, cheque_id=cheque_id)
        if row is None:
            raise ValidationAppError("PDC issued not found")
        self._assert_transition(row.status, "presented")
        return await self._issued.update_status(
            company_id=company_id, cheque_id=cheque_id, status="presented"
        )

    async def clear_issued(
        self,
        *,
        company_id: str,
        cheque_id: str,
        clear_date: datetime,
        auto_fifo: bool = True,
    ) -> dict:
        row = await self._issued.get_cheque(company_id=company_id, cheque_id=cheque_id)
        if row is None:
            raise ValidationAppError("PDC issued not found")
        if row.linkedPaymentId:
            raise ValidationAppError("PDC is already cleared")
        if row.status not in {"pending", "presented"}:
            raise ValidationAppError(
                f"Only pending/presented PDCs can be cleared (current: {row.status})"
            )

        await self._lock_date.assert_not_locked(
            company_id=company_id,
            document_date=clear_date,
            document_label="PDC clear / supplier payment",
        )

        voucher_number = str(
            await self._numbers.reserve_next(company_id=company_id, sequence_key="VP")
        )
        journal = await self._posting.post_supplier_payment(
            company_id=company_id,
            payment_date=clear_date,
            voucher_number=voucher_number,
            bank_account_id=row.bankAccountId,
            total_amount=row.amount,
        )
        payment = await self._payments.create_payment(
            company_id=company_id,
            voucher_number=voucher_number,
            payment_date=clear_date,
            supplier_id=row.supplierId,
            bank_account_id=row.bankAccountId,
            total_amount=row.amount,
            journal_id=journal.id if journal else None,
        )
        alloc = await self._allocation.allocate_supplier_payment(
            company_id=company_id,
            payment_id=payment.id,
            supplier_id=row.supplierId,
            payment_total=row.amount,
            auto_fifo=auto_fifo,
            explicit=None,
        )
        pdc = await self._issued.update_status(
            company_id=company_id,
            cheque_id=cheque_id,
            status="cleared",
            linked_payment_id=payment.id,
        )
        return {
            "pdc": pdc,
            "supplierPayment": payment,
            "posted": journal is not None,
            "allocations": alloc.allocations,
        }

    async def bounce_received(
        self,
        *,
        company_id: str,
        cheque_id: str,
        bounce_date: datetime | None = None,
    ) -> PostDatedChequeReceived:
        """Mark PDC bounced; reverse linked receipt when already cleared."""

        row = await self._received.get_cheque(company_id=company_id, cheque_id=cheque_id)
        if row is None:
            raise ValidationAppError("PDC received not found")
        if row.status == "bounced":
            raise ValidationAppError("PDC is already bounced")
        if row.status == "cancelled":
            raise ValidationAppError("Cancelled PDC cannot be bounced")

        if row.linkedReceiptId:
            receipt = await self._receipts.get_receipt(
                company_id=company_id, receipt_id=row.linkedReceiptId
            )
            if receipt is not None:
                if receipt.journalId and self._journals is not None:
                    await self._journals.reverse_journal(
                        company_id=company_id,
                        journal_id=receipt.journalId,
                        reversal_date=bounce_date or row.chequeDate,
                    )
                await self._receipts.void_receipt(
                    company_id=company_id, receipt_id=receipt.id
                )

        if row.status in {"pending", "presented"}:
            self._assert_transition(row.status, "bounced")
        elif row.status != "cleared":
            raise ValidationAppError(f"Cannot bounce PDC in status '{row.status}'")

        return await self._received.update_status(
            company_id=company_id,
            cheque_id=cheque_id,
            status="bounced",
            linked_receipt_id=None,
        )

    async def bounce_issued(
        self,
        *,
        company_id: str,
        cheque_id: str,
    ) -> PostDatedChequeIssued:
        row = await self._issued.get_cheque(company_id=company_id, cheque_id=cheque_id)
        if row is None:
            raise ValidationAppError("PDC issued not found")
        if row.status in {"bounced", "cancelled"}:
            raise ValidationAppError(f"PDC is already {row.status}")

        if row.linkedPaymentId:
            payment = await self._payments.get_payment(
                company_id=company_id, payment_id=row.linkedPaymentId
            )
            if payment is not None:
                if payment.journalId and self._journals is not None:
                    await self._journals.reverse_journal(
                        company_id=company_id,
                        journal_id=payment.journalId,
                        reversal_date=row.chequeDate,
                    )
                await self._payments.void_payment(
                    company_id=company_id, payment_id=payment.id
                )

        if row.status in {"pending", "presented", "cleared"}:
            return await self._issued.update_status(
                company_id=company_id,
                cheque_id=cheque_id,
                status="bounced",
                linked_payment_id=None,
            )
        raise ValidationAppError(f"Cannot bounce PDC in status '{row.status}'")
