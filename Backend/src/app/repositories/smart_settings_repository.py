"""Smart Settings JSON document."""

from __future__ import annotations

from typing import Any

from prisma_generated import Prisma
from prisma_generated.fields import Json
from prisma_generated.models import SmartSettings


class SmartSettingsRepository:
    """Load and replace Smart Settings accordion payload."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def get_for_company(self, *, company_id: str) -> SmartSettings | None:
        """Return settings row or ``None`` if missing."""

        return await self._db.smartsettings.find_unique(where={"companyId": company_id})

    async def upsert_payload(self, *, company_id: str, payload: dict[str, Any]) -> SmartSettings:
        """Create or replace the JSON payload."""

        return await self._db.smartsettings.upsert(
            where={"companyId": company_id},
            data={
                "create": {"companyId": company_id, "payload": Json(payload)},
                "update": {"payload": Json(payload)},
            },
        )

    async def merge_payload(self, *, company_id: str, patch: dict[str, Any]) -> SmartSettings:
        """Shallow-merge keys into the existing payload."""

        existing = await self.get_for_company(company_id=company_id)
        base: dict[str, Any] = (
            dict(existing.payload) if existing and isinstance(existing.payload, dict) else {}
        )
        base.update(patch)
        return await self.upsert_payload(company_id=company_id, payload=base)
