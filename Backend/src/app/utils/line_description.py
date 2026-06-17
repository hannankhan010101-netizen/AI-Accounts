"""Merge Smart Settings product-description fields onto repo line dicts."""

from __future__ import annotations

from typing import Any


def merge_line_description_fields(
    repo_lines: list[dict[str, Any]],
    request_lines: list[Any],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for i, row in enumerate(repo_lines):
        merged = dict(row)
        if i < len(request_lines):
            req = request_lines[i]
            desc = getattr(req, "description", None)
            if desc and str(desc).strip():
                merged["description"] = str(desc).strip()
            fields = getattr(req, "description_fields", None)
            if fields:
                merged["descriptionFields"] = fields
            batch = getattr(req, "batch_number", None)
            if batch and str(batch).strip():
                merged["batchNumber"] = str(batch).strip()
            expiry = getattr(req, "expiry_date", None)
            if expiry is not None:
                merged["expiryDate"] = expiry
        out.append(merged)
    return out
