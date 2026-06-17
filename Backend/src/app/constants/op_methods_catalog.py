"""FA §12.1 OP (payment) methods — defaults for receipts and bill payments."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OpMethodDef:
    id: str
    label: str


OP_METHOD_CATALOG: tuple[OpMethodDef, ...] = (
    OpMethodDef("cash", "Cash"),
    OpMethodDef("cheque", "Cheque"),
    OpMethodDef("pay_order", "Pay order"),
    OpMethodDef("demand_draft", "Demand draft"),
    OpMethodDef("bank_transfer", "Bank transfer / TT"),
    OpMethodDef("online", "Online payment"),
    OpMethodDef("credit_card", "Credit card"),
    OpMethodDef("pdc", "Post-dated cheque"),
)

DEFAULT_OP_METHOD_IDS: list[str] = [m.id for m in OP_METHOD_CATALOG]

DEFAULT_OP_METHODS_SETTINGS: dict[str, object] = {
    "defaultPaymentMethod": "cash",
    "enabledMethods": list(DEFAULT_OP_METHOD_IDS),
}
