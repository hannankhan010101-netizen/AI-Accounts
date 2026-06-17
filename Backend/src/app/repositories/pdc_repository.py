"""Post-Dated Cheques (PDCR + PDCI) persistence — Sprint 14, catalog §5.7 / §6.1."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from prisma_generated import Prisma
from prisma_generated.models import (
    PostDatedChequeIssued,
    PostDatedChequeReceived,
)

from app.services.party_snapshot_service import PartySnapshotService


_ALLOWED_STATUSES = {"pending", "presented", "cleared", "bounced", "cancelled"}


class PdcReceivedRepository:
    """Post-dated cheques received from customers."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def get_cheque(
        self, *, company_id: str, cheque_id: str
    ) -> PostDatedChequeReceived | None:
        row = await self._db.postdatedchequereceived.find_unique(where={"id": cheque_id})
        if row is None or row.companyId != company_id:
            return None
        return row

    async def list_cheques(
        self, *, company_id: str, status: str | None = None, take: int = 200
    ) -> list[PostDatedChequeReceived]:
        where: dict = {"companyId": company_id}
        if status:
            where["status"] = status
        return await self._db.postdatedchequereceived.find_many(
            where=where,
            order={"chequeDate": "asc"},
            take=take,
        )

    async def create_cheque(
        self,
        *,
        company_id: str,
        voucher_number: str,
        cheque_number: str,
        bank_name: str,
        customer_id: str,
        received_date: datetime,
        cheque_date: datetime,
        amount: Decimal,
        notes: str | None = None,
    ) -> PostDatedChequeReceived:
        data = {
                "companyId": company_id,
                "voucherNumber": voucher_number,
                "chequeNumber": cheque_number,
                "bankName": bank_name,
                "customerId": customer_id,
                "receivedDate": received_date,
                "chequeDate": cheque_date,
                "amount": amount,
                "notes": notes,
                "status": "pending",
            }
        data.update(
            await PartySnapshotService(self._db).customer_fields(
                company_id=company_id, customer_id=customer_id
            )
        )
        return await self._db.postdatedchequereceived.create(data=data)

    async def update_status(
        self,
        *,
        company_id: str,
        cheque_id: str,
        status: str,
        linked_receipt_id: str | None = None,
    ) -> PostDatedChequeReceived:
        if status not in _ALLOWED_STATUSES:
            raise ValueError(f"status must be one of {sorted(_ALLOWED_STATUSES)}")
        row = await self._db.postdatedchequereceived.find_unique(where={"id": cheque_id})
        if row is None or row.companyId != company_id:
            raise ValueError("PDC not found for this company")
        data: dict = {"status": status}
        if linked_receipt_id is not None:
            data["linkedReceiptId"] = linked_receipt_id
        return await self._db.postdatedchequereceived.update(
            where={"id": cheque_id}, data=data
        )


class PdcIssuedRepository:
    """Post-dated cheques issued to suppliers."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def get_cheque(
        self, *, company_id: str, cheque_id: str
    ) -> PostDatedChequeIssued | None:
        row = await self._db.postdatedchequeissued.find_unique(where={"id": cheque_id})
        if row is None or row.companyId != company_id:
            return None
        return row

    async def list_cheques(
        self, *, company_id: str, status: str | None = None, take: int = 200
    ) -> list[PostDatedChequeIssued]:
        where: dict = {"companyId": company_id}
        if status:
            where["status"] = status
        return await self._db.postdatedchequeissued.find_many(
            where=where,
            order={"chequeDate": "asc"},
            take=take,
        )

    async def create_cheque(
        self,
        *,
        company_id: str,
        voucher_number: str,
        cheque_number: str,
        bank_account_id: str,
        supplier_id: str,
        issued_date: datetime,
        cheque_date: datetime,
        amount: Decimal,
        notes: str | None = None,
    ) -> PostDatedChequeIssued:
        data = {
                "companyId": company_id,
                "voucherNumber": voucher_number,
                "chequeNumber": cheque_number,
                "bankAccountId": bank_account_id,
                "supplierId": supplier_id,
                "issuedDate": issued_date,
                "chequeDate": cheque_date,
                "amount": amount,
                "notes": notes,
                "status": "pending",
            }
        data.update(
            await PartySnapshotService(self._db).supplier_fields(
                company_id=company_id, supplier_id=supplier_id
            )
        )
        return await self._db.postdatedchequeissued.create(data=data)

    async def update_status(
        self,
        *,
        company_id: str,
        cheque_id: str,
        status: str,
        linked_payment_id: str | None = None,
    ) -> PostDatedChequeIssued:
        if status not in _ALLOWED_STATUSES:
            raise ValueError(f"status must be one of {sorted(_ALLOWED_STATUSES)}")
        row = await self._db.postdatedchequeissued.find_unique(where={"id": cheque_id})
        if row is None or row.companyId != company_id:
            raise ValueError("PDC not found for this company")
        data: dict = {"status": status}
        if linked_payment_id is not None:
            data["linkedPaymentId"] = linked_payment_id
        return await self._db.postdatedchequeissued.update(
            where={"id": cheque_id}, data=data
        )
