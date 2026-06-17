#!/usr/bin/env bash
# Pre-production deploy gate — env vars + optional DB tenant check.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

STRICT=""
SKIP_DB=""
SKIP_ENV=""
ENV_FILE=""
for arg in "$@"; do
  case "$arg" in
    --strict) STRICT="--strict" ;;
    --skip-db) SKIP_DB=1 ;;
    --skip-env-check) SKIP_ENV=1 ;;
    --env-file=*) ENV_FILE="${arg#*=}" ;;
  esac
done

if [[ -z "${SKIP_ENV:-}" ]]; then
  ENV_ARGS=()
  [[ -n "$STRICT" ]] && ENV_ARGS+=("$STRICT")
  [[ -n "$ENV_FILE" ]] && ENV_ARGS+=(--env-file "$ENV_FILE")
  python scripts/_prod_env_check.py "${ENV_ARGS[@]}"
fi

if [[ -z "${SKIP_DB:-}" ]]; then
  python scripts/fastaccounts_migrate/_preflight_deploy.py
fi
