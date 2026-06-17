"""Intercept and collect JSON XHR responses during module navigation."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from html import unescape
from typing import Any
from urllib.parse import urlparse

from playwright.sync_api import Page, Response

logger = logging.getLogger(__name__)

# URL substrings that suggest data/list API calls.
API_URL_HINTS = (
    "/api/",
    "ajax",
    "datatable",
    "dataTable",
    "DataTable",
    "list",
    "get",
    "fetch",
    "load",
    "grid",
    "search",
    "report",
    "ledger",
    "invoice",
    "customer",
    "supplier",
    "product",
    "bank",
    "payment",
    "receipt",
    "bill",
    "order",
    "stock",
    "journal",
    "coa",
    "nominal",
    "dashboard",
    "index.php",
)

# Skip static assets and analytics.
SKIP_URL_PATTERNS = re.compile(
    r"\.(js|css|png|jpg|jpeg|gif|svg|woff|woff2|ttf|ico)(\?|$)|"
    r"google-analytics|googletagmanager|facebook|hotjar|sentry",
    re.I,
)

ID_FIELDS = (
    "id",
    "Id",
    "ID",
    "InvID",
    "VoucherID",
    "AccountNo",
    "CustomerAccountNo",
    "SupplierAccountNo",
    "ProductCode",
    "DocNo",
    "docNo",
    "VoucherNo",
    "InvoiceNo",
    "BillNo",
    "uuid",
    "UUID",
)


@dataclass
class CapturedResponse:
    url: str
    method: str
    status: int
    content_type: str
    body: Any
    module_key: str = ""
    post_data: str | None = None
    request_headers: dict[str, str] = field(default_factory=dict)

    def url_pattern(self) -> str:
        """Normalize URL for deduplication (strip query except pagination keys)."""
        parsed = urlparse(self.url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"


@dataclass
class NetworkCapture:
    responses: list[CapturedResponse] = field(default_factory=list)
    _seen_urls: set[str] = field(default_factory=set)
    _active_module: str = ""

    def attach(self, page: Page) -> None:
        page.on("response", self._on_response)

    def set_module(self, module_key: str) -> None:
        self._active_module = module_key

    def clear_module_buffer(self) -> None:
        """Clear responses for fresh capture on re-navigation."""
        pass  # keep all; tag by module_key instead

    def _on_response(self, response: Response) -> None:
        try:
            self._maybe_capture(response)
        except Exception as exc:
            logger.debug("Response capture skipped: %s", exc)

    def _maybe_capture(self, response: Response) -> None:
        url = response.url
        if SKIP_URL_PATTERNS.search(url):
            return
        if response.status >= 400:
            return

        content_type = (response.headers.get("content-type") or "").lower()
        is_listing = _url_looks_like_api(url) or "_listing" in url or "_list" in url

        if "json" not in content_type and not is_listing:
            if not _url_looks_like_api(url):
                return

        body = _parse_response_body(response)
        if body is None or body == "" or body == {} or body == []:
            return

        dedupe_key = f"{self._active_module}:{response.request.method}:{url}:{response.request.post_data or ''}"
        if dedupe_key in self._seen_urls:
            return
        self._seen_urls.add(dedupe_key)

        captured = CapturedResponse(
            url=url,
            method=response.request.method,
            status=response.status,
            content_type=content_type,
            body=body,
            module_key=self._active_module,
            post_data=response.request.post_data,
            request_headers=dict(response.request.headers),
        )
        self.responses.append(captured)
        logger.debug("Captured %s %s [%s]", response.request.method, url[:120], self._active_module)

    def for_module(self, module_key: str) -> list[CapturedResponse]:
        return [r for r in self.responses if r.module_key == module_key]

    def discovery_map(self) -> dict[str, list[dict[str, Any]]]:
        """Map module_key -> list of endpoint summaries."""
        result: dict[str, list[dict[str, Any]]] = {}
        for resp in self.responses:
            entry = {
                "url": resp.url,
                "method": resp.method,
                "status": resp.status,
                "urlPattern": resp.url_pattern(),
            }
            result.setdefault(resp.module_key, []).append(entry)
        return result


def _parse_response_body(response: Response) -> Any:
    """Parse JSON bodies even when served as text/html (FastAccounts DataTables)."""
    try:
        return response.json()
    except Exception:
        pass
    try:
        text = response.text().strip()
    except Exception:
        return None
    if not text:
        return None
    if text.startswith("{") or text.startswith("["):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None
    return None


def _strip_html(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    if "<" not in value:
        return unescape(value.strip())
    text = re.sub(r"<[^>]+>", " ", value)
    text = unescape(re.sub(r"\s+", " ", text)).strip()
    return text


def clean_record(rec: dict[str, Any]) -> dict[str, Any]:
    """Strip HTML from DataTables cell values and extract entity IDs from checkboxes."""
    cleaned: dict[str, Any] = {}
    for key, val in rec.items():
        if key in ("0", "selector_checkbox", "actions"):
            if isinstance(val, str):
                m = re.search(r'value="(\d+)"', val)
                if m and "entityId" not in cleaned:
                    cleaned["entityId"] = m.group(1)
            continue
        cleaned[key] = _strip_html(val)
    return cleaned


def _url_looks_like_api(url: str) -> bool:
    lower = url.lower()
    return any(h.lower() in lower for h in API_URL_HINTS)


def extract_records_from_body(body: Any) -> list[dict[str, Any]]:
    """Pull row-like dicts from common API response shapes."""
    if isinstance(body, list):
        return [r for r in body if isinstance(r, dict)]

    if not isinstance(body, dict):
        return []

    # DataTables format
    if "data" in body and isinstance(body["data"], list):
        rows = body["data"]
        if rows and isinstance(rows[0], list):
            return _datatables_rows_to_dicts(body)
        return [r for r in rows if isinstance(r, dict)]

    for key in ("rows", "Rows", "records", "Records", "items", "Items", "results", "Results", "list", "List"):
        val = body.get(key)
        if isinstance(val, list):
            return [r for r in val if isinstance(r, dict)]

    # Customer ledger style
    if "Message" in body and isinstance(body["Message"], list):
        return [r for r in body["Message"] if isinstance(r, dict)]

    # Nested data object
    data = body.get("Data") or body.get("data")
    if isinstance(data, dict):
        for key in ("rows", "records", "items", "list"):
            val = data.get(key)
            if isinstance(val, list):
                return [r for r in val if isinstance(r, dict)]

    # Single record wrapper
    if any(k in body for k in ID_FIELDS):
        return [body]

    return []


def _datatables_rows_to_dicts(body: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert DataTables array rows to dicts using columns metadata if present."""
    rows = body.get("data") or []
    columns = body.get("columns") or []
    col_names: list[str] = []
    for col in columns:
        if isinstance(col, dict):
            col_names.append(str(col.get("data") or col.get("name") or col.get("title") or ""))
        else:
            col_names.append(str(col))

    result: list[dict[str, Any]] = []
    for row in rows:
        if isinstance(row, dict):
            result.append(row)
        elif isinstance(row, list):
            if col_names and len(col_names) == len(row):
                result.append({col_names[i] or f"col_{i}": row[i] for i in range(len(row))})
            else:
                result.append({f"col_{i}": v for i, v in enumerate(row)})
    return result


