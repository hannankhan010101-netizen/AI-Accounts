"""P45 foundation unit tests."""

from __future__ import annotations

import json
import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest


def test_parse_names_only_role_export_json() -> None:
    from app.services.role_import_parser import parse_role_import_file

    payload = {
        "exportedAt": "2026-01-01T00:00:00Z",
        "namesOnly": True,
        "roles": [
            {"name": "Admin", "permissions": ["*"]},
            {"name": "Clerk", "permissions": []},
        ],
    }
    rows = parse_role_import_file(
        filename="roles.json",
        content=json.dumps(payload).encode(),
    )
    assert len(rows) == 2
    assert rows[0]["name"] == "Admin"
    assert "id" not in rows[0]


def test_parse_role_import_requires_name() -> None:
    from app.services.role_import_parser import parse_role_import_file

    with pytest.raises(ValueError, match="name is required"):
        parse_role_import_file(
            filename="bad.json",
            content=json.dumps({"roles": [{"permissions": []}]}).encode(),
        )


def test_bank_payment_receipt_audit_constants() -> None:
    from app.domain.document_workflow import SOURCE_BANK_PAYMENT, SOURCE_BANK_RECEIPT

    assert SOURCE_BANK_PAYMENT == "BANK_PAYMENT"
    assert SOURCE_BANK_RECEIPT == "BANK_RECEIPT"
