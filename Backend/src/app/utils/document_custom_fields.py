"""Merge optional document metadata into ``customFields`` JSON."""

from __future__ import annotations

from typing import Any

from app.utils.smart_filters import smart_filters_custom_fields


def document_custom_fields(
    *,
    smart_filters: dict[str, Any] | None = None,
    payment_method: str | None = None,
) -> dict[str, Any]:
    out: dict[str, Any] = dict(smart_filters_custom_fields(smart_filters))
    method = (payment_method or "").strip()
    if method:
        out["paymentMethod"] = method
    return out
