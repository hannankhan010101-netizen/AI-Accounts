#!/usr/bin/env python3
"""HTTP smoke test after API + optional frontend deploy.

Usage:
  python scripts/_post_deploy_smoke.py --api-url https://api.example.com
  python scripts/_post_deploy_smoke.py --api-url https://api.example.com --frontend-url https://app.example.com
  python scripts/_post_deploy_smoke.py --api-url http://127.0.0.1:8000 \\
      --company-id cmpfm1nst0001lhq3rz09938z --token eyJ...
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

DEFAULT_TENANT = "cmpfm1nst0001lhq3rz09938z"


def _get(
    url: str,
    *,
    token: str | None = None,
    origin: str | None = None,
    timeout: float = 20.0,
) -> tuple[int, str, dict[str, str]]:
    req = urllib.request.Request(url)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    if origin:
        req.add_header("Origin", origin)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            headers = {k.lower(): v for k, v in resp.headers.items()}
            return resp.status, resp.read().decode("utf-8", errors="replace"), headers
    except urllib.error.URLError as exc:
        raise ConnectionError(f"Could not reach {url}: {exc.reason}") from exc
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        headers = {k.lower(): v for k, v in exc.headers.items()}
        return exc.code, body, headers


def _print_integrations(body: str) -> None:
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        print(f"    (non-JSON response, {len(body)} bytes)")
        return
    payload = data.get("result") if isinstance(data, dict) else data
    if not isinstance(payload, dict):
        print(f"    unexpected shape: {type(payload).__name__}")
        return
    for name in ("fbr", "paypro", "kuickpay"):
        row = payload.get(name)
        if isinstance(row, dict):
            print(
                f"    {name}: mode={row.get('mode')} ready={row.get('ready')}"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description="Post-deploy API smoke test")
    parser.add_argument("--api-url", required=True, help="API origin, no trailing slash")
    parser.add_argument("--frontend-url", default="", help="Optional Vercel origin for /login check")
    parser.add_argument(
        "--company-id",
        default=DEFAULT_TENANT,
        help=f"Tenant id (default: {DEFAULT_TENANT})",
    )
    parser.add_argument("--token", default="", help="Bearer JWT for authenticated tenant checks")
    args = parser.parse_args()

    base = args.api_url.rstrip("/")
    frontend = args.frontend_url.rstrip("/") if args.frontend_url else ""
    issues: list[str] = []

    print(f"=== Post-deploy smoke ({base}) ===\n")

    try:
        status, body, headers = _get(f"{base}/health")
    except ConnectionError as exc:
        print(f"  GET /health -> unreachable")
        print(f"    {exc}")
        print("\n  SMOKE: FAIL")
        return 1

    print(f"  GET /health -> {status}")
    if status != 200:
        issues.append(f"/health returned {status}")
    elif "ok" not in body.lower() and "healthy" not in body.lower():
        print(f"    body: {body[:200]}")

    status, _, _ = _get(f"{base}/docs")
    print(f"  GET /docs -> {status}")
    if status not in {200, 307, 308}:
        issues.append(f"/docs returned {status}")

    status, _, _ = _get(f"{base}/openapi.json")
    print(f"  GET /openapi.json -> {status}")
    if status != 200:
        issues.append(f"/openapi.json returned {status}")

    if frontend:
        status, _, _ = _get(f"{frontend}/login")
        print(f"  GET {frontend}/login -> {status}")
        if status not in {200, 307, 308}:
            issues.append(f"frontend /login returned {status}")

        status, body, cors_headers = _get(
            f"{base}/health",
            origin=frontend,
        )
        acao = cors_headers.get("access-control-allow-origin", "")
        print(f"  CORS preflight (Origin: {frontend}) -> {status}, ACAO={acao or '(none)'}")
        if status != 200:
            issues.append(f"CORS health check returned {status}")
        elif acao and acao not in {frontend, "*"}:
            issues.append(f"CORS ACAO mismatch: {acao!r} (expected {frontend})")

    token = args.token.strip()
    company_id = args.company_id.strip()
    if company_id and token:
        path = f"{base}/api/v1/companies/{company_id}/integrations/readiness"
        status, body, _ = _get(path, token=token)
        print(f"  GET integrations/readiness -> {status}")
        if status == 200:
            _print_integrations(body)
        else:
            issues.append(f"integrations/readiness returned {status}")
    elif company_id:
        print("  (skip authenticated checks — pass --token for integrations/readiness)")

    if issues:
        print("\n  SMOKE: FAIL")
        for item in issues:
            print(f"    - {item}")
        return 1

    print("\n  SMOKE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
