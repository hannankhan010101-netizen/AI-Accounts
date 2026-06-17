"""P46 foundation unit tests."""

from __future__ import annotations

import json
import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest


def test_describe_names_only_export() -> None:
    from app.services.role_import_parser import describe_role_import_file

    payload = {
        "namesOnly": True,
        "roles": [{"name": "Admin", "permissions": ["*"]}],
    }
    hint = describe_role_import_file(
        filename="roles.json",
        content=json.dumps(payload).encode(),
    )
    assert hint["namesOnly"] is True
    assert hint["fileFormat"] == "json"


def test_bank_reconciliation_audit_constant() -> None:
    from app.domain.document_workflow import SOURCE_BANK_RECONCILIATION

    assert SOURCE_BANK_RECONCILIATION == "BANK_RECONCILIATION"


@pytest.mark.asyncio
async def test_openapi_bank_reconciliation_detail() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    base = "/api/v1/companies/{company_id}"
    assert f"{base}/bank-reconciliations/{{reconciliation_id}}" in paths
    assert "get" in paths[f"{base}/bank-reconciliations/{{reconciliation_id}}"]
