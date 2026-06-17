"""P4 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.core.exceptions import ValidationAppError
from app.domain import document_workflow as wf
from app.repositories.journal_repository import JournalRepository


@pytest.mark.asyncio
async def test_openapi_p4_routes_registered() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/assembly/templates" in paths
    assert "/api/v1/companies/{company_id}/bank/fx-revaluations" in paths
    assert "/api/v1/companies/{company_id}/sales-invoices/{invoice_id}/fbr/submit" in paths
    assert "/api/v1/companies/{company_id}/lock-date/users/{user_id}" in paths


def test_assembly_and_fx_source_types() -> None:
    assert wf.SOURCE_ASSEMBLY_JOB == "ASSEMBLY_JOB"
    assert wf.SOURCE_FX_REVALUATION == "FX_REVALUATION"


def test_journal_assert_mutable_raises_for_posted() -> None:
    async def _run() -> None:
        repo = JournalRepository(None)  # type: ignore[arg-type]

        class _Journal:
            status = "posted"
            reversesJournalId = None

        async def fake_get(*, company_id: str, journal_id: str):
            _ = company_id, journal_id
            return _Journal()

        repo.get_by_id = fake_get  # type: ignore[method-assign]
        with pytest.raises(ValidationAppError):
            await repo.assert_mutable(company_id="c1", journal_id="j1")

    import asyncio

    asyncio.get_event_loop().run_until_complete(_run())


def test_report_pdf_generates_bytes() -> None:
    pytest.importorskip("fpdf")
    from app.services.report_pdf_service import rows_to_pdf

    pdf = rows_to_pdf(title="Test", rows=[{"code": "1000", "name": "Cash"}])
    assert pdf[:4] == b"%PDF"
