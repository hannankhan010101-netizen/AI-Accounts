"""Apply field-level security policies to API responses — RBAC v2."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.repositories.membership_repository import MembershipRepository
from app.services.access_control_service import AccessControlService
from app.services.effective_permission_service import EffectivePermissionService

# Policy field keys → response keys per entity type.
ENTITY_FIELD_MAP: dict[str, dict[str, list[str]]] = {
    "product": {
        "cost_price": ["cost", "unitCost", "standardCost", "averageCost"],
        "profit_margin": ["margin", "profitMargin", "grossMargin"],
        "discount": ["discount", "discountAmount", "discountPercent"],
        "tax_rate": ["taxRate", "vatRate"],
    },
    "customer": {
        "credit_limit": ["creditLimit"],
        "discount": ["discount", "discountPercent"],
    },
    "invoice": {
        "cost_price": ["cost", "unitCost"],
        "profit_margin": ["margin", "profitMargin"],
        "discount": ["discount", "discountAmount", "discountPercent"],
    },
    "bill": {
        "discount": ["discount", "discountAmount"],
        "gl_account": ["glAccountId", "accountId"],
    },
    "bank_account": {
        "bank_account": ["accountNumber", "iban", "routingNumber"],
    },
}


class FieldMaskingService:
    def __init__(
        self,
        *,
        access_control: AccessControlService,
        membership_repo: MembershipRepository,
        effective_permissions: EffectivePermissionService,
    ) -> None:
        self._access_control = access_control
        self._membership_repo = membership_repo
        self._effective_permissions = effective_permissions

    async def field_access_for_user(
        self, *, company_id: str, user_id: str
    ) -> dict[str, str] | None:
        """Return merged field access map, or None when masking should be skipped."""
        perms = await self._effective_permissions.permissions_for_user(
            company_id=company_id, user_id=user_id
        )
        if "*" in perms:
            return None

        membership = await self._membership_repo.get_membership(
            company_id=company_id, user_id=user_id
        )
        if membership is None:
            return {}
        role_ids = membership.get("roleIds") or []
        if not role_ids and membership.get("roleId"):
            role_ids = [membership["roleId"]]
        if not role_ids:
            return {}
        return await self._access_control.field_access_for_roles(
            company_id=company_id, role_ids=role_ids
        )

    def mask_row(
        self,
        row: dict[str, Any],
        *,
        entity: str,
        field_access: dict[str, str] | None,
    ) -> dict[str, Any]:
        if not field_access:
            return row

        mapping = ENTITY_FIELD_MAP.get(entity, {})
        if not mapping:
            return row

        out = deepcopy(row)
        for policy_key, response_keys in mapping.items():
            level = field_access.get(policy_key, "edit")
            if level != "hidden":
                continue
            for key in response_keys:
                if key in out:
                    out[key] = None
        return out

    def mask_rows(
        self,
        rows: list[dict[str, Any]],
        *,
        entity: str,
        field_access: dict[str, str] | None,
    ) -> list[dict[str, Any]]:
        if not field_access:
            return rows
        return [
            self.mask_row(row, entity=entity, field_access=field_access) for row in rows
        ]

    async def mask_for_user(
        self,
        *,
        company_id: str,
        user_id: str,
        rows: list[dict[str, Any]],
        entity: str,
    ) -> list[dict[str, Any]]:
        field_access = await self.field_access_for_user(
            company_id=company_id, user_id=user_id
        )
        return self.mask_rows(rows, entity=entity, field_access=field_access)
