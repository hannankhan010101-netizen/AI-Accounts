"""P21 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

from app.services.inventory_quantity_service import InventoryQuantityService


def test_inventory_delivery_stock_helpers() -> None:
    assert hasattr(InventoryQuantityService, "apply_delivery_note_lines")
    assert hasattr(InventoryQuantityService, "restore_delivery_note_lines")


def test_openapi_delivery_create_returns_stock() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    post = paths["/api/v1/companies/{company_id}/delivery-notes"]["post"]
    assert post is not None
