"""Payment gateway transaction persistence — P5."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from prisma_generated import Prisma
from prisma_generated.models import PaymentGatewayTransaction


class PaymentGatewayRepository:
    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_transactions(
        self, *, company_id: str, provider: str | None = None, take: int = 100
    ) -> list[PaymentGatewayTransaction]:
        where: dict = {"companyId": company_id}
        if provider:
            where["provider"] = provider
        return await self._db.paymentgatewaytransaction.find_many(
            where=where,
            order={"createdAt": "desc"},
            take=take,
        )

    async def create_pending(
        self,
        *,
        company_id: str,
        provider: str,
        merchant_ref: str,
        amount: Decimal,
        customer_id: str | None,
        payload: dict[str, Any],
    ) -> PaymentGatewayTransaction:
        return await self._db.paymentgatewaytransaction.create(
            data={
                "companyId": company_id,
                "provider": provider,
                "merchantRef": merchant_ref,
                "amount": amount,
                "customerId": customer_id,
                "payload": payload,
                "status": "pending",
            }
        )

    async def get_by_merchant_ref(
        self, *, company_id: str, provider: str, merchant_ref: str
    ) -> PaymentGatewayTransaction | None:
        return await self._db.paymentgatewaytransaction.find_first(
            where={
                "companyId": company_id,
                "provider": provider,
                "merchantRef": merchant_ref,
            }
        )

    async def mark_settled(
        self,
        *,
        transaction_id: str,
        sales_receipt_id: str | None,
        payload: dict[str, Any],
    ) -> PaymentGatewayTransaction:
        return await self._db.paymentgatewaytransaction.update(
            where={"id": transaction_id},
            data={
                "status": "settled",
                "salesReceiptId": sales_receipt_id,
                "payload": payload,
            },
        )
