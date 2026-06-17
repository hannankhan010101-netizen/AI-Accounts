#!/usr/bin/env bash
# Full release gate — run before tagging or production deploy.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

SKIP_GO_LIVE=""
SKIP_DB=""
SKIP_ENV_STRICT=""
ENV_FILE=""
for arg in "$@"; do
  case "$arg" in
    --skip-go-live) SKIP_GO_LIVE=1 ;;
    --skip-db) SKIP_DB=1 ;;
    --skip-env-strict) SKIP_ENV_STRICT=1 ;;
    --env-file=*) ENV_FILE="${arg#*=}" ;;
  esac
done

echo "=== Release check (Nafy-Pharma) ==="

echo ""
echo "[1/3] Local CI..."
"$ROOT/scripts/ci-local.sh"

echo ""
echo "[2/3] Deploy preflight..."
if [[ -n "${SKIP_DB:-}" && -n "${SKIP_ENV_STRICT:-}" ]]; then
  echo "  (preflight skipped)"
elif [[ -n "${SKIP_DB:-}" ]]; then
  ARGS=(--strict)
  [[ -n "$ENV_FILE" ]] && ARGS+=(--env-file "$ENV_FILE")
  python scripts/_prod_env_check.py "${ARGS[@]}"
elif [[ -n "${SKIP_ENV_STRICT:-}" ]]; then
  "$ROOT/scripts/deploy-preflight.sh" --skip-env-check
else
  PF_ARGS=(--strict)
  [[ -n "$ENV_FILE" ]] && PF_ARGS+=(--env-file="$ENV_FILE")
  "$ROOT/scripts/deploy-preflight.sh" "${PF_ARGS[@]}"
fi

if [[ -n "${SKIP_GO_LIVE:-}" ]]; then
  echo ""
  echo "=== Release check: PASS (go-live skipped) ==="
  exit 0
fi

echo ""
echo "[3/3] Go-live verification (may take several minutes)..."
"$ROOT/scripts/go-live.sh"
exit $?
