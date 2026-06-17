"""Onboarding JSON payloads — Prisma Client Python quirks."""

from __future__ import annotations

from prisma_generated import fields

from app.core.prisma_data import json_field


def test_json_field_wraps_dotted_tour_keys():
    payload = {"tours": {"onboard.core": {"stepIndex": 2, "status": "in_progress"}}}
    wrapped = json_field(payload)
    assert isinstance(wrapped, fields.Json)
    assert wrapped.data["tours"]["onboard.core"]["stepIndex"] == 2
