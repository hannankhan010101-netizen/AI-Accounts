"""Date advancement for recurring schedules."""

from __future__ import annotations

import calendar
from datetime import datetime, timedelta


def advance_schedule_date(
    current: datetime, *, frequency: str, interval: int
) -> datetime:
    step = max(interval, 1)
    if frequency == "daily":
        return current.replace(microsecond=0) + timedelta(days=step)
    if frequency == "weekly":
        return current.replace(microsecond=0) + timedelta(weeks=step)
    if frequency == "monthly":
        month_index = current.month - 1 + step
        year = current.year + month_index // 12
        month = month_index % 12 + 1
        last_day = calendar.monthrange(year, month)[1]
        day = min(current.day, last_day)
        return current.replace(year=year, month=month, day=day, microsecond=0)
    return current.replace(microsecond=0) + timedelta(days=step)
