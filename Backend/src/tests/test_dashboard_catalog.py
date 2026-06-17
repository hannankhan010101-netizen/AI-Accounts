"""Dashboard widget catalog defaults."""

from app.constants.dashboard_catalog import DEFAULT_DASHBOARD_WIDGETS, DASHBOARD_WIDGET_CATALOG
from app.constants.listing_catalog import LISTING_BY_ID


def test_dashboard_widget_catalog_covers_fa_sections() -> None:
    ids = {wid for wid, _ in DASHBOARD_WIDGET_CATALOG}
    assert "ar-summary" in ids
    assert "ap-summary" in ids
    assert "bank-balances" in ids
    assert "pnl-fy" in ids
    assert len(DEFAULT_DASHBOARD_WIDGETS) == len(DASHBOARD_WIDGET_CATALOG)


def test_listing_catalog_has_bank_and_pdc_targets() -> None:
    assert "bank-payments" in LISTING_BY_ID
    assert "bank-receipts" in LISTING_BY_ID
    assert "bank-transfer" in LISTING_BY_ID
    assert "pdc-received" in LISTING_BY_ID
    assert "pdc-issued" in LISTING_BY_ID
    assert "quotation" in LISTING_BY_ID
    assert "purchase-order" in LISTING_BY_ID
    assert "grn" in LISTING_BY_ID
    assert "delivery-note" in LISTING_BY_ID
    assert "sales-all" in LISTING_BY_ID
    assert "purchases-all" in LISTING_BY_ID
    assert "journals" in LISTING_BY_ID
    assert "stock-adjustment" in LISTING_BY_ID
    assert "product-batches" in LISTING_BY_ID
    assert "user-log" in LISTING_BY_ID
    assert "assembly-templates" in LISTING_BY_ID
    pdc = LISTING_BY_ID["pdc-received"]
    keys = {c.key for c in pdc.columns}
    assert "chequeDate" in keys
    assert "dueDate" not in keys
