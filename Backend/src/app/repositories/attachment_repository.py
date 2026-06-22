"""Persistence for polymorphic attachments."""

from __future__ import annotations

from prisma_generated import Prisma
from prisma_generated.models import Attachment


class AttachmentRepository:
    """Load and store attachment rows for any voucher or master entity."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_for_entity(
        self,
        *,
        company_id: str,
        entity_type: str,
        entity_id: str,
    ) -> list[Attachment]:
        """Return attachments linked to a single business object."""

        return await self._db.attachment.find_many(
            where={
                "companyId": company_id,
                "entityType": entity_type,
                "entityId": entity_id,
            },
            order={"createdAt": "desc"},
            take=100,
        )

    async def create(
        self,
        *,
        company_id: str,
        entity_type: str,
        entity_id: str,
        file_name: str,
        storage_key: str,
        mime_type: str | None,
        byte_size: int,
    ) -> Attachment:
        """Insert attachment metadata after blob upload."""

        return await self._db.attachment.create(
            data={
                "companyId": company_id,
                "entityType": entity_type,
                "entityId": entity_id,
                "fileName": file_name,
                "storageKey": storage_key,
                "mimeType": mime_type,
                "byteSize": byte_size,
            }
        )

    async def get_by_id(self, *, company_id: str, attachment_id: str) -> Attachment | None:
        return await self._db.attachment.find_first(
            where={"id": attachment_id, "companyId": company_id},
        )

    async def delete(self, *, company_id: str, attachment_id: str) -> bool:
        row = await self.get_by_id(company_id=company_id, attachment_id=attachment_id)
        if row is None:
            return False
        await self._db.attachment.delete(where={"id": attachment_id})
        return True
