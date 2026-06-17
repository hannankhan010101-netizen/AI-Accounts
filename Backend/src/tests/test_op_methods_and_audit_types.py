"""Audit transaction types and OP methods catalogs."""

from app.constants.audit_transaction_types import (
    AUDIT_TRANSACTION_TYPE_CATALOG,
    audit_transaction_type_groups,
)
from app.constants.op_methods_catalog import DEFAULT_OP_METHODS_SETTINGS, OP_METHOD_CATALOG


def test_audit_transaction_type_groups() -> None:
    groups = audit_transaction_type_groups()
    assert len(groups) >= 5
    sales = next(g for g in groups if g["group"] == "Sales")
    ids = {t["id"] for t in sales["types"]}
    assert "SALES_INVOICE" in ids
    assert "PDC_RECEIVED" in ids
    assert len(AUDIT_TRANSACTION_TYPE_CATALOG) >= 20


def test_op_methods_defaults() -> None:
    assert DEFAULT_OP_METHODS_SETTINGS["defaultPaymentMethod"] == "cash"
    enabled = DEFAULT_OP_METHODS_SETTINGS["enabledMethods"]
    assert isinstance(enabled, list)
    assert len(enabled) == len(OP_METHOD_CATALOG)
