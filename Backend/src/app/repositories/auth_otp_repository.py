"""Persisted email OTP challenges (signup and password reset)."""

from __future__ import annotations

from datetime import datetime

from prisma_generated import Prisma
from prisma_generated.models import AuthOtpChallenge


class AuthOtpRepository:
    """Create and clear OTP rows bound to a user."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def delete_for_user_purpose(self, *, user_id: str, purpose: str) -> None:
        """Remove all challenges for this user and purpose before issuing a new code."""

        await self._db.authotpchallenge.delete_many(where={"userId": user_id, "purpose": purpose})

    async def create(
        self,
        *,
        user_id: str,
        purpose: str,
        code_hash: str,
        expires_at: datetime,
    ) -> AuthOtpChallenge:
        """Insert a new active challenge."""

        return await self._db.authotpchallenge.create(
            data={
                "userId": user_id,
                "purpose": purpose,
                "codeHash": code_hash,
                "expiresAt": expires_at,
            }
        )

    async def find_latest_for_user_purpose(
        self,
        *,
        user_id: str,
        purpose: str,
    ) -> AuthOtpChallenge | None:
        """Return the newest challenge row for verification attempts."""

        rows = await self._db.authotpchallenge.find_many(
            where={"userId": user_id, "purpose": purpose},
            order={"createdAt": "desc"},
            take=1,
        )
        return rows[0] if rows else None
