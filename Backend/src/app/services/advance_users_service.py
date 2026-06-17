"""Advance user visibility + data scope assignments — FA §12.5 / RBAC v2."""

from __future__ import annotations

from typing import Any, Callable, TypeVar

from app.services.access_control_service import AccessControlService
from app.services.app_settings_service import AppSettingsService
from prisma_generated import Prisma

T = TypeVar("T")


def _normalize_tokens(raw: list[str] | None) -> set[str]:
    if not raw:
        return set()
    out: set[str] = set()
    for item in raw:
        token = str(item or "").strip()
        if token:
            out.add(token)
    return out


def _rule_for_user(rules: list[dict[str, Any]], user_id: str) -> dict[str, Any] | None:
    for rule in rules:
        if str(rule.get("userId") or "").strip() == user_id:
            return rule
    return None


def _allows_all(tokens: set[str]) -> bool:
    return not tokens or "*" in tokens


class AdvanceUsersService:
    """Resolve which customer/supplier/product ids a user may see."""

    def __init__(
        self,
        *,
        app_settings: AppSettingsService,
        prisma_client: Prisma,
        access_control: AccessControlService,
    ) -> None:
        self._settings = app_settings
        self._db = prisma_client
        self._access_control = access_control

    async def _membership_id(self, *, company_id: str, user_id: str) -> str | None:
        if self._db is None:
            return None
        row = await self._db.companymembership.find_unique(
            where={"companyId_userId": {"companyId": company_id, "userId": user_id}},
        )
        return row.id if row else None

    async def filter_customers(
        self, *, company_id: str, user_id: str, rows: list[T]
    ) -> list[T]:
        allowed = await self._allowed_tokens(
            company_id=company_id, user_id=user_id, field="customerIds", scope_type="customer"
        )
        return self._filter_rows(
            rows,
            allowed,
            id_getter=lambda r: str(getattr(r, "id", "")),
            code_getter=lambda r: str(getattr(r, "code", "")),
        )

    async def filter_suppliers(
        self, *, company_id: str, user_id: str, rows: list[T]
    ) -> list[T]:
        allowed = await self._allowed_tokens(
            company_id=company_id, user_id=user_id, field="supplierIds", scope_type="supplier"
        )
        return self._filter_rows(
            rows,
            allowed,
            id_getter=lambda r: str(getattr(r, "id", "")),
            code_getter=lambda r: str(getattr(r, "code", "")),
        )

    async def filter_products(
        self, *, company_id: str, user_id: str, rows: list[T]
    ) -> list[T]:
        allowed = await self._allowed_tokens(
            company_id=company_id, user_id=user_id, field="productIds", scope_type="product"
        )
        return self._filter_rows(
            rows,
            allowed,
            id_getter=lambda r: str(getattr(r, "id", "")),
            code_getter=lambda r: str(getattr(r, "code", "")),
        )

    async def _allowed_tokens(
        self,
        *,
        company_id: str,
        user_id: str,
        field: str,
        scope_type: str,
    ) -> set[str] | None:
        membership_id = await self._membership_id(company_id=company_id, user_id=user_id)
        if membership_id and self._access_control is not None:
            scoped = await self._access_control.allowed_scope_ids(
                company_id=company_id,
                membership_id=membership_id,
                scope_type=scope_type,
            )
            if scoped is not None:
                if "*" in scoped:
                    return None
                return set(scoped)

        payload = await self._settings.get_advance_users_settings(company_id=company_id)
        rules = payload.get("rules")
        if not isinstance(rules, list):
            return None
        rule = _rule_for_user(rules, user_id)
        if rule is None:
            return None
        tokens = _normalize_tokens(rule.get(field))
        if _allows_all(tokens):
            return None
        return tokens

    @staticmethod
    def _filter_rows(
        rows: list[T],
        allowed: set[str] | None,
        *,
        id_getter: Callable[[T], str],
        code_getter: Callable[[T], str],
    ) -> list[T]:
        if allowed is None:
            return rows
        out: list[T] = []
        for row in rows:
            rid = id_getter(row)
            code = code_getter(row)
            if rid in allowed or code in allowed:
                out.append(row)
        return out
