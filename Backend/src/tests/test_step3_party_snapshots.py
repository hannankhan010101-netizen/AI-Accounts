"""Step 3 party snapshot column locality validation."""

from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

os.environ.setdefault("SKIP_PRISMA", "1")

from app.repositories.sales_invoice_repository import SalesInvoiceRepository
from app.repositories.sql import aging_queries as aq
from app.services.activity_service import _sales_invoice_row
from app.services.party_snapshot_service import PartySnapshotService

MIGRATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "prisma"
    / "migrations"
    / "20260611120000_step3_party_snapshots"
    / "migration.sql"
)

PARTY_TABLES = (
    "sales_invoices",
    "sales_receipts",
    "sales_credits",
    "quotations",
    "sales_orders",
    "delivery_notes",
    "pdc_received",
    "supplier_bills",
    "supplier_payments",
    "supplier_credits",
    "purchase_orders",
    "goods_receipt_notes",
    "pdc_issued",
)


@pytest.fixture(scope="module")
def migration_sql() -> str:
    return MIGRATION_PATH.read_text(encoding="utf-8")


def test_migration_file_exists() -> None:
    assert MIGRATION_PATH.is_file()


def test_migration_adds_party_columns(migration_sql: str) -> None:
    assert "customer_code" in migration_sql
    assert "supplier_name" in migration_sql
    for table in PARTY_TABLES:
        assert f'"{table}"' in migration_sql


def test_migration_backfills_all_tables(migration_sql: str) -> None:
    updates = [line for line in migration_sql.splitlines() if line.strip().startswith("UPDATE")]
    assert len(updates) >= len(PARTY_TABLES)


def test_migration_recreates_ar_ap_mvs(migration_sql: str) -> None:
    assert "mv_ar_customer_open" in migration_sql
    assert "mv_ap_supplier_open" in migration_sql
    assert "MAX(si.\"customer_name\")" in migration_sql
    assert "MAX(sb.\"supplier_name\")" in migration_sql


def test_aging_merged_sql_uses_master_party_lookup() -> None:
    assert "FROM customers" in aq.AR_AGING_MERGED_SQL
    assert "FROM suppliers" in aq.AP_AGING_MERGED_SQL
    assert "LEFT JOIN customers" in aq.AR_AGING_FROM_MV_MERGED_SQL
    assert "LEFT JOIN suppliers" in aq.AP_AGING_FROM_MV_MERGED_SQL
    for sql in (
        aq.AR_AGING_MERGED_SQL,
        aq.AP_AGING_MERGED_SQL,
        aq.AR_AGING_FROM_MV_MERGED_SQL,
        aq.AP_AGING_FROM_MV_MERGED_SQL,
    ):
        lowered = sql.lower()
        assert "from supplier_bills" not in lowered or "supplier_code" not in lowered
        assert "from sales_invoices" not in lowered or "customer_code" not in lowered


@pytest.mark.asyncio
async def test_party_snapshot_service_customer() -> None:
    prisma = MagicMock()
    prisma.customer.find_unique = AsyncMock(
        return_value=SimpleNamespace(companyId="co1", code="C001", name="Acme Ltd")
    )
    svc = PartySnapshotService(prisma)
    code, name = await svc.customer_snapshot(company_id="co1", customer_id="cust1")
    assert code == "C001"
    assert name == "Acme Ltd"


@pytest.mark.asyncio
async def test_party_snapshot_service_rejects_wrong_company() -> None:
    from app.core.exceptions import ValidationAppError

    prisma = MagicMock()
    prisma.customer.find_unique = AsyncMock(
        return_value=SimpleNamespace(companyId="other", code="C001", name="Acme Ltd")
    )
    svc = PartySnapshotService(prisma)
    with pytest.raises(ValidationAppError):
        await svc.customer_snapshot(company_id="co1", customer_id="cust1")


@pytest.mark.asyncio
async def test_create_invoice_sets_party_snapshot() -> None:
    prisma = MagicMock()
    prisma.customer.find_unique = AsyncMock(
        return_value=SimpleNamespace(companyId="co1", code="C001", name="Acme Ltd")
    )
    captured: dict = {}

    async def _create(**kwargs: object) -> MagicMock:
        captured.update(kwargs)
        return MagicMock()

    prisma.salesinvoice.create = AsyncMock(side_effect=_create)
    repo = SalesInvoiceRepository(prisma)
    await repo.create_invoice(
        company_id="co1",
        invoice_number="SI-1",
        invoice_date=MagicMock(),
        customer_id="cust1",
        lines=[{"lineTotal": "100"}],
    )
    data = captured["data"]
    assert data["customerCode"] == "C001"
    assert data["customerName"] == "Acme Ltd"


def test_activity_row_includes_party_fields() -> None:
    inv = MagicMock(
        id="inv1",
        invoiceNumber="SI-1",
        invoiceDate=MagicMock(isoformat=lambda: "2026-01-01T00:00:00"),
        customerId="cust1",
        customerCode="C001",
        customerName="Acme Ltd",
        totalAmount="100",
        status="posted",
    )
    row = _sales_invoice_row(inv)
    assert row["partyCode"] == "C001"
    assert row["partyName"] == "Acme Ltd"
