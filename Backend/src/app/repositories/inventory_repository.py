"""Inventory write surface — Stock Adjustment, Stock Transfer, Batch & Expiry (§7)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.constants.inventory_alerts import EXPIRY_ALERT_WINDOW_DAYS
from prisma_generated import Prisma
from prisma_generated.models import (
    ProductBatch,
    StockAdjustment,
    StockTransfer,
)


class StockAdjustmentRepository:
    """§7.3 stock adjustment vouchers."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_adjustments(
        self, *, company_id: str, take: int = 50
    ) -> list[StockAdjustment]:
        return await self._db.stockadjustment.find_many(
            where={"companyId": company_id},
            order={"adjustmentDate": "desc"},
            take=take,
            include={"lines": True},
        )

    async def get_adjustment(
        self, *, company_id: str, adjustment_id: str
    ) -> StockAdjustment | None:
        row = await self._db.stockadjustment.find_unique(
            where={"id": adjustment_id},
            include={"lines": True},
        )
        if row is None or row.companyId != company_id:
            return None
        return row

    async def create_adjustment(
        self,
        *,
        company_id: str,
        voucher_number: str,
        adjustment_date: datetime,
        reason: str,
        notes: str | None,
        lines: list[dict],
    ) -> StockAdjustment:
        return await self._db.stockadjustment.create(
            data={
                "companyId": company_id,
                "voucherNumber": voucher_number,
                "adjustmentDate": adjustment_date,
                "reason": reason,
                "notes": notes,
                "status": "draft",
                "lines": {"create": lines},
            },
            include={"lines": True},
        )

    async def mark_posted(
        self,
        *,
        company_id: str,
        adjustment_id: str,
        journal_id: str,
    ) -> StockAdjustment:
        row = await self.get_adjustment(
            company_id=company_id, adjustment_id=adjustment_id
        )
        if row is None:
            raise ValueError("Stock adjustment not found")
        return await self._db.stockadjustment.update(
            where={"id": adjustment_id},
            data={"status": "posted", "journalId": journal_id},
            include={"lines": True},
        )

    async def update_status(
        self,
        *,
        company_id: str,
        adjustment_id: str,
        status: str,
    ) -> StockAdjustment:
        row = await self.get_adjustment(
            company_id=company_id, adjustment_id=adjustment_id
        )
        if row is None:
            raise ValueError("Stock adjustment not found")
        return await self._db.stockadjustment.update(
            where={"id": adjustment_id},
            data={"status": status},
            include={"lines": True},
        )


class StockTransferRepository:
    """§7.2 stock transfer between two locations."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_transfers(
        self, *, company_id: str, take: int = 50
    ) -> list[StockTransfer]:
        return await self._db.stocktransfer.find_many(
            where={"companyId": company_id},
            order={"transferDate": "desc"},
            take=take,
            include={"lines": True},
        )

    async def get_transfer(
        self, *, company_id: str, transfer_id: str
    ) -> StockTransfer | None:
        row = await self._db.stocktransfer.find_unique(
            where={"id": transfer_id},
            include={"lines": True},
        )
        if row is None or row.companyId != company_id:
            return None
        return row

    async def create_transfer(
        self,
        *,
        company_id: str,
        voucher_number: str,
        transfer_date: datetime,
        from_location_code: str,
        to_location_code: str,
        notes: str | None,
        lines: list[dict],
    ) -> StockTransfer:
        if from_location_code == to_location_code:
            raise ValueError("From and To locations must differ")
        return await self._db.stocktransfer.create(
            data={
                "companyId": company_id,
                "voucherNumber": voucher_number,
                "transferDate": transfer_date,
                "fromLocationCode": from_location_code,
                "toLocationCode": to_location_code,
                "notes": notes,
                "status": "posted",
                "lines": {"create": lines},
            },
            include={"lines": True},
        )


class ProductBatchRepository:
    """§7.8 product batch + expiry tracking."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_batches(
        self,
        *,
        company_id: str,
        product_code: str | None = None,
        take: int = 500,
    ) -> list[ProductBatch]:
        where: dict = {"companyId": company_id}
        if product_code:
            where["productCode"] = product_code
        return await self._db.productbatch.find_many(
            where=where,
            order={"expiryDate": "asc"},
            take=take,
        )

    async def list_expiring_batches(
        self,
        *,
        company_id: str,
        within_days: int = EXPIRY_ALERT_WINDOW_DAYS,
        include_expired: bool = True,
        take: int = 500,
        now: datetime | None = None,
    ) -> list[ProductBatch]:
        """Batches with on-hand qty and expiry within alert window (or already expired)."""

        ref = now or datetime.now(UTC)
        end = ref + timedelta(days=within_days)
        where: dict = {
            "companyId": company_id,
            "expiryDate": {"not": None, "lte": end},
            "quantityOnHand": {"gt": Decimal(0)},
        }
        if not include_expired:
            where["expiryDate"] = {"not": None, "gt": ref, "lte": end}
        return await self._db.productbatch.find_many(
            where=where,
            order={"expiryDate": "asc"},
            take=take,
        )

    async def create_batch(
        self,
        *,
        company_id: str,
        product_code: str,
        batch_number: str,
        expiry_date: datetime | None,
        quantity_on_hand: Decimal,
        notes: str | None = None,
    ) -> ProductBatch:
        return await self._db.productbatch.create(
            data={
                "companyId": company_id,
                "productCode": product_code,
                "batchNumber": batch_number,
                "expiryDate": expiry_date,
                "quantityOnHand": quantity_on_hand,
                "notes": notes,
            }
        )

    async def adjust_quantity(
        self,
        *,
        company_id: str,
        batch_id: str,
        delta: Decimal,
    ) -> ProductBatch:
        existing = await self._db.productbatch.find_unique(where={"id": batch_id})
        if existing is None or existing.companyId != company_id:
            raise ValueError("Batch not found for this company")
        return await self._db.productbatch.update(
            where={"id": batch_id},
            data={"quantityOnHand": existing.quantityOnHand + delta},
        )

    async def apply_product_delta(
        self,
        *,
        company_id: str,
        product_code: str,
        delta: Decimal,
        batch_number: str | None = None,
    ) -> ProductBatch:
        """Adjust batch quantity; uses explicit batch or first batch / MAIN — P17."""

        batch_key = (batch_number or "").strip()
        if batch_key:
            row = await self._db.productbatch.find_first(
                where={
                    "companyId": company_id,
                    "productCode": product_code,
                    "batchNumber": batch_key,
                }
            )
            if row is not None:
                return await self.adjust_quantity(
                    company_id=company_id,
                    batch_id=row.id,
                    delta=delta,
                )
            if delta < 0:
                raise ValueError(
                    f"Batch {batch_key} not found for product {product_code}; "
                    "cannot reduce stock"
                )
            return await self.create_batch(
                company_id=company_id,
                product_code=product_code,
                batch_number=batch_key,
                expiry_date=None,
                quantity_on_hand=delta,
                notes="Auto-created by stock movement",
            )

        rows = await self._db.productbatch.find_many(
            where={"companyId": company_id, "productCode": product_code},
            order={"batchNumber": "asc"},
            take=1,
        )
        if rows:
            return await self.adjust_quantity(
                company_id=company_id,
                batch_id=rows[0].id,
                delta=delta,
            )
        if delta < 0:
            raise ValueError(
                f"No batch for product {product_code}; cannot reduce stock further"
            )
        return await self.create_batch(
            company_id=company_id,
            product_code=product_code,
            batch_number="MAIN",
            expiry_date=None,
            quantity_on_hand=delta,
            notes="Auto-created by stock movement",
        )
