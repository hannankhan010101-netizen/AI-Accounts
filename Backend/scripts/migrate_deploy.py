#!/usr/bin/env python3
"""Apply Prisma migrations using DIRECT_URL (session pooler :5432).

Runtime API should keep DATABASE_URL on the transaction pooler (:6543).
Do not use `npx prisma` — Node Prisma 7 is incompatible with schema.prisma.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    try:
        from dotenv import load_dotenv

        load_dotenv(ROOT / ".env")
    except ImportError:
        pass

    direct = os.getenv("DIRECT_URL", "").strip()
    if direct:
        os.environ["DATABASE_URL"] = direct
        print("Using DIRECT_URL for migrate deploy (port 5432 session pooler).")
    elif not os.getenv("DATABASE_URL", "").strip():
        print("ERROR: set DIRECT_URL or DATABASE_URL for migrate deploy.", file=sys.stderr)
        return 1
    else:
        print(
            "WARNING: DIRECT_URL not set; using DATABASE_URL (may hang on :6543 pooler).",
            file=sys.stderr,
        )

    env = {**os.environ, "PYTHONPATH": "src"}
    cmd = [sys.executable, "-m", "prisma", "migrate", "deploy"]
    return subprocess.call(cmd, cwd=ROOT, env=env)


if __name__ == "__main__":
    raise SystemExit(main())
