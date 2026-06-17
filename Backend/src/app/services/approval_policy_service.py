"""Authorisation policy documents."""

from __future__ import annotations

from app.repositories.approval_policy_repository import ApprovalPolicyRepository


class ApprovalPolicyService:
    """Load and replace approval matrices."""

    def __init__(self, *, approval_policy_repository: ApprovalPolicyRepository) -> None:
        self._repo = approval_policy_repository

    async def list_policies(self, *, company_id: str):
        """Return all configured entity policies."""

        return await self._repo.list_for_company(company_id=company_id)

    async def upsert_policy(self, *, company_id: str, entity_type: str, rules: dict):
        """Replace JSON rules for one entity family."""

        return await self._repo.upsert(
            company_id=company_id,
            entity_type=entity_type,
            rules=rules,
        )
