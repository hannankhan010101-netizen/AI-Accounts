"""Attachment orchestration."""

from __future__ import annotations

from app.repositories.attachment_repository import AttachmentRepository
from app.services.attachment_storage import resolve_path, save_upload


class AttachmentService:
    """Tenant-scoped attachment listing and registration."""

    def __init__(self, *, attachment_repository: AttachmentRepository) -> None:
        self._repo = attachment_repository

    async def list_attachments(
        self,
        *,
        company_id: str,
        entity_type: str,
        entity_id: str,
    ):
        """Return metadata rows for one host entity."""

        return await self._repo.list_for_entity(
            company_id=company_id,
            entity_type=entity_type,
            entity_id=entity_id,
        )

    async def register_attachment(
        self,
        *,
        company_id: str,
        entity_type: str,
        entity_id: str,
        file_name: str,
        storage_key: str,
        mime_type: str | None,
        byte_size: int,
    ):
        """Persist attachment row after storage upload."""

        return await self._repo.create(
            company_id=company_id,
            entity_type=entity_type,
            entity_id=entity_id,
            file_name=file_name,
            storage_key=storage_key,
            mime_type=mime_type,
            byte_size=byte_size,
        )

    async def upload_file(
        self,
        *,
        company_id: str,
        entity_type: str,
        entity_id: str,
        file_name: str,
        data: bytes,
        mime_type: str | None,
    ):
        storage_key, _path = save_upload(
            company_id=company_id,
            file_name=file_name,
            data=data,
        )
        return await self.register_attachment(
            company_id=company_id,
            entity_type=entity_type,
            entity_id=entity_id,
            file_name=file_name,
            storage_key=storage_key,
            mime_type=mime_type,
            byte_size=len(data),
        )

    async def open_file(self, *, company_id: str, attachment_id: str):
        row = await self._repo.get_by_id(company_id=company_id, attachment_id=attachment_id)
        if row is None:
            return None, None
        path = resolve_path(row.storageKey)
        if not path.is_file():
            return row, None
        return row, path
