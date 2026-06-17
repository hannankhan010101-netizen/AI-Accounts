"""P47 foundation unit tests."""

from __future__ import annotations

import json
import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest


@pytest.mark.asyncio
async def test_openapi_reconciliation_complete() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    base = "/api/v1/companies/{company_id}"
    key = f"{base}/bank-reconciliations/{{reconciliation_id}}/complete"
    assert key in paths
    assert "post" in paths[key]


def test_import_presets_json_shape() -> None:
    payload = {
        "version": 1,
        "presets": [
            {
                "id": "x",
                "label": "My filter",
                "draft": {"typeContains": "BANK", "dateFrom": "2026-01-01"},
            }
        ],
    }
    rows = payload["presets"]
    assert len(rows) == 1
    assert rows[0]["label"] == "My filter"
    assert json.dumps(payload)
