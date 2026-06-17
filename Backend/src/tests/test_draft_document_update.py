"""Draft document PATCH routes registered in tenant API."""

from pathlib import Path


def test_patch_draft_sales_invoice_and_supplier_bill_routes_exist() -> None:
    tenant_routes = (
        Path(__file__).resolve().parents[1] / "app" / "api" / "routes" / "tenant.py"
    ).read_text(encoding="utf-8")
    assert '@router.patch("/sales-invoices/{invoice_id}")' in tenant_routes
    assert "async def update_sales_invoice" in tenant_routes
    assert '@router.patch("/supplier-bills/{bill_id}")' in tenant_routes
    assert "async def update_supplier_bill" in tenant_routes
