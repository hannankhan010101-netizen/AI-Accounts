"""Bank / Financial numeric report IDs (live UI capture) — P13."""

from __future__ import annotations

from app.constants.report_aliases import resolve_report_handler_id

BANK_FINANCIAL_NUMERIC_IDS: frozenset[str] = frozenset(
    {
        "072",
        "073",
        "074",
        "076",
        "077",
        "300",
        "475",
        "477",
    }
)

_RESOLVED_OK = frozenset(
    {
        "071",
        "300",
        "475",
        "477",
        "BANK_REC",
        "BANK_BAL",
        "BANK_ACT",
        "BANK_XFR",
        "BANK_CF",
    }
)


def bank_financial_coverage() -> dict[str, object]:
    unmapped = sorted(
        rid
        for rid in BANK_FINANCIAL_NUMERIC_IDS
        if resolve_report_handler_id(rid) not in _RESOLVED_OK
    )
    return {
        "bankFinancialNumericIds": len(BANK_FINANCIAL_NUMERIC_IDS),
        "unmappedBankFinancialIds": unmapped,
    }
