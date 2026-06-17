"""Financial module report IDs (slugs + provisional numeric aliases) — P15."""

from __future__ import annotations

from app.constants.report_aliases import resolve_report_handler_id

FINANCIAL_REPORT_IDS: frozenset[str] = frozenset(
    {
        "TB",
        "PNL",
        "BS",
        "GL",
        "FIN_MTB",
        "FIN_CMP",
        "FIN_PNL_CAT",
        "FIN_TB12",
        "203",
        "204",
        "205",
        "207",
        "208",
        "209",
        "210",
    }
)

_IMPLEMENTED_FIN_HANDLERS: frozenset[str] = frozenset(
    {
        "TB",
        "PNL",
        "BS",
        "GL",
        "FIN_MTB",
        "FIN_CMP",
        "FIN_PNL_CAT",
        "FIN_TB12",
    }
)


# Slug cards (TB, PNL, …) pass through resolve unchanged; 203–210 are stable internal aliases.
FINANCIAL_ID_SOURCE: str = "json-config-financial_report_ids.json"


def financial_report_coverage() -> dict[str, object]:
    unmapped = sorted(
        rid
        for rid in FINANCIAL_REPORT_IDS
        if resolve_report_handler_id(rid) not in _IMPLEMENTED_FIN_HANDLERS
    )
    return {
        "financialReportIds": len(FINANCIAL_REPORT_IDS),
        "financialIdSource": FINANCIAL_ID_SOURCE,
        "unmappedFinancialReportIds": unmapped,
    }