def dedupe_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Merge records by stable ID fields."""
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for rec in records:
        key = _record_key(rec)
        if key in seen:
            continue
        seen.add(key)
        unique.append(rec)
    return unique


def _record_key(rec: dict[str, Any]) -> str:
    for field_name in ID_FIELDS:
        val = rec.get(field_name)
        if val is not None and str(val).strip():
            return f"{field_name}:{val}"
    # Fallback: hash salient values
    parts = sorted(f"{k}={v}" for k, v in rec.items() if v is not None)
    return "|".join(parts[:8]) if parts else json.dumps(rec, sort_keys=True, default=str)


def build_module_result(
    module_key: str,
    label: str,
    source_url: str,
    responses: list[CapturedResponse],
    errors: list[str],
) -> dict[str, Any]:
    """Assemble export payload for one module."""
    all_records: list[dict[str, Any]] = []
    raw_responses: list[dict[str, Any]] = []

    for resp in responses:
        is_listing = "_listing" in resp.url or (
            isinstance(resp.body, dict) and "recordsTotal" in resp.body
        )
        if is_listing or len(responses) <= 5:
            raw_responses.append({
                "url": resp.url,
                "method": resp.method,
                "status": resp.status,
                "body": resp.body,
            })
        all_records.extend(extract_records_from_body(resp.body))

    records = dedupe_records(all_records)
    records = [clean_record(r) for r in records]

    if not raw_responses and not errors:
        errors.append("No JSON API responses captured for this module")

    return {
        "module": module_key,
        "label": label,
        "sourceUrl": source_url,
        "recordCount": len(records),
        "records": records,
        "rawResponses": raw_responses,
        "errors": errors,
    }
