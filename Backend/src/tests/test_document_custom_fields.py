"""Document customFields merge helper."""

from app.utils.document_custom_fields import document_custom_fields


def test_document_custom_fields_merges_payment_method_and_filters() -> None:
    out = document_custom_fields(
        smart_filters={"filter1": "Region A"},
        payment_method="cheque",
    )
    assert out["paymentMethod"] == "cheque"
    assert out["smartFilters"] == {"filter1": "Region A"}


def test_document_custom_fields_omits_empty() -> None:
    assert document_custom_fields() == {}
    assert document_custom_fields(payment_method="  ") == {}
