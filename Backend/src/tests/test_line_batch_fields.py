"""Batch/expiry fields merged onto taxed invoice lines."""

from datetime import datetime, timezone

from app.models.requests.sales_requests import SalesInvoiceLineRequest
from app.utils.line_description import merge_line_description_fields


def test_merge_batch_and_expiry_on_repo_lines() -> None:
    repo_lines = [{"productCode": "P1", "lineTotal": 100}]
    req = SalesInvoiceLineRequest(
        productCode="P1",
        quantity=1,
        rate=100,
        batchNumber="B-42",
        expiryDate=datetime(2026, 6, 1, tzinfo=timezone.utc),
    )
    merged = merge_line_description_fields(repo_lines, [req])
    assert merged[0]["batchNumber"] == "B-42"
    assert merged[0]["expiryDate"] == req.expiry_date
