"""P20 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.repositories.delivery_repository import DeliveryNoteRepository
from app.repositories.goods_issue_repository import GoodsIssueRepository
from app.services.document_reversal_service import DocumentReversalService


def test_delivery_note_repo_has_source_list() -> None:
    assert hasattr(DeliveryNoteRepository, "list_by_source")
    assert hasattr(DeliveryNoteRepository, "update_status")


def test_goods_issue_repo_has_journal_update() -> None:
    assert hasattr(GoodsIssueRepository, "update_journal_id")


def test_document_reversal_p20_methods() -> None:
    assert hasattr(DocumentReversalService, "void_delivery_note")
    assert hasattr(DocumentReversalService, "void_delivery_notes_for_sales_order")
    assert hasattr(DocumentReversalService, "repost_remaining_goods_issue_cogs")


@pytest.mark.asyncio
async def test_openapi_p20_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/delivery-notes/{note_id}/void" in paths
    assert (
        "/api/v1/companies/{company_id}/sales-invoices/{invoice_id}/goods-issue/repost-remaining-cogs"
        in paths
    )
