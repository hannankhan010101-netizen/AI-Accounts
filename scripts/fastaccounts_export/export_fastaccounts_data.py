#!/usr/bin/env python3
"""
FastAccounts full account data export.

Logs into https://my.fastaccounts.io/, navigates every major sidebar module,
captures internal JSON/XHR responses (with pagination), and writes consolidated JSON.

Usage:
  cd scripts/fastaccounts_export
  pip install -r requirements.txt
  playwright install chromium
  copy .env.example .env   # fill FA_EMAIL and FA_PASSWORD
  python export_fastaccounts_data.py
  python export_fastaccounts_data.py --discover --headed
  python export_fastaccounts_data.py --modules customers,sales_invoices

Known limits:
  - Report variants may need date filters; exports catalog + default payloads.
  - Binary attachments/PDFs are skipped unless JSON metadata exists.
  - Licensed modules absent from your sidebar appear as skipped_not_in_menu.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from browser_session import (
    BrowserSession,
    SessionConfig,
    capture_auth_from_response,
    create_session,
    discover_sidebar_links,
    login,
    navigate_to_module,
    open_settings_menu,
)
from modules_manifest import (
    CRITICAL_MODULE_KEYS,
    ALL_MODULES,
    ModuleDef,
    get_modules,
    get_settings_modules,
)
from html_capture import capture_form_fields, capture_html_tables
from network_capture import NetworkCapture, build_module_result
from pagination import paginate_module

SCRIPT_DIR = Path(__file__).resolve().parent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def load_config() -> SessionConfig:
    load_dotenv(SCRIPT_DIR / ".env")
    email = os.environ.get("FA_EMAIL", "").strip()
    password = os.environ.get("FA_PASSWORD", "").strip()
    if not email or not password:
        raise SystemExit(
            "Missing FA_EMAIL or FA_PASSWORD. Copy .env.example to .env and fill credentials."
        )
    headless_str = os.environ.get("FA_HEADLESS", "true").strip().lower()
    return SessionConfig(
        base_url=os.environ.get("FA_BASE_URL", "https://my.fastaccounts.io/").strip(),
        email=email,
        password=password,
        headless=headless_str not in ("0", "false", "no"),
        nav_timeout_ms=int(os.environ.get("FA_NAV_TIMEOUT_MS", "60000")),
        page_delay_ms=int(os.environ.get("FA_PAGE_DELAY_MS", "300")),
    )


def output_dir() -> Path:
    load_dotenv(SCRIPT_DIR / ".env")
    rel = os.environ.get("FA_OUTPUT_DIR", "output")
    out = SCRIPT_DIR / rel
    out.mkdir(parents=True, exist_ok=True)
    return out


def wait_for_listing_response(session: BrowserSession) -> None:
    """Allow DataTables AJAX to complete after navigation."""
    session.page.wait_for_timeout(5000)
    try:
        session.page.wait_for_load_state("networkidle", timeout=10_000)
    except Exception:
        pass


def export_module(
    session: BrowserSession,
    capture: NetworkCapture,
    module: ModuleDef,
) -> dict[str, Any]:
    """Navigate to module, capture data, paginate."""
    errors: list[str] = []
    capture.set_module(module.key)

    try:
        source_url = navigate_to_module(session, module)
    except Exception as exc:
        errors.append(f"Navigation failed: {exc}")
        return build_module_result(module.key, module.label, "", [], errors)

    wait_for_listing_response(session)
    session.wait_settle()
    session.page.wait_for_timeout(2000)

    try:
        paginate_module(session.page, capture, module.key)
    except Exception as exc:
        errors.append(f"Pagination partial failure: {exc}")

    final_responses = capture.for_module(module.key)
    for resp in final_responses:
        capture_auth_from_response(session, resp.url, resp.body)

    result = build_module_result(
        module.key,
        module.label,
        source_url,
        final_responses,
        errors,
    )

    if result["recordCount"] == 0:
        html_records = capture_html_tables(session.page)
        if not html_records and module.category == "settings":
            html_records = capture_form_fields(session.page)
        if html_records:
            result["records"] = html_records
            result["recordCount"] = len(html_records)
            result["errors"] = [e for e in result["errors"] if "No JSON" not in e]

    return result


def export_settings_modules(
    session: BrowserSession,
    capture: NetworkCapture,
    modules: list[ModuleDef],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    try:
        open_settings_menu(session)
        session.wait_settle()
    except Exception as exc:
        logger.warning("Settings menu open failed: %s", exc)

    for module in modules:
        logger.info("Exporting settings: %s", module.label)
        results.append(export_module(session, capture, module))
    return results


def run_export(
    *,
    discover: bool = False,
    headed: bool = False,
    module_filter: set[str] | None = None,
    include_settings: bool = True,
) -> tuple[dict[str, Any], dict[str, Any], int]:
    config = load_config()
    if headed:
        config.headless = False

    session = create_session(config)
    capture = NetworkCapture()
    capture.attach(session.page)

    exit_code = 0
    modules_exported: dict[str, Any] = {}
    all_errors: list[dict[str, str]] = []

    try:
        login(session)
        session.wait_settle()

        discovered_links = discover_sidebar_links(session)
        logger.info("Discovered %d sidebar links", len(discovered_links))

        operational = get_modules(module_filter)
        for module in operational:
            logger.info("Exporting: %s (%s)", module.label, module.key)
            result = export_module(session, capture, module)
            modules_exported[module.key] = result
            for err in result.get("errors", []):
                all_errors.append({"module": module.key, "message": err})
            if module.critical and result.get("recordCount", 0) == 0 and result.get("errors"):
                exit_code = 1
                logger.warning("Critical module %s has no records", module.key)

        if include_settings and (module_filter is None or module_filter & {m.key for m in get_settings_modules()}):
            settings_mods = get_settings_modules(module_filter)
            if settings_mods:
                for result in export_settings_modules(session, capture, settings_mods):
                    modules_exported[result["module"]] = result
                    for err in result.get("errors", []):
                        all_errors.append({"module": result["module"], "message": err})

        # Auto-detected sidebar links not in manifest
        manifest_labels = {m.label.lower() for m in ALL_MODULES}
        extra_links = [
            link for link in discovered_links
            if link["text"].lower() not in manifest_labels
        ]
        if extra_links:
            modules_exported["discovered_sidebar_links"] = {
                "module": "discovered_sidebar_links",
                "label": "Discovered Sidebar Links",
                "recordCount": len(extra_links),
                "records": extra_links,
                "rawResponses": [],
                "errors": [],
            }

    except Exception as exc:
        logger.error("Export failed: %s", exc)
        all_errors.append({"module": "_global", "message": str(exc)})
        exit_code = 2
    finally:
        session.close()

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    export_payload: dict[str, Any] = {
        "exportedAt": datetime.now(timezone.utc).isoformat(),
        "account": {"email": config.email},
        "baseUrl": config.base_url,
        "modules": modules_exported,
        "errors": all_errors,
    }

    summary = build_summary(export_payload, timestamp)

    out_dir = output_dir()
    export_file = out_dir / f"fastaccounts_export_{timestamp}.json"
    summary_file = out_dir / "export_summary.json"

    with export_file.open("w", encoding="utf-8") as f:
        json.dump(export_payload, f, indent=2, ensure_ascii=False, default=str)
    logger.info("Wrote %s", export_file)

    with summary_file.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
    logger.info("Wrote %s", summary_file)

    if discover:
        discovery_file = SCRIPT_DIR / "discovered_endpoints.json"
        with discovery_file.open("w", encoding="utf-8") as f:
            json.dump(capture.discovery_map(), f, indent=2, ensure_ascii=False)
        logger.info("Wrote %s", discovery_file)

    print_coverage_report(summary)

    # Re-check critical modules for exit code
    for key in CRITICAL_MODULE_KEYS:
        if module_filter and key not in module_filter:
            continue
        mod = modules_exported.get(key, {})
        if mod.get("recordCount", 0) == 0:
            logger.warning("Critical module '%s' exported 0 records", key)
            if exit_code == 0:
                exit_code = 1

    return export_payload, summary, exit_code


def build_summary(export_payload: dict[str, Any], timestamp: str) -> dict[str, Any]:
    modules = export_payload.get("modules", {})
    module_stats = []
    for key, data in modules.items():
        if not isinstance(data, dict):
            continue
        module_stats.append({
            "key": key,
            "label": data.get("label", key),
            "recordCount": data.get("recordCount", 0),
            "rawResponseCount": len(data.get("rawResponses", [])),
            "errorCount": len(data.get("errors", [])),
            "status": "ok" if data.get("recordCount", 0) > 0 or not data.get("errors") else "empty",
        })

    critical_failures = [
        s["key"] for s in module_stats
        if s["key"] in CRITICAL_MODULE_KEYS and s["recordCount"] == 0
    ]

    return {
        "timestamp": timestamp,
        "exportedAt": export_payload.get("exportedAt"),
        "accountEmail": export_payload.get("account", {}).get("email"),
        "totalModules": len(module_stats),
        "totalRecords": sum(s["recordCount"] for s in module_stats),
        "criticalFailures": critical_failures,
        "modules": module_stats,
        "errors": export_payload.get("errors", []),
    }


def print_coverage_report(summary: dict[str, Any]) -> None:
    print("\n" + "=" * 60)
    print("FastAccounts Export Summary")
    print("=" * 60)
    print(f"Account:       {summary.get('accountEmail', 'N/A')}")
    print(f"Modules:       {summary.get('totalModules', 0)}")
    print(f"Total records: {summary.get('totalRecords', 0)}")
    if summary.get("criticalFailures"):
        print(f"CRITICAL gaps: {', '.join(summary['criticalFailures'])}")
    print("-" * 60)
    for mod in summary.get("modules", []):
        status = mod.get("status", "?")
        print(
            f"  [{status:5}] {mod.get('label', mod.get('key'))}: "
            f"{mod.get('recordCount', 0)} records, "
            f"{mod.get('rawResponseCount', 0)} API responses"
        )
    if summary.get("errors"):
        print("-" * 60)
        print(f"Errors ({len(summary['errors'])}):")
        for err in summary["errors"][:20]:
            print(f"  - [{err.get('module')}] {err.get('message')}")
    print("=" * 60 + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export all FastAccounts account data to JSON")
    parser.add_argument(
        "--discover",
        action="store_true",
        help="Save discovered_endpoints.json with captured API URLs",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run browser in headed mode (visible window)",
    )
    parser.add_argument(
        "--modules",
        type=str,
        default="",
        help="Comma-separated module keys to export (default: all)",
    )
    parser.add_argument(
        "--no-settings",
        action="store_true",
        help="Skip settings mega-menu modules",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    module_filter: set[str] | None = None
    if args.modules.strip():
        module_filter = {k.strip() for k in args.modules.split(",") if k.strip()}

    _, _, exit_code = run_export(
        discover=args.discover,
        headed=args.headed,
        module_filter=module_filter,
        include_settings=not args.no_settings,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
