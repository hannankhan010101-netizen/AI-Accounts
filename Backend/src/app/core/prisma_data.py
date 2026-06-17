"""Helpers for Prisma Client Python create/update payloads."""

from __future__ import annotations

from typing import Any

from prisma_generated import fields


def omit_none(data: dict[str, Any]) -> dict[str, Any]:
    """Drop keys whose value is None — Prisma Python rejects explicit nulls on optionals."""

    return {k: v for k, v in data.items() if v is not None}


def optional_json(value: dict[str, Any] | None) -> fields.Json | None:
    if value is None:
        return None
    return fields.Json(value)


def json_field(value: dict[str, Any] | list[Any]) -> fields.Json:
    """Wrap JSON for Prisma — required so dotted object keys are not parsed as GraphQL paths."""

    return fields.Json(value)
