"""Add require_module_reports guard to all /reports routes in tenant.py."""

from __future__ import annotations

import re
from pathlib import Path

GUARD = '    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],\n'
PATTERN = re.compile(
    r'(@router\.(?:get|post)\("/reports[^"]+"\)\nasync def [^\n]+\(\n    company_id: str,\n)'
)


def main() -> None:
    path = Path(__file__).resolve().parents[1] / "src" / "app" / "api" / "routes" / "tenant.py"
    text = path.read_text(encoding="utf-8")
    patched = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal patched
        block = match.group(1)
        if "_reports:" in block:
            return block
        patched += 1
        return block + GUARD

    updated = PATTERN.sub(repl, text)
    path.write_text(updated, encoding="utf-8")
    print(f"patched {patched} report routes")


if __name__ == "__main__":
    main()
