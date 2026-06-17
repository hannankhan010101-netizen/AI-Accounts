"""Customer / supplier advance return — FA §5.8 / §6.4."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from prisma_generated import Prisma

from app.core.exceptions import NotFoundError, ValidationAppError
from app.repositories.bank_receipt_repository import BankReceiptRepository
from app.repositories.bank_repository import BankRepository
from app.repositories.sales_receipt_repository import SalesReceiptRepository
from app.repositories.supplier_payment_repository import SupplierPaymentRepository
from app.services.document_number_service import DocumentNumberService
from app.services.lock_date_service import LockDateService
from app.services.posting_service import PostingService
from app.utils.settlement_balance import settlement_unallocated


class AdvanceReturnService:
    def __init__(
        self,
        *,
        prisma: Prisma,
        sales_receipts: SalesReceiptRepository,
        supplier_payments: SupplierPaymentRepository,
        banks: BankRepository,
        bank_receipts: BankReceiptRepository,
        document_numbers: DocumentNumberService,
        lock_date: LockDateService,
        posting: PostingService,
    ) -> None:
        self._db = prisma
        self._sales_receipts = sales_receipts
        self._supplier_payments = supplier_payments
        self._banks = banks
        self._bank_receipts = bank_receipts
        self._numbers = document_numbers
        self._lock_date = lock_date
        self._posting = posting

    async def receipt_balance(
        self,
        *,
        company_id: str,
        receipt_id: str,
    ) -> dict[str, Decimal]:
        row = await self._sales_receipts.get_receipt(
            company_id=company_id, receipt_id=receipt_id
        )
        if row is None:
            raise NotFoundError("Sales receipt not found")
        allocated = await self._sum_receipt_allocations(receipt_id=receipt_id)
        returned = await self._sum_customer_returns(receipt_id=receipt_id)
        total = Decimal(str(row.totalAmount))
        unallocated = settlement_unallocated(
            total=total, allocated=allocated, returned=returned
        )
        return {
            "total": total,
            "allocated": allocated,
            "returned": returned,
            "unallocated": unallocated,
        }

    async def payment_balance(
        self,
        *,
        company_id: str,
        payment_id: str,
    ) -> dict[str, Decimal]:
        row = await self._supplier_payments.get_payment(
            company_id=company_id, payment_id=payment_id
        )
        if row is None:
            raise NotFoundError("Supplier payment not found")
        allocated = await self._sum_payment_allocations(payment_id=payment_id)
        returned = await self._sum_supplier_returns(payment_id=payment_id)
        total = Decimal(str(row.totalAmount))
        unallocated = settlement_unallocated(
            total=total, allocated=allocated, returned=returned
        )
        return {
            "total": total,
            "allocated": allocated,
            "returned": returned,
            "unallocated": unallocated,
        }

    async def return_customer_advance(
        self,
        *,
        company_id: str,
        receipt_id: str,
        return_date: datetime,
        amount: Decimal,
        bank_account_id: str | None = None,
    ) -> dict[str, Any]:
        receipt = await self._sales_receipts.get_receipt(
            company_id=company_id, receipt_id=receipt_id
        )
        if receipt is None:
            raise NotFoundError("Sales receipt not found")

        balances = await self.receipt_balance(company_id=company_id, receipt_id=receipt_id)
        if amount > balances["unallocated"]:
            raise ValidationAppError(
                f"Return amount exceeds unallocated advance ({balances['unallocated']})."
            )

        bank_id = bank_account_id or receipt.bankAccountId
        await self._lock_date.assert_not_locked(
            company_id=company_id,
            document_date=return_date,
            document_label="customer advance return",
        )

        ar_nominal, _ = await self._posting.subledger_nominals(company_id=company_id)
        if not ar_nominal:
            raise ValidationAppError(
                "Set receivables nominal in Smart Settings → Defaults before returning advance."
            )

        voucher_number = str(
            await self._numbers.reserve_next(company_id=company_id, sequence_key="EP")
        )
        journal = await self._posting.post_bank_payment(
            company_id=company_id,
            payment_date=return_date,
            voucher_number=voucher_number,
            bank_account_id=bank_id,
            counterpart_nominal_code=str(ar_nominal),
            total_amount=amount,
        )
        payment = await self._banks.create_payment(
            company_id=company_id,
            bank_account_id=bank_id,
            payment_date=return_date,
            voucher_number=voucher_number,
            total_amount=amount,
            nominal_code=str(ar_nominal),
            journal_id=journal.id if journal else None,
            custom_fields={
                "advanceReturnFrom": "sales_receipt",
                "sourceReceiptId": receipt_id,
                "sourceReceiptNumber": receipt.receiptNumber,
            },
        )
        advance_return = await self._db.customeradvancereturn.create(
            data={
                "companyId": company_id,
                "salesReceiptId": receipt_id,
                "bankPaymentId": payment.id,
                "amount": amount,
                "returnDate": return_date,
            },
            include={"bankPayment": True},
        )
        return {
            "advanceReturn": advance_return,
            "bankPayment": payment,
            "posted": journal is not None,
        }

    async def return_supplier_advance(
        self,
        *,
        company_id: str,
        payment_id: str,
        return_date: datetime,
        amount: Decimal,
        bank_account_id: str | None = None,
    ) -> dict[str, Any]:
        payment_row = await self._supplier_payments.get_payment(
            company_id=company_id, payment_id=payment_id
        )
        if payment_row is None:
            raise NotFoundError("Supplier payment not found")

        balances = await self.payment_balance(company_id=company_id, payment_id=payment_id)
        if amount > balances["unallocated"]:
            raise ValidationAppError(
                f"Return amount exceeds unallocated advance ({balances['unallocated']})."
            )

        bank_id = bank_account_id or payment_row.bankAccountId
        await self._lock_date.assert_not_locked(
            company_id=company_id,
            document_date=return_date,
            document_label="supplier advance return",
        )

        _, ap_nominal = await self._posting.subledger_nominals(company_id=company_id)
        if not ap_nominal:
            raise ValidationAppError(
                "Set payables nominal in Smart Settings → Defaults before returning advance."
            )

        voucher_number = str(
            await self._numbers.reserve_next(company_id=company_id, sequence_key="IR")
        )
        journal = await self._posting.post_bank_receipt(
            company_id=company_id,
            receipt_date=return_date,
            voucher_number=voucher_number,
            bank_account_id=bank_id,
            counterpart_nominal_code=str(ap_nominal),
            total_amount=amount,
        )
        bank_receipt = await self._bank_receipts.create_receipt(
            company_id=company_id,
            voucher_number=voucher_number,
            receipt_date=return_date,
            bank_account_id=bank_id,
            total_amount=amount,
            nominal_code=str(ap_nominal),
            journal_id=journal.id if journal else None,
            custom_fields={
                "advanceReturnFrom": "supplier_payment",
                "sourcePaymentId": payment_id,
                "sourcePaymentNumber": payment_row.voucherNumber,
            },
        )
        advance_return = await self._db.supplieradvancereturn.create(
            data={
                "companyId": company_id,
                "supplierPaymentId": payment_id,
                "bankReceiptId": bank_receipt.id,
                "amount": amount,
                "returnDate": return_date,
            },
            include={"bankReceipt": True},
        )
        return {
            "advanceReturn": advance_return,
            "bankReceipt": bank_receipt,
            "posted": journal is not None,
        }

    async def list_receipt_balances(
        self, *, company_id: str, receipt_ids: list[str]
    ) -> dict[str, Decimal]:
        if not receipt_ids:
            return {}
        receipts = await self._db.salesreceipt.find_many(
            where={"companyId": company_id, "id": {"in": receipt_ids}},
            include={"allocations": True, "advanceReturns": True},
        )
        out: dict[str, Decimal] = {}
        for row in receipts:
            total = Decimal(str(row.totalAmount))
            allocated = sum(
                (Decimal(str(a.amount)) for a in (row.allocations or [])),
                Decimal(0),
            )
            returned = sum(
                (Decimal(str(r.amount)) for r in (row.advanceReturns or [])),
                Decimal(0),
            )
            out[row.id] = settlement_unallocated(
                total=total, allocated=allocated, returned=returned
            )
        return out

    async def list_payment_balances(
        self, *, company_id: str, payment_ids: list[str]
    ) -> dict[str, Decimal]:
        if not payment_ids:
            return {}
        payments = await self._db.supplierpayment.find_many(
            where={"companyId": company_id, "id": {"in": payment_ids}},
            include={"allocations": True, "advanceReturns": True},
        )
        out: dict[str, Decimal] = {}
        for row in payments:
            total = Decimal(str(row.totalAmount))
            allocated = sum(
                (Decimal(str(a.amount)) for a in (row.allocations or [])),
                Decimal(0),
            )
            returned = sum(
                (Decimal(str(r.amount)) for r in (row.advanceReturns or [])),
                Decimal(0),
            )
            out[row.id] = settlement_unallocated(
                total=total, allocated=allocated, returned=returned
            )
        return out

    async def _sum_receipt_allocations(self, *, receipt_id: str) -> Decimal:
        rows = await self._db.salesreceiptallocation.find_many(
            where={"salesReceiptId": receipt_id},
        )
        return sum((Decimal(str(r.amount)) for r in rows), Decimal(0))

    async def _sum_payment_allocations(self, *, payment_id: str) -> Decimal:
        rows = await self._db.supplierpaymentallocation.find_many(
            where={"supplierPaymentId": payment_id},
        )
        return sum((Decimal(str(r.amount)) for r in rows), Decimal(0))

    async def _sum_customer_returns(self, *, receipt_id: str) -> Decimal:
        rows = await self._db.customeradvancereturn.find_many(
            where={"salesReceiptId": receipt_id},
        )
        return sum((Decimal(str(r.amount)) for r in rows), Decimal(0))

    async def _sum_supplier_returns(self, *, payment_id: str) -> Decimal:
        rows = await self._db.supplieradvancereturn.find_many(
            where={"supplierPaymentId": payment_id},
        )
        return sum((Decimal(str(r.amount)) for r in rows), Decimal(0))

    async def list_customer_returns(self, *, receipt_id: str) -> list[Any]:
        return await self._db.customeradvancereturn.find_many(
            where={"salesReceiptId": receipt_id},
            include={"bankPayment": True},
            order={"returnDate": "desc"},
        )

    async def list_supplier_returns(self, *, payment_id: str) -> list[Any]:
        return await self._db.supplieradvancereturn.find_many(
            where={"supplierPaymentId": payment_id},
            include={"bankReceipt": True},
            order={"returnDate": "desc"},
        )
