"""Shared online-payment settlement → sales receipt + FIFO allocation — P7."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from app.core.exceptions import ValidationAppError
from app.repositories.sales_receipt_repository import SalesReceiptRepository
from app.repositories.smart_settings_repository import SmartSettingsRepository
from app.services.allocation_service import AllocationService
from app.services.document_number_service import DocumentNumberService
from app.services.lock_date_service import LockDateService
from app.services.allocation_service import AllocationLine
from app.services.posting_service import PostingService
from prisma_generated.models import PaymentGatewayTransaction


class PaymentSettlementHelper:
    def __init__(
        self,
        *,
        sales_receipt_repository: SalesReceiptRepository,
        document_number_service: DocumentNumberService,
        posting_service: PostingService,
        lock_date_service: LockDateService | None = None,
        smart_settings_repository: SmartSettingsRepository | None = None,
        allocation_service: AllocationService | None = None,
        default_bank_key: str = "payproDefaultBankAccountId",
    ) -> None:
        self._receipts = sales_receipt_repository
        self._numbers = document_number_service
        self._posting = posting_service
        self._lock_date = lock_date_service
        self._smart_settings = smart_settings_repository
        self._allocation = allocation_service
        self._default_bank_key = default_bank_key

    async def resolve_bank_account_id(
        self, *, company_id: str, stored_payload: dict[str, Any]
    ) -> str | None:
        bank = stored_payload.get("bankAccountId")
        if bank:
            return str(bank)
        return await self._default_bank(company_id=company_id)

    async def create_receipt_with_allocation(
        self,
        *,
        company_id: str,
        row: PaymentGatewayTransaction,
        stored_payload: dict[str, Any],
        document_label: str = "online payment receipt",
        auto_fifo: bool = True,
        explicit_allocations: list[AllocationLine] | None = None,
    ) -> str:
        customer_id = row.customerId or stored_payload.get("customerId")
        if not customer_id:
            raise ValidationAppError(
                "customerId required to auto-create sales receipt on settlement"
            )
        bank_account_id = await self.resolve_bank_account_id(
            company_id=company_id, stored_payload=stored_payload
        )
        if not bank_account_id:
            raise ValidationAppError(
                f"bankAccountId on initiate or {self._default_bank_key} in Smart Settings defaults"
            )

        receipt_date = datetime.now(timezone.utc)
        if self._lock_date:
            await self._lock_date.assert_not_locked(
                company_id=company_id,
                document_date=receipt_date,
                document_label=document_label,
            )

        receipt_number = str(
            await self._numbers.reserve_next(company_id=company_id, sequence_key="SR")
        )
        journal = await self._posting.post_sales_receipt(
            company_id=company_id,
            receipt_date=receipt_date,
            receipt_number=receipt_number,
            bank_account_id=bank_account_id,
            total_amount=row.amount,
        )
        receipt = await self._receipts.create_receipt(
            company_id=company_id,
            receipt_number=receipt_number,
            receipt_date=receipt_date,
            customer_id=str(customer_id),
            bank_account_id=bank_account_id,
            total_amount=row.amount,
            journal_id=journal.id if journal else None,
        )
        if self._allocation is not None:
            await self._allocation.allocate_sales_receipt(
                company_id=company_id,
                receipt_id=receipt.id,
                customer_id=str(customer_id),
                receipt_total=row.amount,
                auto_fifo=auto_fifo and not explicit_allocations,
                explicit=explicit_allocations,
            )
        return receipt.id

    async def _default_bank(self, *, company_id: str) -> str | None:
        if self._smart_settings is None:
            return None
        settings_row = await self._smart_settings.get_for_company(company_id=company_id)
        if settings_row is None or not isinstance(settings_row.payload, dict):
            return None
        defaults = settings_row.payload.get("defaults")
        if not isinstance(defaults, dict):
            return None
        bank = defaults.get(self._default_bank_key)
        return str(bank) if bank else None
