"""Assembly module report IDs — P14."""

from __future__ import annotations

from app.constants.report_aliases import resolve_report_handler_id

ASSEMBLY_REPORT_IDS: frozenset[str] = frozenset(
    {
        "ASM_JOB",
        "ASM_TPL",
        "ASM_WIP",
        "ASM_COMP",
        "201",
        "202",
    }
)

_RESOLVED_ASM = frozenset({"ASM_JOB", "ASM_TPL", "ASM_WIP", "ASM_COMP"})


def assembly_report_coverage() -> dict[str, object]:
    unmapped = sorted(
        rid
        for rid in ASSEMBLY_REPORT_IDS
        if resolve_report_handler_id(rid) not in _RESOLVED_ASM
    )
    return {
        "assemblyReportIds": len(ASSEMBLY_REPORT_IDS),
        "unmappedAssemblyReportIds": unmapped,
    }
