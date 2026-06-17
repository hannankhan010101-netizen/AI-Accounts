"""Report sync export — P4 / §4.6."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

from app.services.report_service import ReportService


def test_format_rows_export_csv() -> None:
    rows = [{"a": 1, "b": "x"}, {"a": 2, "b": "y"}]
    out = ReportService.format_rows_export(rows=rows, export_format="csv", title="T")
    assert out.content is not None
    assert "a,b" in out.content
    assert "1,x" in out.content


def test_format_rows_export_json() -> None:
    rows = [{"productCode": "SKU-1"}]
    out = ReportService.format_rows_export(rows=rows, export_format="json", title="T")
    assert out.content is not None
    assert "SKU-1" in out.content
