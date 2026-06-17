"""Last rate doc type normalization."""

from app.services.last_rate_service import LAST_RATE_DOC_TYPES, normalize_last_rate_doc_type


def test_normalize_last_rate_doc_type_maps_legacy_keys() -> None:
    assert normalize_last_rate_doc_type("salesInvoice") == "SI"
    assert normalize_last_rate_doc_type("supplierBill") == "VI"
    assert normalize_last_rate_doc_type("SO") == "SO"


def test_last_rate_doc_types_match_smart_settings() -> None:
    assert "SI" in LAST_RATE_DOC_TYPES
    assert "VI" in LAST_RATE_DOC_TYPES
    assert "SO" in LAST_RATE_DOC_TYPES
    assert "PO" in LAST_RATE_DOC_TYPES
