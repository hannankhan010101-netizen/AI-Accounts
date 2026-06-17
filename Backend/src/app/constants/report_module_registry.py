"""Bank / Financial / Assembly / Projects report IDs — P11 extension beyond §10.11."""

from __future__ import annotations

from app.constants.report_aliases import resolve_report_handler_id

MODULE_REPORT_IDS: frozenset[str] = frozenset(
    {
        "BANK_BAL",
        "BANK_CF",
        "BANK_REC",
        "BANK_XFR",
        "BANK_ACT",
        "ASM_JOB",
        "ASM_TPL",
        "PRJ_PAY",
        "FIN_MTB",
        "FIN_CMP",
        "FIN_PNL_CAT",
        "ASM_WIP",
        "ASM_COMP",
        "FIN_TB12",
    }
)

IMPLEMENTED_MODULE_HANDLERS: frozenset[str] = frozenset(MODULE_REPORT_IDS)


def module_report_coverage() -> dict[str, object]:
    unmapped = sorted(
        rid
        for rid in MODULE_REPORT_IDS
        if resolve_report_handler_id(rid) not in IMPLEMENTED_MODULE_HANDLERS
    )
    return {
        "moduleReportIds": len(MODULE_REPORT_IDS),
        "implementedModuleHandlers": len(IMPLEMENTED_MODULE_HANDLERS),
        "unmappedModuleReportIds": unmapped,
    }
