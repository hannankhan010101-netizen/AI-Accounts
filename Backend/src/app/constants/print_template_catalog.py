"""Print template codes — FastAccounts Settings → Printing (catalog §12.1 / §12.8)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PrintTemplateDef:
    code: str
    label: str
    group: str
    supports_two_copies: bool = False
    print_modes: tuple[str, ...] = ("document",)


PRINT_TEMPLATE_CATALOG: tuple[PrintTemplateDef, ...] = (
    # Sales
    PrintTemplateDef("si", "Sales Invoice (SI)", "Sales Printing"),
    PrintTemplateDef("sc", "Sales Credit (SC)", "Sales Printing"),
    PrintTemplateDef("so", "Sales Order (SO)", "Sales Printing"),
    PrintTemplateDef("sr", "Sales Receipt (SR)", "Sales Printing", supports_two_copies=True),
    PrintTemplateDef("pdcr", "Post Dated Cheque Received (PDCR)", "Sales Printing"),
    PrintTemplateDef("gdnso", "Delivery Note from SO (GDNSO)", "Sales Printing"),
    PrintTemplateDef("gdnsi", "Delivery Note from SI (GDNSI)", "Sales Printing"),
    PrintTemplateDef("cus", "Customer (CUS)", "Sales Printing"),
    # Purchases
    PrintTemplateDef("vi", "Supplier Bill (VI)", "Purchases Printing"),
    PrintTemplateDef("vc", "Supplier Credit (VC)", "Purchases Printing"),
    PrintTemplateDef("po", "Purchase Order (PO)", "Purchases Printing"),
    PrintTemplateDef("vp", "Bill Payment (VP)", "Purchases Printing", supports_two_copies=True),
    PrintTemplateDef("pdci", "Post Dated Cheque Issued (PDCI)", "Purchases Printing"),
    PrintTemplateDef("grnpo", "GRN from PO (GRNPO)", "Purchases Printing"),
    PrintTemplateDef("grnvi", "GRN from VI (GRNVI)", "Purchases Printing"),
    # Journal / Bank / Other / Project
    PrintTemplateDef("journal", "Journal", "Journal / Bank / Other / Project Printing"),
    PrintTemplateDef(
        "bank",
        "Bank voucher",
        "Journal / Bank / Other / Project Printing",
        print_modes=("voucher", "journal"),
    ),
    PrintTemplateDef("assembly", "Assembly", "Journal / Bank / Other / Project Printing"),
    PrintTemplateDef("stock-adjustment", "Stock Adjustment", "Journal / Bank / Other / Project Printing"),
    PrintTemplateDef("stock-transfer", "Stock Transfer", "Journal / Bank / Other / Project Printing"),
    PrintTemplateDef("user-log", "User Log", "Journal / Bank / Other / Project Printing"),
    PrintTemplateDef("project", "Project", "Journal / Bank / Other / Project Printing"),
)

PRINT_TEMPLATE_BY_CODE: dict[str, PrintTemplateDef] = {t.code: t for t in PRINT_TEMPLATE_CATALOG}


def default_print_template(code: str) -> dict[str, object]:
    """Default layout flags for a document print template."""

    meta = PRINT_TEMPLATE_BY_CODE.get(code)
    out: dict[str, object] = {
        "code": code,
        "title": meta.label if meta else code.upper(),
        "showLogo": True,
        "showBusinessBlock": True,
        "headerNote": "",
        "footerNote": "",
        "paperSize": "A4",
        "showTaxColumns": True,
        "printMode": "document",
    }
    if meta and meta.supports_two_copies:
        out["twoCopies"] = False
    if meta and len(meta.print_modes) > 1:
        out["printMode"] = meta.print_modes[0]
    return out
