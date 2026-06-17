"""P24 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.services.document_reversal_service import DocumentReversalService


def test_document_reversal_void_grn() -> None:
    assert hasattr(DocumentReversalService, "void_goods_receipt_note")


@pytest.mark.asyncio
async def test_openapi_grn_void_route() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/goods-receipt-notes/{note_id}/void" in paths


def test_permission_seed_doc_exists() -> None:
    from pathlib import Path

    doc = Path(__file__).resolve().parents[2] / "docs" / "PERMISSION-SEED.md"
    assert doc.is_file()
    assert "Administrator" in doc.read_text(encoding="utf-8")
