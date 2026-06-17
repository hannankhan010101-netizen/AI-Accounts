"""Journal bulk import groups lines and enforces balance."""

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.import_handlers import _import_journals


@pytest.mark.asyncio
async def test_import_journals_groups_and_balances() -> None:
    db = AsyncMock()
    seq = MagicMock()
    seq.nextValue = 10
    db.documentnumbersequence.find_unique.return_value = seq
    created = MagicMock()
    repo_create = AsyncMock(return_value=created)

    with patch(
        "app.services.import_handlers.JournalRepository.create_with_lines",
        repo_create,
    ):
        result = await _import_journals(
            db=db,
            company_id="co1",
            rows=[
                {
                    "journalRef": "J1",
                    "journalDate": "2026-01-15",
                    "nominalCode": "1000",
                    "debit": "500",
                    "credit": "0",
                },
                {
                    "journalRef": "J1",
                    "nominalCode": "2000",
                    "debit": "0",
                    "credit": "500",
                },
            ],
        )

    assert result.created == 1
    assert result.skipped == 0
    repo_create.assert_awaited_once()
    call_kw = repo_create.await_args.kwargs
    assert call_kw["total_amount"] == Decimal("500")
