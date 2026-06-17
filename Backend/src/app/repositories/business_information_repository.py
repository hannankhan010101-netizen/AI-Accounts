"""Business profile for prints and compliance."""

from __future__ import annotations

from typing import Any

from prisma_generated import Prisma
from prisma_generated.models import BusinessInformation


class BusinessInformationRepository:
    """Company legal/trading identity."""

    _ALLOWED_KEYS: frozenset[str] = frozenset(
        {
            "businessName",
            "addressLine1",
            "addressLine2",
            "addressLine3",
            "addressLine4",
            "addressLine5",
            "branchName",
            "phoneNumber",
            "mobileNumber",
            "emailAddress",
            "websiteAddress",
            "logoUrl",
            "cnic",
            "stn",
            "ntn",
            "applyOnAllPrints",
        }
    )

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def get_for_company(self, *, company_id: str) -> BusinessInformation | None:
        """Return business information row."""

        return await self._db.businessinformation.find_unique(where={"companyId": company_id})

    async def upsert_fields(self, *, company_id: str, fields: dict[str, Any]) -> BusinessInformation:
        """Merge scalar fields into the profile."""

        clean = {k: v for k, v in fields.items() if k in self._ALLOWED_KEYS}
        return await self._db.businessinformation.upsert(
            where={"companyId": company_id},
            data={
                "create": {"companyId": company_id, **clean},
                "update": clean,
            },
        )
