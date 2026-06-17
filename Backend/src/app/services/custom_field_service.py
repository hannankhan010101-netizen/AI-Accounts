"""Custom field definitions and entity values — P11/P12 validation."""

from __future__ import annotations

from typing import Any

from app.core.exceptions import NotFoundError, ValidationAppError
from prisma_generated import Prisma

ALLOWED_ENTITY_TYPES = frozenset({"customer", "product"})
ALLOWED_FIELD_TYPES = frozenset({"text", "number", "date", "picklist"})


class CustomFieldService:
    def __init__(self, *, prisma: Prisma) -> None:
        self._db = prisma

    def _serialize_definition(self, row: Any) -> dict[str, Any]:
        options = row.picklistOptions if row.picklistOptions else None
        if isinstance(options, list):
            picklist = options
        else:
            picklist = None
        return {
            "id": row.id,
            "entityType": row.entityType,
            "fieldKey": row.fieldKey,
            "label": row.label,
            "fieldType": row.fieldType,
            "isRequired": row.isRequired,
            "picklistOptions": picklist,
        }

    async def list_definitions(
        self, *, company_id: str, entity_type: str | None = None
    ) -> list[dict[str, Any]]:
        where: dict[str, Any] = {"companyId": company_id}
        if entity_type:
            where["entityType"] = entity_type.lower()
        rows = await self._db.customfielddefinition.find_many(
            where=where, order={"fieldKey": "asc"}
        )
        return [self._serialize_definition(r) for r in rows]

    async def create_definition(
        self,
        *,
        company_id: str,
        entity_type: str,
        field_key: str,
        label: str,
        field_type: str = "text",
        is_required: bool = False,
        picklist_options: list[str] | None = None,
    ) -> dict[str, Any]:
        et = entity_type.strip().lower()
        if et not in ALLOWED_ENTITY_TYPES:
            raise ValidationAppError("entityType must be customer or product")
        ft = field_type.strip().lower() or "text"
        if ft not in ALLOWED_FIELD_TYPES:
            raise ValidationAppError(f"fieldType must be one of: {sorted(ALLOWED_FIELD_TYPES)}")
        key = field_key.strip()
        if not key:
            raise ValidationAppError("fieldKey is required")
        if ft == "picklist":
            if not picklist_options:
                raise ValidationAppError("picklistOptions required for picklist fields")
        elif picklist_options:
            raise ValidationAppError("picklistOptions only allowed for picklist fieldType")

        row = await self._db.customfielddefinition.create(
            data={
                "companyId": company_id,
                "entityType": et,
                "fieldKey": key,
                "label": label.strip() or key,
                "fieldType": ft,
                "isRequired": is_required,
                "picklistOptions": picklist_options if ft == "picklist" else None,
            }
        )
        return self._serialize_definition(row)

    async def _validate_payload(
        self, *, company_id: str, entity_type: str, custom_fields: dict[str, Any]
    ) -> None:
        defs = await self.list_definitions(
            company_id=company_id, entity_type=entity_type
        )
        by_key = {d["fieldKey"]: d for d in defs}
        for key, value in custom_fields.items():
            spec = by_key.get(key)
            if spec is None:
                raise ValidationAppError(f"Unknown custom field: {key}")
            if value is None or value == "":
                if spec.get("isRequired"):
                    raise ValidationAppError(f"Required custom field missing: {key}")
                continue
            ft = spec.get("fieldType")
            if ft == "picklist":
                allowed = spec.get("picklistOptions") or []
                if str(value) not in [str(o) for o in allowed]:
                    raise ValidationAppError(
                        f"Value {value!r} not in picklist for {key}"
                    )
            elif ft == "number":
                try:
                    float(str(value))
                except ValueError as exc:
                    raise ValidationAppError(f"{key} must be numeric") from exc

        for spec in defs:
            if spec.get("isRequired") and spec["fieldKey"] not in custom_fields:
                existing_required = spec["fieldKey"]
                raise ValidationAppError(f"Required custom field missing: {existing_required}")

    async def patch_customer_fields(
        self, *, company_id: str, customer_id: str, custom_fields: dict[str, Any]
    ) -> dict[str, Any]:
        row = await self._db.customer.find_first(
            where={"id": customer_id, "companyId": company_id}
        )
        if row is None:
            raise NotFoundError("Customer not found")
        merged = {**(row.customFields or {}), **custom_fields}
        await self._validate_payload(
            company_id=company_id, entity_type="customer", custom_fields=merged
        )
        updated = await self._db.customer.update(
            where={"id": customer_id},
            data={"customFields": merged},
        )
        return {"id": updated.id, "customFields": updated.customFields}

    async def patch_product_fields(
        self, *, company_id: str, product_id: str, custom_fields: dict[str, Any]
    ) -> dict[str, Any]:
        row = await self._db.product.find_first(
            where={"id": product_id, "companyId": company_id}
        )
        if row is None:
            raise NotFoundError("Product not found")
        merged = {**(row.customFields or {}), **custom_fields}
        await self._validate_payload(
            company_id=company_id, entity_type="product", custom_fields=merged
        )
        updated = await self._db.product.update(
            where={"id": product_id},
            data={"customFields": merged},
        )
        return {"id": updated.id, "customFields": updated.customFields}
