"""Product master orchestration — create, update, archive, opening stock."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from app.core.exceptions import NotFoundError, ValidationAppError
from app.repositories.attachment_repository import AttachmentRepository
from app.repositories.inventory_repository import ProductBatchRepository
from app.repositories.product_repository import ProductRepository
from app.services.audit_log_service import AuditLogService
from app.services.auto_code_service import AutoCodeService
from app.services.field_masking_service import FieldMaskingService
from app.services.product_uom_service import ProductUomService
from prisma_generated.models import Product

_ALLOWED_IMAGE_MIMES = frozenset(
    {"image/jpeg", "image/png", "image/webp", "image/gif"}
)


class ProductService:
    def __init__(
        self,
        *,
        product_repository: ProductRepository,
        batch_repository: ProductBatchRepository,
        attachment_repository: AttachmentRepository,
        uom_service: ProductUomService,
        auto_code_service: AutoCodeService,
        audit_service: AuditLogService,
        field_masking: FieldMaskingService,
    ) -> None:
        self._products = product_repository
        self._batches = batch_repository
        self._attachments = attachment_repository
        self._uoms = uom_service
        self._auto_code = auto_code_service
        self._audit = audit_service
        self._field_masking = field_masking

    async def _can_write_cost(self, *, company_id: str, user_id: str) -> bool:
        access = await self._field_masking.field_access_for_user(
            company_id=company_id, user_id=user_id
        )
        if access is None:
            return True
        return access.get("cost_price", "edit") != "hidden"

    async def create_product(
        self,
        *,
        company_id: str,
        user_id: str,
        code: str | None,
        name: str,
        is_stock: bool,
        unit: str = "EA",
        category: str | None = None,
        cost: float | None = None,
        sale_price: float | None = None,
        low_stock_level: float | None = None,
        bin_location: str | None = None,
        opening_stock: dict[str, Any] | None = None,
    ) -> Product:
        resolved_code = await self._auto_code.resolve_code(
            company_id=company_id, entity_key="product", provided=code
        )
        if await self._products.code_exists(company_id=company_id, code=resolved_code):
            raise ValidationAppError(f"Product code {resolved_code} already exists")

        can_cost = await self._can_write_cost(company_id=company_id, user_id=user_id)
        cost_val = Decimal(str(cost or 0)) if can_cost else Decimal("0")
        sale_val = Decimal(str(sale_price or 0))

        row = await self._products.create_product(
            company_id=company_id,
            code=resolved_code,
            name=name.strip(),
            is_stock=is_stock,
            unit=unit,
            category=category,
            cost=cost_val,
            sale_price=sale_val,
            low_stock_level=low_stock_level,
            bin_location=bin_location,
        )

        if is_stock and sale_val > 0:
            await self._uoms.upsert_uom(
                company_id=company_id,
                product_id=row.id,
                unit_code=row.unit,
                conversion_factor=Decimal("1"),
                sale_price=sale_val,
                is_default=True,
            )

        if is_stock and opening_stock:
            qty = Decimal(str(opening_stock.get("quantity") or 0))
            if qty > 0:
                rate = opening_stock.get("rate")
                rate_dec = Decimal(str(rate if rate is not None else cost_val))
                await self._apply_opening_stock(
                    company_id=company_id,
                    product=row,
                    quantity=qty,
                    rate=rate_dec,
                )

        await self._audit.record(
            company_id=company_id,
            user_id=user_id,
            transaction_type="PRODUCT_CREATED",
            transaction_id=row.id,
            status="ok",
            details=f"Product {row.code} created",
        )
        return row

    async def get_product(self, *, company_id: str, product_id: str) -> Product:
        row = await self._products.get_by_id(company_id=company_id, product_id=product_id)
        if row is None:
            raise NotFoundError("Product not found")
        return row

    async def update_product(
        self,
        *,
        company_id: str,
        user_id: str,
        product_id: str,
        name: str,
        is_stock: bool,
        unit: str,
        category: str | None,
        cost: float | None,
        sale_price: float | None,
        low_stock_level: float | None,
        bin_location: str | None,
        custom_fields: dict | None = None,
    ) -> Product:
        existing = await self.get_product(company_id=company_id, product_id=product_id)
        if existing.isArchived:
            raise ValidationAppError("Archived products cannot be edited")

        can_cost = await self._can_write_cost(company_id=company_id, user_id=user_id)
        data: dict[str, object] = {
            "name": name.strip(),
            "isStock": is_stock,
            "unit": unit,
            "category": category.strip()[:64] if category else None,
            "salePrice": Decimal(str(sale_price or 0)),
            "lowStockLevel": (
                Decimal(str(low_stock_level)) if low_stock_level is not None else None
            ),
            "binLocation": bin_location.strip()[:64] if bin_location else None,
        }
        if can_cost and cost is not None:
            data["cost"] = Decimal(str(cost))
        if custom_fields is not None:
            data["customFields"] = custom_fields

        row = await self._products.update_product(
            product_id=product_id,
            company_id=company_id,
            data=data,
        )

        if is_stock:
            await self._uoms.upsert_uom(
                company_id=company_id,
                product_id=product_id,
                unit_code=row.unit,
                conversion_factor=Decimal("1"),
                sale_price=row.salePrice,
                is_default=True,
            )

        await self._audit.record(
            company_id=company_id,
            user_id=user_id,
            transaction_type="PRODUCT_UPDATED",
            transaction_id=product_id,
            status="ok",
            details=f"Product {row.code} updated",
        )
        return row

    async def archive_product(
        self, *, company_id: str, user_id: str, product_id: str
    ) -> Product:
        row = await self._products.set_archived(
            product_id=product_id, company_id=company_id, archived=True
        )
        await self._audit.record(
            company_id=company_id,
            user_id=user_id,
            transaction_type="PRODUCT_ARCHIVED",
            transaction_id=product_id,
            status="ok",
            details=f"Product {row.code} archived",
        )
        return row

    async def restore_product(
        self, *, company_id: str, user_id: str, product_id: str
    ) -> Product:
        row = await self._products.set_archived(
            product_id=product_id, company_id=company_id, archived=False
        )
        await self._audit.record(
            company_id=company_id,
            user_id=user_id,
            transaction_type="PRODUCT_RESTORED",
            transaction_id=product_id,
            status="ok",
            details=f"Product {row.code} restored",
        )
        return row

    async def search_products(
        self,
        *,
        company_id: str,
        query: str,
        limit: int = 20,
        active_only: bool = True,
    ) -> list[Product]:
        return await self._products.search_products(
            company_id=company_id,
            query=query,
            limit=limit,
            active_only=active_only,
        )

    async def set_primary_image(
        self,
        *,
        company_id: str,
        user_id: str,
        product_id: str,
        attachment_id: str | None,
    ) -> Product:
        await self.get_product(company_id=company_id, product_id=product_id)
        if attachment_id:
            att = await self._attachments.get_by_id(
                company_id=company_id, attachment_id=attachment_id
            )
            if att is None or att.entityType != "product" or att.entityId != product_id:
                raise ValidationAppError("Invalid attachment for this product")
            mime = (att.mimeType or "").lower()
            if mime and mime not in _ALLOWED_IMAGE_MIMES:
                raise ValidationAppError("Primary image must be JPEG, PNG, or WebP")
        row = await self._products.set_primary_image(
            product_id=product_id,
            company_id=company_id,
            attachment_id=attachment_id,
        )
        await self._audit.record(
            company_id=company_id,
            user_id=user_id,
            transaction_type="PRODUCT_IMAGE_SET",
            transaction_id=product_id,
            status="ok",
            details=f"Primary image set for {row.code}",
        )
        return row

    async def apply_opening_stock(
        self,
        *,
        company_id: str,
        user_id: str,
        product_id: str,
        quantity: float,
        rate: float | None = None,
    ) -> Product:
        product = await self.get_product(company_id=company_id, product_id=product_id)
        if not product.isStock:
            raise ValidationAppError("Opening stock applies to stock products only")
        if product.isArchived:
            raise ValidationAppError("Archived products cannot receive opening stock")
        qty = Decimal(str(quantity))
        if qty <= 0:
            raise ValidationAppError("Quantity must be positive")
        rate_dec = Decimal(str(rate if rate is not None else product.cost))
        await self._apply_opening_stock(
            company_id=company_id,
            product=product,
            quantity=qty,
            rate=rate_dec,
        )
        if rate is not None and await self._can_write_cost(
            company_id=company_id, user_id=user_id
        ):
            await self._products.update_product(
                product_id=product_id,
                company_id=company_id,
                data={"cost": rate_dec},
            )
        return await self.get_product(company_id=company_id, product_id=product_id)

    async def _apply_opening_stock(
        self,
        *,
        company_id: str,
        product: Product,
        quantity: Decimal,
        rate: Decimal,
    ) -> None:
        batch_number = f"OPENING-{product.code}"
        existing = await self._batches.list_batches(
            company_id=company_id, product_code=product.code
        )
        opening = next((b for b in existing if b.batchNumber == batch_number), None)
        if opening is None:
            await self._batches.create_batch(
                company_id=company_id,
                product_code=product.code,
                batch_number=batch_number,
                expiry_date=None,
                quantity_on_hand=quantity,
                notes=f"Opening stock @ {rate}",
            )
        else:
            await self._batches.adjust_quantity(
                company_id=company_id,
                batch_id=opening.id,
                delta=quantity,
            )
