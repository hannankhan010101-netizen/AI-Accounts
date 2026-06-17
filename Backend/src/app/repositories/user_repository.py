"""User identity rows."""

from __future__ import annotations

from prisma_generated import Prisma
from prisma_generated.models import User


class UserRepository:
    """CRUD helpers for login identity."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def find_by_id(self, *, user_id: str) -> User | None:
        """Locate a user by primary key."""

        return await self._db.user.find_unique(where={"id": user_id})

    async def find_by_email(self, *, email: str) -> User | None:
        """Locate a user by normalized email."""

        return await self._db.user.find_unique(where={"email": email})

    async def create(
        self,
        *,
        email: str,
        password_hash: str,
        first_name: str,
        last_name: str,
        phone: str | None = None,
        email_verified: bool = True,
    ) -> User:
        """Insert a new interactive user."""

        return await self._db.user.create(
            data={
                "email": email,
                "passwordHash": password_hash,
                "firstName": first_name,
                "lastName": last_name,
                "phone": phone,
                "emailVerified": email_verified,
            }
        )

    async def update_email_verified(self, *, user_id: str, verified: bool) -> User:
        """Flip email verification after successful OTP."""

        return await self._db.user.update(
            where={"id": user_id},
            data={"emailVerified": verified},
        )

    async def update_password_hash(self, *, user_id: str, password_hash: str) -> User:
        """Apply a new password hash after reset."""

        return await self._db.user.update(
            where={"id": user_id},
            data={"passwordHash": password_hash},
        )

    async def update_profile(
        self,
        *,
        user_id: str,
        first_name: str | None = None,
        last_name: str | None = None,
        phone: str | None = None,
    ) -> User:
        """Patch profile fields for the signed-in user."""

        data: dict[str, object] = {}
        if first_name is not None:
            data["firstName"] = first_name
        if last_name is not None:
            data["lastName"] = last_name
        if phone is not None:
            data["phone"] = phone or None
        if not data:
            user = await self.find_by_id(user_id=user_id)
            if user is None:
                raise ValueError("User not found")
            return user
        return await self._db.user.update(where={"id": user_id}, data=data)
