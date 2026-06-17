#!/usr/bin/env bash
# Local CI gate — mirrors GitHub Actions checks (no Docker/E2E).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

SKIP_FRONTEND=""
for arg in "$@"; do
  case "$arg" in
    --skip-frontend) SKIP_FRONTEND=1 ;;
  esac
done

echo "=== Backend pytest ==="
cd Backend
export PYTHONPATH=src SKIP_PRISMA=1 OUTBOX_POLL_ENABLED=0
python -m pytest src/tests -q

echo ""
echo "=== Feature matrix ==="
cd "$ROOT"
python scripts/_generate_feature_matrix.py

if [[ -z "${SKIP_FRONTEND:-}" ]]; then
  echo ""
  echo "=== Frontend typecheck ==="
  cd Frontend
  npm run typecheck

  echo ""
  echo "=== Frontend lint ==="
  npm run lint

  echo ""
  echo "=== Frontend build ==="
  NEXT_PUBLIC_API_BASE_URL=https://api.example.com npm run build
fi

echo ""
echo "=== CI local: PASS ==="
