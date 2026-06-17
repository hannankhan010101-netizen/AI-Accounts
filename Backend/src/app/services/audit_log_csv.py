"""Audit log CSV export — P32."""

from __future__ import annotations

import csv
from io import StringIO
from typing import Any


def audit_log_entries_to_csv(rows: list[Any]) -> str:
    """Serialize audit rows to CSV text."""

    fieldnames = [
        "id",
        "createdAt",
        "userId",
        "transactionType",
        "transactionId",
        "status",
        "details",
    ]
    buf = StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        if hasattr(row, "model_dump"):
            data = row.model_dump()
        elif isinstance(row, dict):
            data = row
        else:
            data = {
                "id": getattr(row, "id", ""),
                "createdAt": getattr(row, "createdAt", ""),
                "userId": getattr(row, "userId", ""),
                "transactionType": getattr(row, "transactionType", ""),
                "transactionId": getattr(row, "transactionId", ""),
                "status": getattr(row, "status", ""),
                "details": getattr(row, "details", ""),
            }
        writer.writerow(
            {
                "id": data.get("id", ""),
                "createdAt": data.get("createdAt", ""),
                "userId": data.get("userId", ""),
                "transactionType": data.get("transactionType", ""),
                "transactionId": data.get("transactionId", ""),
                "status": data.get("status", ""),
                "details": data.get("details", ""),
            }
        )
    return buf.getvalue()
