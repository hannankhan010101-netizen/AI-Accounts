#!/usr/bin/env python3
"""Check Prisma migration status using DIRECT_URL (session pooler :5432).

`prisma migrate status` on Supabase :6543 often fails with P1017 — use this instead.
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
        print("Using DIRECT_URL for migrate status (port 5432 session pooler).")
    elif not os.getenv("DATABASE_URL", "").strip():
        print("ERROR: set DIRECT_URL or DATABASE_URL.", file=sys.stderr)
        return 1
    else:
        print(
            "WARNING: DIRECT_URL not set; using DATABASE_URL (may fail on :6543 pooler).",
            file=sys.stderr,
        )

    env = {**os.environ, "PYTHONPATH": "src"}
    cmd = [sys.executable, "-m", "prisma", "migrate", "status"]
    return subprocess.call(cmd, cwd=ROOT, env=env)


if __name__ == "__main__":
    raise SystemExit(main())
