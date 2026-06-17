"""Keyset (cursor) pagination helpers for Prisma list reports."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def page_size_from_criteria(criteria: dict[str, Any], *, default: int = 200, maximum: int = 5000) -> int:
    return min(max(1, int(criteria.get("pageSize") or default)), maximum)


def parse_cursor_datetime(value: Any) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def apply_desc_date_keyset(
    where: dict[str, Any],
    *,
    criteria: dict[str, Any],
    date_field: str,
) -> dict[str, Any]:
    """
    Descending sort on ``(date_field, id)`` — pass ``cursorDate`` + ``cursorId`` in criteria.
    """

    cursor_date = parse_cursor_datetime(criteria.get("cursorDate"))
    cursor_id = criteria.get("cursorId")
    if cursor_date is None or not cursor_id:
        return where
    return {
        **where,
        "OR": [
            {date_field: {"lt": cursor_date}},
            {date_field: cursor_date, "id": {"lt": str(cursor_id)}},
        ],
    }


def apply_asc_code_keyset(
    where: dict[str, Any],
    *,
    criteria: dict[str, Any],
    code_field: str = "code",
) -> dict[str, Any]:
    """Ascending sort on ``(code, id)`` — pass ``cursorCode`` + ``cursorId``."""

    cursor_code = criteria.get("cursorCode")
    cursor_id = criteria.get("cursorId")
    if not cursor_code or not cursor_id:
        return where
    return {
        **where,
        "OR": [
            {code_field: {"gt": str(cursor_code)}},
            {code_field: str(cursor_code), "id": {"gt": str(cursor_id)}},
        ],
    }


def trim_keyset_page(
    rows: list[Any],
    *,
    page_size: int,
    to_dict: Any,
    date_field: str,
    id_field: str = "id",
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    """If more than ``page_size`` rows were fetched, trim and build ``nextCursor``."""

    out = [to_dict(r) for r in rows[:page_size]]
    if len(rows) <= page_size:
        return out, None
    last = rows[page_size - 1]
    date_val = getattr(last, date_field, None)
    cursor_date = date_val.isoformat() if isinstance(date_val, datetime) else str(date_val)
    return out, {
        "cursorDate": cursor_date,
        "cursorId": getattr(last, id_field),
        "hasMore": True,
    }


def trim_keyset_page_code(
    rows: list[Any],
    *,
    page_size: int,
    to_dict: Any,
    code_field: str = "code",
    id_field: str = "id",
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    out = [to_dict(r) for r in rows[:page_size]]
    if len(rows) <= page_size:
        return out, None
    last = rows[page_size - 1]
    return out, {
        "cursorCode": getattr(last, code_field),
        "cursorId": getattr(last, id_field),
        "hasMore": True,
    }


def attach_pagination_meta(
    rows: list[dict[str, Any]],
    *,
    criteria: dict[str, Any],
    next_cursor: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if not criteria.get("includePaginationMeta"):
        return rows
    meta: dict[str, Any] = {
        "pageSize": page_size_from_criteria(criteria),
        "returnedRows": len(rows),
        "hasMore": bool(next_cursor and next_cursor.get("hasMore")),
    }
    if next_cursor:
        meta["nextCursor"] = {k: v for k, v in next_cursor.items() if k != "hasMore"}
    return [{"_meta": meta}, *rows]
