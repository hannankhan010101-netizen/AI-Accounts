"""Apply useConfiguredListColumns to key list pages."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "Frontend" / "src" / "app" / "(app)"

WIRING = [
    ("sales/receipts/page.tsx", "sales-receipt", "SalesReceipt"),
    ("purchases/bills/page.tsx", "supplier-bill", "SupplierBill"),
    ("purchases/payments/page.tsx", "supplier-payment", "SupplierPayment"),
    ("inventory/products/page.tsx", "products", "Product"),
]


def wire(path: Path, listing_id: str, row_type: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if "useConfiguredListColumns" in text:
        print(f"skip {path.relative_to(ROOT.parent.parent.parent)} (already wired)")
        return False

    if "useMemo" not in text:
        text = text.replace('import { useMemo } from "react";\n', "")
        text = text.replace(
            '"use client";\n\n',
            '"use client";\n\nimport { useMemo } from "react";\n',
            1,
        )
        if "useMemo" not in text:
            text = text.replace(
                '"use client";\n\nimport ',
                '"use client";\n\nimport { useMemo } from "react";\nimport ',
                1,
            )

    if "useConfiguredListColumns" not in text:
        anchor = 'import { responsiveListColumns } from "@/lib/grid/responsive-columns";'
        if anchor in text:
            text = text.replace(
                anchor,
                anchor + '\nimport { useConfiguredListColumns } from "@/lib/hooks/use-configured-list-columns";',
            )
        else:
            text = text.replace(
                'import { PageHeader }',
                'import { useConfiguredListColumns } from "@/lib/hooks/use-configured-list-columns";\nimport { PageHeader }',
                1,
            )

    # const columns = responsiveListColumns<...>([ ... ]);
    pattern = re.compile(
        r"(\s*)const columns = responsiveListColumns<(\w+)>\(\[\s*\n",
        re.MULTILINE,
    )
    m = pattern.search(text)
    if not m:
        print(f"WARN no columns block in {path}")
        return False

    indent = m.group(1)
    type_name = m.group(2)

    # Find matching closing ]);
    start = m.start()
    depth = 0
    i = m.end() - 1
    while i < len(text):
        if text[i : i + 2] == "])":
            depth -= 1
            if depth == 0 and text[i : i + 3] == "]);":
                end = i + 3
                break
        if text[i] == "[":
            depth += 1
        i += 1
    else:
        print(f"WARN could not close columns in {path}")
        return False

    inner = text[m.end() : end - 3]
    # Detect deps from common patterns
    deps = []
    if "customerNameById" in inner:
        deps.append("customerNameById")
    if "supplierNameById" in inner:
        deps.append("supplierNameById")
    if "bankLabelById" in inner:
        deps.append("bankLabelById")
    deps_str = ", ".join(deps) if deps else ""

    replacement = (
        f"{indent}const baseColumns = useMemo(\n"
        f"{indent}  () => responsiveListColumns<{type_name}>([\n"
        f"{inner}\n"
        f"{indent}  ]),\n"
        f"{indent}  [{deps_str}],\n"
        f"{indent});\n"
        f"{indent}const columns = useConfiguredListColumns({listing_id!r}, baseColumns);"
    )
    text = text[:start] + replacement + text[end:]
    path.write_text(text, encoding="utf-8")
    print(f"OK {path.relative_to(ROOT.parent.parent.parent)} -> {listing_id}")
    return True


def main() -> None:
    n = 0
    for rel, listing_id, _ in WIRING:
        if wire(ROOT / rel, listing_id, _):
            n += 1
    print(f"Wired {n} list pages")


if __name__ == "__main__":
    main()
