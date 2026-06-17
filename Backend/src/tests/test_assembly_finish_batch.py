from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.assembly_service import AssemblyService


def _assembly_service(*, assembly_repo: MagicMock) -> AssemblyService:
    return AssemblyService(
        assembly_repository=assembly_repo,
        product_repository=MagicMock(),
        document_number_service=MagicMock(reserve_next=AsyncMock(return_value=1)),
        posting_service=MagicMock(
            create_traced_journal=AsyncMock(return_value=MagicMock(id="j1"))
        ),
        prerequisites=MagicMock(
            require_stock_adjustment_posting=AsyncMock(
                return_value={"inventoryNominalCode": "1300"}
            )
        ),
    )


@pytest.mark.asyncio
async def test_finish_job_creates_product_batch_when_batch_set() -> None:
    job = MagicMock(
        id="job1",
        jobNumber="AJ-1",
        jobDate=MagicMock(),
        finishedProductCode="FIN1",
        quantity=Decimal("5"),
        status="draft",
        journalId=None,
        batchNumber="BATCH-A",
        expiryDate=None,
        lines=[MagicMock(quantity=Decimal("1"), unitCost=Decimal("10"), componentProductCode="C1")],
    )
    assembly_repo = MagicMock()
    assembly_repo.get_job = AsyncMock(return_value=job)
    assembly_repo.mark_finished = AsyncMock(return_value=job)
    assembly_repo._db = AsyncMock()
    assembly_repo._db.productbatch.find_first = AsyncMock(return_value=None)
    assembly_repo._db.productbatch.create = AsyncMock()

    svc = _assembly_service(assembly_repo=assembly_repo)
    await svc.finish_job(company_id="co1", job_id="job1")

    assembly_repo._db.productbatch.create.assert_awaited_once()
    data = assembly_repo._db.productbatch.create.call_args.kwargs["data"]
    assert data["productCode"] == "FIN1"
    assert data["batchNumber"] == "BATCH-A"
    assert data["quantityOnHand"] == Decimal("5")
