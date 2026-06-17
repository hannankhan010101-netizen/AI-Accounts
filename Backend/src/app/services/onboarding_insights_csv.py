"""Onboarding insights CSV export — P53."""

from __future__ import annotations

import csv
from io import StringIO
from typing import Any


def insights_to_csv(insights: dict[str, Any]) -> str:
    buf = StringIO()
    writer = csv.writer(buf)

    writer.writerow(["metric", "value"])
    writer.writerow(["totalLearners", insights.get("totalLearners", 0)])
    writer.writerow(["usersWithActivity", insights.get("usersWithActivity", 0)])
    writer.writerow([])

    writer.writerow(["tourId", "started", "completed", "ratePercent"])
    for row in insights.get("tourCompletion") or []:
        if isinstance(row, dict):
            writer.writerow(
                [
                    row.get("tourId", ""),
                    row.get("started", 0),
                    row.get("completed", 0),
                    row.get("ratePercent", 0),
                ]
            )
    writer.writerow([])

    writer.writerow(["step", "views"])
    for row in insights.get("topStepViews") or []:
        if isinstance(row, dict):
            writer.writerow([row.get("step", ""), row.get("views", 0)])

    return buf.getvalue()
