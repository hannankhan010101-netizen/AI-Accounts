"""Evaluate approval policies before posting high-value documents — P3 / RBAC v2."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from app.core.exceptions import ValidationAppError
from app.repositories.approval_policy_repository import ApprovalPolicyRepository
from app.repositories.approval_request_repository import ApprovalRequestRepository
from app.repositories.membership_role_repository import MembershipRoleRepository
from prisma_generated import Prisma


class ApprovalEngineService:
    def __init__(
        self,
        *,
        policy_repository: ApprovalPolicyRepository,
        request_repository: ApprovalRequestRepository,
        prisma_client: Prisma,
        membership_roles: MembershipRoleRepository,
    ) -> None:
        self._policies = policy_repository
        self._requests = request_repository
        self._db = prisma_client
        self._membership_roles = membership_roles

    def _threshold(self, rules: dict[str, Any]) -> Decimal | None:
        levels = rules.get("levels")
        if isinstance(levels, list) and levels:
            mins: list[Decimal] = []
            for level in levels:
                if not isinstance(level, dict):
                    continue
                raw = level.get("minAmount")
                if raw is not None:
                    try:
                        mins.append(Decimal(str(raw)))
                    except Exception:  # noqa: BLE001
                        continue
            if mins:
                return min(mins)
        raw = rules.get("minAmount") or rules.get("requiresApprovalAbove")
        if raw is None:
            return None
        try:
            return Decimal(str(raw))
        except Exception:  # noqa: BLE001
            return None

    def _levels_for_amount(self, rules: dict[str, Any], amount: Decimal) -> list[dict[str, Any]]:
        levels = rules.get("levels")
        if not isinstance(levels, list):
            return []
        applicable: list[dict[str, Any]] = []
        for level in levels:
            if not isinstance(level, dict):
                continue
            try:
                min_amount = Decimal(str(level.get("minAmount", 0)))
            except Exception:  # noqa: BLE001
                min_amount = Decimal(0)
            if amount >= min_amount:
                applicable.append(level)
        return applicable

    async def _user_role_ids(self, *, company_id: str, user_id: str) -> set[str]:
        membership = await self._db.companymembership.find_unique(
            where={"companyId_userId": {"companyId": company_id, "userId": user_id}},
        )
        if membership is None:
            return set()
        role_ids = await self._membership_roles.list_role_ids(membership_id=membership.id)
        if not role_ids and membership.roleId:
            role_ids = [membership.roleId]
        return set(role_ids)

    async def assert_can_approve(
        self,
        *,
        company_id: str,
        user_id: str,
        entity_type: str,
        amount: Decimal,
    ) -> None:
        rules = await self._policy_for(company_id=company_id, entity_type=entity_type)
        levels = self._levels_for_amount(rules, amount)
        if not levels:
            return
        user_roles = await self._user_role_ids(company_id=company_id, user_id=user_id)
        allowed: set[str] = set()
        for level in levels:
            for rid in level.get("approverRoleIds") or []:
                allowed.add(str(rid))
        if not allowed:
            return
        if user_roles.intersection(allowed):
            return
        raise ValidationAppError("You are not authorized to approve this request.")

    async def _policy_for(self, *, company_id: str, entity_type: str) -> dict[str, Any]:
        policies = await self._policies.list_for_company(company_id=company_id)
        for p in policies:
            if p.entityType == entity_type:
                return p.rules if isinstance(p.rules, dict) else {}
        return {}

    async def requires_approval(
        self, *, company_id: str, entity_type: str, amount: Decimal
    ) -> bool:
        rules = await self._policy_for(company_id=company_id, entity_type=entity_type)
        threshold = self._threshold(rules)
        if threshold is None:
            return False
        return amount >= threshold

    async def assert_can_post(
        self,
        *,
        company_id: str,
        entity_type: str,
        entity_id: str,
        amount: Decimal,
    ) -> None:
        """Raise when policy requires approval and no approved request exists."""

        if not await self.requires_approval(
            company_id=company_id, entity_type=entity_type, amount=amount
        ):
            return
        approved = await self._requests.find_approved_for_entity(
            company_id=company_id,
            entity_type=entity_type,
            entity_id=entity_id,
        )
        if approved is None:
            raise ValidationAppError(
                "Document exceeds approval threshold. Submit an approval request first."
            )

    async def list_requests(self, *, company_id: str, status: str | None = None):
        return await self._requests.list_for_company(
            company_id=company_id, status=status
        )

    async def submit_request(
        self,
        *,
        company_id: str,
        entity_type: str,
        entity_id: str,
        amount: Decimal,
        requested_by_id: str | None,
        notes: str | None = None,
    ):
        if not await self.requires_approval(
            company_id=company_id, entity_type=entity_type, amount=amount
        ):
            raise ValidationAppError("This document does not require approval")
        return await self._requests.create_pending(
            company_id=company_id,
            entity_type=entity_type,
            entity_id=entity_id,
            amount=amount,
            requested_by_id=requested_by_id,
            notes=notes,
        )

    async def get_request(self, *, company_id: str, request_id: str):
        return await self._requests.get_by_id(
            company_id=company_id, request_id=request_id
        )

    async def approve_request(
        self,
        *,
        company_id: str,
        request_id: str,
        approved_by_id: str | None,
    ):
        row = await self._requests.get_by_id(
            company_id=company_id, request_id=request_id
        )
        if row is None:
            raise ValidationAppError("Approval request not found")
        if row.status != "pending":
            raise ValidationAppError(f"Request is already {row.status}")
        return await self._requests.mark_approved(
            request_id=request_id,
            approved_by_id=approved_by_id,
            approved_at=datetime.now(timezone.utc),
        )

    async def reject_request(self, *, company_id: str, request_id: str):
        row = await self._requests.get_by_id(
            company_id=company_id, request_id=request_id
        )
        if row is None:
            raise ValidationAppError("Approval request not found")
        if row.status != "pending":
            raise ValidationAppError(f"Request is already {row.status}")
        return await self._requests.mark_rejected(request_id=request_id)
