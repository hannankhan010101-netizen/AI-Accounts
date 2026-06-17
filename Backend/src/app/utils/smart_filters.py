"""Persist Smart Filter / Doc label values on commercial documents."""

from __future__ import annotations

from typing import Any


def smart_filters_custom_fields(smart_filters: dict[str, Any] | None) -> dict[str, Any]:
    """Wrap non-empty smart filter values for ``customFields`` JSON storage."""

    if not smart_filters:
        return {}
    cleaned = {
        str(k): str(v).strip()
        for k, v in smart_filters.items()
        if v is not None and str(v).strip()
    }
    return {"smartFilters": cleaned} if cleaned else {}
