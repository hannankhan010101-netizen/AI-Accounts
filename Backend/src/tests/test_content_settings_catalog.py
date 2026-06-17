"""Content Settings catalog defaults."""

from app.constants.forms_catalog import default_form_layout
from app.constants.menu_catalog import default_menu_layout


def test_default_form_layout_has_fields() -> None:
    layout = default_form_layout("sales-invoice")
    assert layout["formId"] == "sales-invoice"
    fields = layout["fields"]
    assert isinstance(fields, list)
    assert len(fields) >= 4
    assert fields[0]["key"] == "invoiceDate"


def test_default_menu_layout_has_items() -> None:
    layout = default_menu_layout()
    items = layout["items"]
    assert isinstance(items, list)
    assert len(items) >= 10
    assert items[0]["href"] == "/dashboard"
