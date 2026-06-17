"""Add businessLogoUrl to voucher print pages using useVoucherPrintPage."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "Frontend" / "src" / "app" / "print"


def wire(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "useVoucherPrintPage" not in text:
        return False
    if "businessLogoUrl" in text:
        return False

    text2 = text.replace(
        "businessName, businessAddress, template",
        "businessName, businessAddress, businessLogoUrl, template",
    )
    text2 = re.sub(
        r"(businessAddress=\{businessAddress\})\n(\s+)(fields=|template=|tableHeaders=)",
        r"\1\n\2businessLogoUrl={businessLogoUrl}\n\2\3",
        text2,
        count=1,
    )
    if text2 == text:
        return False
    path.write_text(text2, encoding="utf-8")
    print(f"OK {path.relative_to(ROOT.parent.parent)}")
    return True


def main() -> None:
    n = sum(wire(p) for p in ROOT.rglob("page.tsx"))
    print(f"Wired {n} pages")


if __name__ == "__main__":
    main()
