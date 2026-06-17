"""Query helpers for Sales All / Purchases All activity feeds."""

from __future__ import annotations

from datetime import date, datetime, time, timezone
from typing import Any


def parse_activity_date(value: str | None, *, end_of_day: bool = False) -> datetime | None:
    """Parse YYYY-MM-DD (or ISO datetime) for Prisma date filters."""

    if not value or not str(value).strip():
        return None
    raw = str(value).strip()
    if "T" in raw:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    d = date.fromisoformat(raw[:10])
    t = time(23, 59, 59, 999999) if end_of_day else time.min
    return datetime.combine(d, t, tzinfo=timezone.utc)


def activity_where(
    *,
    company_id: str,
    party_field: str,
    date_field: str,
    party_id: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    status: str | None = None,
) -> dict[str, Any]:
    """Build a Prisma ``where`` clause for one activity source table."""

    where: dict[str, Any] = {"companyId": company_id}
    if party_id:
        where[party_field] = party_id
    if status:
        where["status"] = status
    date_bounds: dict[str, datetime] = {}
    if date_from:
        date_bounds["gte"] = date_from
    if date_to:
        date_bounds["lte"] = date_to
    if date_bounds:
        where[date_field] = date_bounds
    return where


def filter_activity_rows(
    rows: list[dict[str, Any]],
    *,
    doc_type: str | None,
    status: str | None,
) -> list[dict[str, Any]]:
    """Post-merge filters when doc type spans multiple tables."""

    out = rows
    if doc_type:
        out = [r for r in out if r.get("docType") == doc_type]
    if status:
        out = [r for r in out if (r.get("status") or "") == status]
    return out
