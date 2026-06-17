"""Activity list filter helpers — Sales All / Purchases All."""

from datetime import datetime, timezone

from app.services.activity_filters import (
    activity_where,
    filter_activity_rows,
    parse_activity_date,
)


def test_parse_activity_date_end_of_day() -> None:
    dt = parse_activity_date("2026-01-15", end_of_day=True)
    assert dt is not None
    assert dt.day == 15
    assert dt.hour == 23


def test_activity_where_party_and_status() -> None:
    where = activity_where(
        company_id="co1",
        party_field="customerId",
        date_field="invoiceDate",
        party_id="cust1",
        status="posted",
    )
    assert where == {
        "companyId": "co1",
        "customerId": "cust1",
        "status": "posted",
    }


def test_activity_where_date_range() -> None:
    dt_from = datetime(2026, 1, 1, tzinfo=timezone.utc)
    dt_to = datetime(2026, 1, 31, 23, 59, 59, 999999, tzinfo=timezone.utc)
    where = activity_where(
        company_id="co1",
        party_field="customerId",
        date_field="invoiceDate",
        date_from=dt_from,
        date_to=dt_to,
    )
    assert where["invoiceDate"]["gte"] == dt_from
    assert where["invoiceDate"]["lte"] == dt_to


def test_filter_activity_rows_doc_type() -> None:
    rows = [
        {"docType": "Sale Invoice", "status": "posted"},
        {"docType": "Sale Receipt", "status": "posted"},
    ]
    out = filter_activity_rows(rows, doc_type="Sale Invoice", status=None)
    assert len(out) == 1
    assert out[0]["docType"] == "Sale Invoice"
