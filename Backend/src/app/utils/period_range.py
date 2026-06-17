"""Period helpers for command center date ranges."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

PeriodKey = Literal["mtd", "qtd", "ytd", "fy"]


def resolve_period(
    period: str,
    *,
    now: datetime | None = None,
) -> tuple[datetime, datetime, datetime, datetime]:
    """
    Return (from, to, prior_from, prior_to) UTC for the requested period key.
    """

    current = now or datetime.now(timezone.utc)
    to = current
    key = period if period in ("mtd", "qtd", "ytd", "fy") else "fy"

    if key == "mtd":
        start = current.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if start.month == 1:
            prior_start = start.replace(year=start.year - 1, month=12)
        else:
            prior_start = start.replace(month=start.month - 1)
        prior_end = start
    elif key == "qtd":
        q_month = ((current.month - 1) // 3) * 3 + 1
        start = current.replace(month=q_month, day=1, hour=0, minute=0, second=0, microsecond=0)
        prior_start = start.replace(month=start.month - 3) if start.month > 3 else start.replace(
            year=start.year - 1, month=start.month + 9
        )
        prior_end = start
    elif key == "ytd":
        start = current.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        prior_start = start.replace(year=start.year - 1)
        prior_end = start.replace(year=start.year - 1, month=current.month, day=current.day)
    else:
        start = current.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        prior_start = start.replace(year=start.year - 1)
        prior_end = start

    return start, to, prior_start, prior_end
