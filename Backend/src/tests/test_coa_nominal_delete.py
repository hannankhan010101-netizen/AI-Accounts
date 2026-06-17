from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.coa_repository import CoaRepository


@pytest.mark.asyncio
async def test_delete_nominal_blocks_when_journal_lines_exist() -> None:
    db = AsyncMock()
    nominal = MagicMock()
    nominal.code = "4000"
    nominal.section.category.companyId = "co1"
    db.nominalaccount.find_unique = AsyncMock(return_value=nominal)
    db.journalline.count = AsyncMock(return_value=3)

    repo = CoaRepository(db)
    with pytest.raises(ValueError, match="journal line"):
        await repo.delete_nominal(company_id="co1", nominal_id="nom1")


@pytest.mark.asyncio
async def test_delete_nominal_succeeds_when_unused() -> None:
    db = AsyncMock()
    nominal = MagicMock()
    nominal.code = "4000"
    nominal.section.category.companyId = "co1"
    db.nominalaccount.find_unique = AsyncMock(return_value=nominal)
    db.journalline.count = AsyncMock(return_value=0)
    db.nominalaccount.delete = AsyncMock()

    repo = CoaRepository(db)
    await repo.delete_nominal(company_id="co1", nominal_id="nom1")
    db.nominalaccount.delete.assert_awaited_once_with(where={"id": "nom1"})


@pytest.mark.asyncio
async def test_bulk_delete_nominals_counts_skipped() -> None:
    db = AsyncMock()
    repo = CoaRepository(db)
    repo.delete_nominal = AsyncMock(side_effect=[None, ValueError("in use")])

    result = await repo.bulk_delete_nominals(
        company_id="co1", nominal_ids=["a", "b"]
    )
    assert result == {"deleted": 1, "skipped": 1}
