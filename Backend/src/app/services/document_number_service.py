"""Expose atomic numbering to voucher services."""

from __future__ import annotations

from app.repositories.document_number_repository import DocumentNumberRepository


class DocumentNumberService:
    """Facade over ``DocumentNumberRepository`` for routes."""

    def __init__(self, *, document_number_repository: DocumentNumberRepository) -> None:
        self._repo = document_number_repository

    async def reserve_next(self, *, company_id: str, sequence_key: str) -> int:
        """Return the next issued integer for a logical sequence key."""

        return await self._repo.reserve_next(company_id=company_id, sequence_key=sequence_key)
