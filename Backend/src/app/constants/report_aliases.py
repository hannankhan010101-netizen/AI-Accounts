"""Map catalog report IDs to implemented query handlers — P5/P6/P7."""

from __future__ import annotations

REPORT_ID_ALIASES: dict[str, str] = {
    "141": "028",
    "142": "029",
    "143": "143",
    "144": "030",
    "160": "034",
    "178": "031",
    "240": "030",
    "241": "031",
    "243": "034",
    "245": "030",
    "246": "034",
    "145": "145",
    "238": "048",
    "081": "PROD_ACT",
    "084": "085",
    "086": "087",
    "088": "085",
    "089": "087",
    "149": "PROD_ACT",
    "164": "080",
    "173": "080",
    "206": "STOCK_XFR",
    "475": "300",
    "477": "300",
    "272": "048",
    # P13 — Bank / Financial numeric IDs → module handlers
    "072": "BANK_REC",
    "073": "BANK_BAL",
    "074": "BANK_ACT",
    "076": "BANK_XFR",
    "077": "BANK_CF",
    "FIN_CMP": "FIN_CMP",
    "FIN_PNL_CAT": "FIN_PNL_CAT",
    "201": "ASM_JOB",
    "202": "ASM_WIP",
    "ASM_COMP": "ASM_COMP",
    # P15/P16 — Financial numeric aliases (core statements + module reports)
    "203": "TB",
    "204": "PNL",
    "205": "BS",
    "207": "FIN_PNL_CAT",
    "208": "FIN_TB12",
    "209": "FIN_CMP",
    "210": "FIN_MTB",
    "FIN_TB12": "FIN_TB12",
}


def resolve_report_handler_id(report_id: str) -> str:
    """Resolve catalog ID to SQL handler key, following alias chains (e.g. 149→081→080)."""

    from app.constants.financial_report_overrides import financial_live_aliases

    live = financial_live_aliases()
    if report_id in live:
        return live[report_id]

    current = report_id
    seen: set[str] = set()
    while current in REPORT_ID_ALIASES and current not in seen:
        seen.add(current)
        current = REPORT_ID_ALIASES[current]
    return current
