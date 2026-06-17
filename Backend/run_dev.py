#!/usr/bin/env python3
"""Start the FastAPI dev server (uvicorn + reload).

Usage (from Backend folder):
    python run_dev.py
    python run_dev.py --port 8001
    .venv\\Scripts\\python run_dev.py

Re-execs with .venv Python when present so PYTHONPATH / imports work in CMD and PowerShell.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"


def _venv_python() -> Path | None:
    if sys.platform == "win32":
        candidate = ROOT / ".venv" / "Scripts" / "python.exe"
    else:
        candidate = ROOT / ".venv" / "bin" / "python"
    return candidate if candidate.is_file() else None


def _reexec_in_venv() -> None:
    venv_py = _venv_python()
    if venv_py is None:
        return
    if Path(sys.executable).resolve() == venv_py.resolve():
        return
    script = str(Path(__file__).resolve())
    raise SystemExit(subprocess.call([str(venv_py), script, *sys.argv[1:]], cwd=ROOT))


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv(ROOT / ".env")
    except ImportError:
        pass


def main() -> int:
    _reexec_in_venv()

    parser = argparse.ArgumentParser(description="Run AI-Accounts backend (uvicorn dev server)")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Bind port (default: 8000)")
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Disable auto-reload on file changes",
    )
    args = parser.parse_args()

    _load_dotenv()

    env = os.environ.copy()
    src_path = str(SRC)
    existing = env.get("PYTHONPATH", "").strip()
    env["PYTHONPATH"] = src_path if not existing else f"{src_path}{os.pathsep}{existing}"

    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        args.host,
        "--port",
        str(args.port),
        "--app-dir",
        str(SRC),
    ]
    if not args.no_reload:
        cmd.append("--reload")

    print(f"Starting backend at http://{args.host}:{args.port}")
    print(f"  cwd: {ROOT}")
    print(f"  app: src/app/main.py")
    return subprocess.call(cmd, cwd=ROOT, env=env)


if __name__ == "__main__":
    raise SystemExit(main())
