"""Per-user onboarding / tour progress — P48."""

from __future__ import annotations

from typing import Any

from prisma_generated import Prisma
from prisma_generated.errors import TableNotFoundError

from app.core.prisma_data import json_field

DEFAULT_PAYLOAD: dict[str, Any] = {
    "tours": {},
    "maturityScore": 0,
    "dismissedHints": [],
    "eventLog": [],
    "preferences": {"emailDigestEnabled": False, "lastDigestSentAt": None},
}


class OnboardingRepository:
    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def get_payload(self, *, company_id: str, user_id: str) -> dict[str, Any]:
        try:
            row = await self._db.useronboardingstate.find_unique(
                where={"companyId_userId": {"companyId": company_id, "userId": user_id}},
            )
        except TableNotFoundError:
            return dict(DEFAULT_PAYLOAD)
        if row is None or not isinstance(row.payload, dict):
            return dict(DEFAULT_PAYLOAD)
        merged = dict(DEFAULT_PAYLOAD)
        merged.update(row.payload)
        if not isinstance(merged.get("tours"), dict):
            merged["tours"] = {}
        if not isinstance(merged.get("dismissedHints"), list):
            merged["dismissedHints"] = []
        if not isinstance(merged.get("eventLog"), list):
            merged["eventLog"] = []
        prefs = merged.get("preferences")
        if not isinstance(prefs, dict):
            merged["preferences"] = dict(DEFAULT_PAYLOAD["preferences"])
        return merged

    async def upsert_payload(
        self, *, company_id: str, user_id: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        try:
            row = await self._db.useronboardingstate.upsert(
                where={"companyId_userId": {"companyId": company_id, "userId": user_id}},
                data={
                    "create": {
                        "companyId": company_id,
                        "userId": user_id,
                        "payload": json_field(payload),
                    },
                    "update": {"payload": json_field(payload)},
                },
            )
        except TableNotFoundError:
            return payload
        out = row.payload if isinstance(row.payload, dict) else dict(DEFAULT_PAYLOAD)
        return out

    async def append_events(
        self,
        *,
        company_id: str,
        user_id: str,
        events: list[dict[str, Any]],
        max_log: int = 100,
    ) -> dict[str, Any]:
        payload = await self.get_payload(company_id=company_id, user_id=user_id)
        log = payload.get("eventLog")
        if not isinstance(log, list):
            log = []
        log = [*log, *events]
        payload["eventLog"] = log[-max_log:]
        return await self.upsert_payload(
            company_id=company_id, user_id=user_id, payload=payload
        )

    async def list_company_payloads(self, *, company_id: str) -> list[dict[str, Any]]:
        rows = await self._db.useronboardingstate.find_many(
            where={"companyId": company_id},
        )
        out: list[dict[str, Any]] = []
        for row in rows:
            if isinstance(row.payload, dict):
                out.append(row.payload)
            else:
                out.append(dict(DEFAULT_PAYLOAD))
        return out
