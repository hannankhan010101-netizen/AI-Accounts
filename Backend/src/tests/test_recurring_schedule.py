from datetime import datetime

from app.utils.schedule_dates import advance_schedule_date


def test_advance_schedule_date_monthly() -> None:
    start = datetime(2026, 1, 15)
    nxt = advance_schedule_date(start, frequency="monthly", interval=1)
    assert nxt.month == 2
    assert nxt.day == 15


def test_advance_schedule_date_weekly() -> None:
    start = datetime(2026, 1, 1)
    nxt = advance_schedule_date(start, frequency="weekly", interval=2)
    assert (nxt - start).days == 14
