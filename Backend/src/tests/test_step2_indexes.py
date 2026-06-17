"""Step 2 composite index migration validation."""

from __future__ import annotations

import os
import re
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

os.environ.setdefault("SKIP_PRISMA", "1")

from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.sql.index_registry import (
    MIGRATION_ONLY_INDEXES,
    STEP2_INDEX_REGISTRY,
    step2_index_names,
)

MIGRATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "prisma"
    / "migrations"
    / "20260610120000_step2_composite_indexes"
    / "migration.sql"
)
SCHEMA_PATH = Path(__file__).resolve().parents[2] / "prisma" / "schema.prisma"


@pytest.fixture(scope="module")
def migration_sql() -> str:
    return MIGRATION_PATH.read_text(encoding="utf-8")


def test_migration_file_exists() -> None:
    assert MIGRATION_PATH.is_file()


def test_pg_trgm_extension_in_migration(migration_sql: str) -> None:
    assert "CREATE EXTENSION IF NOT EXISTS pg_trgm" in migration_sql


def test_all_registry_indexes_in_migration(migration_sql: str) -> None:
    missing = [
        name for name in step2_index_names() if name not in migration_sql
    ]
    assert not missing, f"Missing indexes in migration: {missing}"


def test_all_migration_indexes_in_registry(migration_sql: str) -> None:
    created = re.findall(r'CREATE INDEX IF NOT EXISTS "([^"]+)"', migration_sql)
    extra = [name for name in created if name not in STEP2_INDEX_REGISTRY]
    assert not extra, f"Migration indexes missing from registry: {extra}"


def test_schema_has_no_migration_only_indexes() -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    schema_idxs = set(re.findall(r'map: "(idx_step2_[^"]+)"', schema))
    drift = sorted(MIGRATION_ONLY_INDEXES & schema_idxs)
    assert not drift, f"Partial/GIN indexes must not be in schema.prisma: {drift}"


def test_schema_covers_btree_step2_indexes() -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    schema_idxs = set(re.findall(r'map: "(idx_step2_[^"]+)"', schema))
    expected = set(STEP2_INDEX_REGISTRY) - MIGRATION_ONLY_INDEXES
    missing = sorted(expected - schema_idxs)
    assert not missing, f"B-tree Step 2 indexes missing from schema: {missing}"


def test_keyset_indexes_present(migration_sql: str) -> None:
    assert "idx_step2_si_keyset" in migration_sql
    assert '"invoice_date" DESC, "id" DESC' in migration_sql


def test_trgm_gin_indexes_present(migration_sql: str) -> None:
    assert "gin_trgm_ops" in migration_sql
    assert "idx_step2_users_email_trgm" in migration_sql


def test_partial_draft_indexes_present(migration_sql: str) -> None:
    assert "idx_step2_journals_draft" in migration_sql
    assert 'WHERE "status" = \'draft\'' in migration_sql


def test_registry_covers_migration_only_set() -> None:
    for name in MIGRATION_ONLY_INDEXES:
        assert name in STEP2_INDEX_REGISTRY


@pytest.mark.asyncio
async def test_audit_log_type_contains_filter_unchanged() -> None:
    prisma = MagicMock()
    captured: dict = {}

    async def _find_many(**kwargs: object) -> list:
        captured.update(kwargs)
        return []

    prisma.auditlogentry.find_many = AsyncMock(side_effect=_find_many)
    repo = AuditLogRepository(prisma)
    await repo.list_filtered(
        company_id="co1",
        user_id=None,
        date_from=None,
        date_to=None,
        transaction_type_contains="BANK",
    )
    assert captured["where"]["transactionType"] == {"contains": "BANK"}
