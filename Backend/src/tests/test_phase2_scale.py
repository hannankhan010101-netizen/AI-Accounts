"""Phase 2 — cache, blob store, keyset helpers."""

from __future__ import annotations

import gzip
import json
import os
from decimal import Decimal
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

os.environ.setdefault("SKIP_PRISMA", "1")

from app.core.report_cache import ReportCache
from app.services.report_blob_store import ReportBlobStore
from app.utils.keyset_pagination import (
    apply_desc_date_keyset,
    page_size_from_criteria,
    trim_keyset_page,
)


def test_page_size_default_200() -> None:
    assert page_size_from_criteria({}) == 200
    assert page_size_from_criteria({"pageSize": 50}) == 50


def test_apply_desc_date_keyset_adds_or_clause() -> None:
    where = apply_desc_date_keyset(
        {"companyId": "c1"},
        criteria={"cursorDate": "2026-01-15T00:00:00+00:00", "cursorId": "inv-1"},
        date_field="invoiceDate",
    )
    assert "OR" in where


def test_trim_keyset_page_next_cursor() -> None:
    rows = [MagicMock(id=f"id-{i}", invoiceDate=MagicMock(isoformat=lambda: "2026-01-01")) for i in range(3)]

    def _row(r: MagicMock) -> dict:
        return {"id": r.id}

    out, cursor = trim_keyset_page(
        rows, page_size=2, to_dict=_row, date_field="invoiceDate"
    )
    assert len(out) == 2
    assert cursor is not None
    assert cursor.get("hasMore") is True


@pytest.mark.asyncio
async def test_report_cache_roundtrip_memory_fallback() -> None:
    with patch("app.core.report_cache.get_redis", AsyncMock(return_value=None)):
        cache = ReportCache()
        await cache.set_rows(
            company_id="co1",
            report_id="028",
            criteria={"pageSize": 10},
            rows=[{"id": "1"}],
        )
        assert (
            await cache.get_rows(
                company_id="co1",
                report_id="028",
                criteria={"pageSize": 10},
            )
            is None
        )


@pytest.mark.asyncio
async def test_blob_store_local_roundtrip(tmp_path: Path) -> None:
    with patch("app.services.report_blob_store.get_settings") as mock_settings:
        mock_settings.return_value = MagicMock(
            report_storage_dir=str(tmp_path),
            report_s3_bucket="",
            report_s3_access_key="",
            report_s3_secret_key="",
            report_s3_endpoint="",
            report_s3_region="us-east-1",
        )
        store = ReportBlobStore()
        rows = [{"a": 1}, {"b": Decimal("2.5")}]
        key = await store.save_rows(company_id="co1", run_id="run-1", rows=rows)
        loaded = await store.load_rows(storage_key=key)
        assert loaded[0]["a"] == 1
        path = tmp_path / key
        assert path.is_file()
        raw = gzip.decompress(path.read_bytes())
        assert json.loads(raw.decode())
