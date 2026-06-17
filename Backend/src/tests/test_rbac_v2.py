"""RBAC v2 permission resolution tests."""

from app.services.effective_permission_service import EffectivePermissionService
from app.services.field_masking_service import FieldMaskingService


def test_matches_wildcards() -> None:
    assert EffectivePermissionService.matches(["*"], "sales.invoices.create")
    assert EffectivePermissionService.matches(["sales.*"], "sales.invoices.create")
    assert EffectivePermissionService.matches(["sales.invoices.create"], "sales.invoices.create")
    assert not EffectivePermissionService.matches(["sales.read"], "sales.invoices.create")


def test_filter_by_module() -> None:
    perms = ["sales.read", "purchases.read", "inventory.*"]
    out = EffectivePermissionService.filter_by_module(perms, {"inventory"})
    assert "inventory.*" not in out
    assert "sales.read" in out


def test_field_masking_hides_product_cost() -> None:
    service = FieldMaskingService(
        access_control=None,  # type: ignore[arg-type]
        membership_repo=None,  # type: ignore[arg-type]
        effective_permissions=None,  # type: ignore[arg-type]
    )
    row = {"code": "P1", "name": "Widget", "cost": 12.5, "salePrice": 20}
    masked = service.mask_row(row, entity="product", field_access={"cost_price": "hidden"})
    assert masked["cost"] is None
    assert masked["salePrice"] == 20
