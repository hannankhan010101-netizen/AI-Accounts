"""PayPro online payment orchestration — P7 settlement helper + FIFO allocation."""

from __future__ import annotations

import hashlib
import uuid
from decimal import Decimal
from typing import Any

import httpx

from app.core.config import get_settings
from app.core.exceptions import ValidationAppError
from app.integrations.paypro_client import PayproClient
from app.repositories.payment_gateway_repository import PaymentGatewayRepository
from app.repositories.sales_receipt_repository import SalesReceiptRepository
from app.repositories.smart_settings_repository import SmartSettingsRepository
from app.services.allocation_service import AllocationService
from app.services.document_number_service import DocumentNumberService
from app.services.lock_date_service import LockDateService
from app.services.allocation_service import AllocationLine
from app.services.payment_settlement_helper import PaymentSettlementHelper
from app.services.posting_service import PostingService
from prisma_generated.models import PaymentGatewayTransaction


class PayproService:
    PROVIDER = "paypro"

    def __init__(
        self,
        *,
        payment_gateway_repository: PaymentGatewayRepository,
        sales_receipt_repository: SalesReceiptRepository,
        document_number_service: DocumentNumberService,
        posting_service: PostingService,
        lock_date_service: LockDateService,
        smart_settings_repository: SmartSettingsRepository,
        allocation_service: AllocationService,
        paypro_client: PayproClient | None = None,
    ) -> None:
        self._repo = payment_gateway_repository
        self._settings = get_settings()
        self._client = paypro_client or PayproClient()
        self._settlement = PaymentSettlementHelper(
            sales_receipt_repository=sales_receipt_repository,
            document_number_service=document_number_service,
            posting_service=posting_service,
            lock_date_service=lock_date_service,
            smart_settings_repository=smart_settings_repository,
            allocation_service=allocation_service,
            default_bank_key="payproDefaultBankAccountId",
        )

    async def list_transactions(self, *, company_id: str):
        return await self._repo.list_transactions(
            company_id=company_id, provider=self.PROVIDER
        )

    async def initiate_payment(
        self,
        *,
        company_id: str,
        customer_id: str,
        amount: Decimal,
        bank_account_id: str | None = None,
    ) -> dict[str, Any]:
        if amount <= 0:
            raise ValidationAppError("Amount must be positive")
        merchant_ref = f"PP-{uuid.uuid4().hex[:16].upper()}"
        payload: dict[str, Any] = {
            "customerId": customer_id,
            "bankAccountId": bank_account_id,
        }
        row = await self._repo.create_pending(
            company_id=company_id,
            provider=self.PROVIDER,
            merchant_ref=merchant_ref,
            amount=amount,
            customer_id=customer_id,
            payload=payload,
        )
        checkout_url = None
        mode = "stub"
        if self._client.enabled:
            try:
                live = await self._client.create_checkout(
                    merchant_ref=merchant_ref,
                    amount=amount,
                    customer_id=customer_id,
                )
                checkout_url = live.get("checkoutUrl") or live.get("url")
                mode = "api"
            except httpx.HTTPError as exc:
                payload["checkoutError"] = str(exc)
        if checkout_url is None and self._settings.paypro_merchant_id:
            checkout_url = (
                f"https://paypro.example/checkout?"
                f"merchant={self._settings.paypro_merchant_id}&ref={merchant_ref}"
            )
        return {
            "transaction": row,
            "merchantRef": merchant_ref,
            "checkoutUrl": checkout_url,
            "mode": mode,
            "message": "Live PayPro checkout"
            if mode == "api"
            else "Stub checkout URL. Set PAYPRO_API_URL for production.",
        }

    def verify_webhook_signature(self, *, body: bytes, signature: str | None) -> bool:
        secret = (self._settings.paypro_webhook_secret or "").strip()
        if not secret:
            return True
        if not signature:
            return False
        expected = hashlib.sha256(secret.encode() + body).hexdigest()
        return signature == expected

    async def settle_webhook(
        self,
        *,
        company_id: str,
        merchant_ref: str,
        payload: dict[str, Any],
        auto_fifo: bool = True,
        explicit_allocations: list[AllocationLine] | None = None,
    ) -> PaymentGatewayTransaction:
        row = await self._repo.get_by_merchant_ref(
            company_id=company_id,
            provider=self.PROVIDER,
            merchant_ref=merchant_ref,
        )
        if row is None:
            raise ValidationAppError("Payment transaction not found")
        if row.status == "settled":
            return row

        stored = row.payload if isinstance(row.payload, dict) else {}
        sales_receipt_id = payload.get("salesReceiptId")
        if not sales_receipt_id:
            sales_receipt_id = await self._settlement.create_receipt_with_allocation(
                company_id=company_id,
                row=row,
                stored_payload=stored,
                document_label="PayPro settlement receipt",
                auto_fifo=auto_fifo,
                explicit_allocations=explicit_allocations,
            )

        return await self._repo.mark_settled(
            transaction_id=row.id,
            sales_receipt_id=str(sales_receipt_id) if sales_receipt_id else None,
            payload={**payload, "salesReceiptId": sales_receipt_id},
        )
