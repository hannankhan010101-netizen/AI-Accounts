#!/usr/bin/env sh
# One-command go-live verification. Usage: ./scripts/go-live.sh
set -e
cd "$(dirname "$0")/.."
python scripts/fastaccounts_migrate/_go_live_check.py
