"""Full §10.11 report ID registry — P9 metadata for catalog parity."""

from __future__ import annotations

from app.constants.report_definitions import all_report_definitions
from app.constants.report_aliases import resolve_report_handler_id
from app.constants.report_assembly_registry import assembly_report_coverage
from app.constants.report_financial_registry import financial_report_coverage
from app.constants.report_bank_financial_registry import bank_financial_coverage
from app.constants.report_module_registry import (
    IMPLEMENTED_MODULE_HANDLERS,
    MODULE_REPORT_IDS,
    module_report_coverage,
)

# Numeric IDs captured from FAST-ACCOUNTS-FEATURE-CATALOG.md §10.11 (Sales, Purchases, Inventory, Favorites).
CATALOG_REPORT_IDS: frozenset[str] = frozenset(
    {
        "028", "029", "030", "031", "032", "033", "034", "035",
        "047", "048", "051", "054", "067", "071", "078", "079", "080",
        "081", "082", "083", "084", "085", "086", "087", "088", "089",
        "141", "142", "143", "144", "145", "148", "160", "162", "164",
        "173", "174", "175", "178", "181", "182", "185", "206", "238",
        "240", "241", "243", "245", "246", "272", "300", "311", "475", "477",
        "GRNI", "TB", "PNL", "BS", "GL",
    }
)

IMPLEMENTED_HANDLER_IDS: frozenset[str] = frozenset(
    {
        "028", "029", "030", "031", "032", "033", "034", "035", "047", "048",
        "051", "054", "067", "071", "078", "079", "080", "081", "082", "083",
        "085", "087", "143", "145", "148", "162", "174", "175", "181", "182", "185", "272", "300",
        "311", "475", "477", "STOCK_XFR", "PROD_ACT",
        "GRNI", "TB", "PNL", "BS", "GL",
        "BANK_REC", "BANK_BAL", "BANK_ACT", "BANK_XFR", "BANK_CF",
        "FIN_MTB", "FIN_CMP", "FIN_PNL_CAT", "FIN_TB12",
        "AR_AGING", "AP_AGING", "BUDGET_VS_ACTUAL",
        "ASM_JOB", "ASM_WIP", "ASM_COMP", "ASM_TPL", "PRJ_PAY",
    }
)


def catalog_coverage() -> dict[str, object]:
    """Summary for health/diagnostics endpoints."""

    defined = {r.report_id for r in all_report_definitions()}
    implemented_via_alias = sum(
        1 for rid in CATALOG_REPORT_IDS if resolve_report_handler_id(rid) in IMPLEMENTED_HANDLER_IDS
    )
    module = module_report_coverage()
    return {
        "catalogIds": len(CATALOG_REPORT_IDS),
        "definitionRows": len(defined),
        "implementedHandlers": len(IMPLEMENTED_HANDLER_IDS),
        "catalogWithHandler": implemented_via_alias,
        "unmappedCatalogIds": sorted(
            rid for rid in CATALOG_REPORT_IDS
            if resolve_report_handler_id(rid) not in IMPLEMENTED_HANDLER_IDS
        ),
        **module,
        **bank_financial_coverage(),
        **assembly_report_coverage(),
        **financial_report_coverage(),
    }
