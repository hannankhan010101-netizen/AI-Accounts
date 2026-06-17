"""Pagination helpers: UI next-button fallback and record merging."""

from __future__ import annotations

import logging
import re
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from playwright.sync_api import Page

from network_capture import CapturedResponse, NetworkCapture, dedupe_records, extract_records_from_body

logger = logging.getLogger(__name__)

NEXT_SELECTORS = [
    'a.paginate_button.next:not(.disabled)',
    '.pagination .next:not(.disabled)',
    'button:has-text("Next"):not([disabled])',
    'a:has-text("Next"):not(.disabled)',
    '[aria-label="Next"]:not([disabled])',
    '.dataTables_paginate .next:not(.disabled)',
    'li.next:not(.disabled) a',
    'button[rel="next"]:not([disabled])',
]

PAGINATION_QUERY_KEYS = ("start", "offset", "page", "pageNumber", "pageNum", "draw", "length", "limit", "skip")


def maximize_page_size(page: Page) -> None:
    """Set DataTables page length to maximum available (usually 100)."""
    selectors = [
        '.dataTables_length select',
        'select[name*="length"]',
        'select.form-select',
    ]
    for sel in selectors:
        loc = page.locator(sel).first
        try:
            if loc.count() == 0 or not loc.is_visible(timeout=1500):
                continue
            options = loc.locator("option")
            values: list[str] = []
            for i in range(options.count()):
                val = options.nth(i).get_attribute("value")
                if val and val.isdigit():
                    values.append(val)
            if values:
                max_val = max(values, key=int)
                loc.select_option(max_val)
                page.wait_for_timeout(2000)
                return
        except Exception:
            continue


def paginate_datatable_post(
    page: Page,
    capture: NetworkCapture,
    module_key: str,
    list_response: CapturedResponse,
    max_pages: int = 500,
) -> None:
    """Replay DataTables POST listing with incremented start offset."""
    if list_response.method.upper() != "POST" or not list_response.post_data:
        return

    total = detect_total_from_response(list_response.body)
    records = extract_records_from_body(list_response.body)
    if total is None or len(records) >= total:
        return

    page_size = len(records) or 25
    base_post = list_response.post_data

    for i in range(1, max_pages):
        start = page_size * i
        if start >= total:
            break

        new_post = re.sub(r"start=\d+", f"start={start}", base_post)
        if new_post == base_post:
            # append or replace length/start in form body
            if "start=" in base_post:
                new_post = re.sub(r"start=\d+", f"start={start}", base_post)
            else:
                new_post = base_post + f"&start={start}"

        try:
            result = page.evaluate(
                """async ({ url, postData, headers }) => {
                    const res = await fetch(url, {
                        method: 'POST',
                        credentials: 'include',
                        headers: {
                            'Accept': 'application/json, text/html, */*',
                            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                            'X-Requested-With': 'XMLHttpRequest',
                            ...headers,
                        },
                        body: postData,
                    });
                    const text = await res.text();
                    try { return JSON.parse(text); } catch { return null; }
                }""",
                {
                    "url": list_response.url,
                    "postData": new_post,
                    "headers": {
                        k: v
                        for k, v in list_response.request_headers.items()
                        if k.lower() in ("x-csrf-token", "x-requested-with")
                    },
                },
            )
        except Exception as exc:
            logger.debug("DataTables POST pagination failed: %s", exc)
            break

        if not result:
            break
        new_records = extract_records_from_body(result)
        if not new_records:
            break

        capture.responses.append(
            CapturedResponse(
                url=list_response.url,
                method="POST",
                status=200,
                content_type="application/json",
                body=result,
                module_key=module_key,
                post_data=new_post,
            )
        )
        if _count_module_records(capture, module_key) >= total:
            break


def paginate_module(
    page: Page,
    capture: NetworkCapture,
    module_key: str,
    max_pages: int = 200,
) -> list[CapturedResponse]:
    """
    Paginate a list screen until no more pages.
    Returns newly captured responses beyond initial load.
    """
    maximize_page_size(page)
    initial_count = len(capture.for_module(module_key))

    module_responses = capture.for_module(module_key)
    listing = _find_listing_response(module_responses)
    if listing:
        paginate_datatable_post(page, capture, module_key, listing)

    _click_next_until_done(page, capture, module_key, max_pages)
    return capture.for_module(module_key)[initial_count:]


def _find_listing_response(responses: list[CapturedResponse]) -> CapturedResponse | None:
    candidates = [
        r for r in responses
        if "_listing" in r.url or "_list" in r.url or isinstance(r.body, dict) and "recordsTotal" in r.body
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda r: detect_total_from_response(r.body) or 0)


def _click_next_until_done(
    page: Page,
    capture: NetworkCapture,
    module_key: str,
    max_pages: int,
) -> None:
    prev_record_count = _count_module_records(capture, module_key)

    for page_num in range(max_pages):
        next_btn = _find_next_button(page)
        if next_btn is None:
            break

        try:
            if not next_btn.is_visible(timeout=1000):
                break
            class_attr = next_btn.get_attribute("class") or ""
            if "disabled" in class_attr.lower():
                break
            aria_disabled = next_btn.get_attribute("aria-disabled")
            if aria_disabled == "true":
                break
        except Exception:
            break

        try:
            next_btn.click()
            page.wait_for_timeout(800)
            try:
                page.wait_for_load_state("networkidle", timeout=8000)
            except Exception:
                pass
        except Exception as exc:
            logger.debug("Next click failed on page %d: %s", page_num + 1, exc)
            break

        new_count = _count_module_records(capture, module_key)
        if new_count <= prev_record_count:
            # No new data — stop
            break
        prev_record_count = new_count
        logger.debug("Module %s: paginated to page %d (%d records)", module_key, page_num + 2, new_count)


def _find_next_button(page: Page):
    for sel in NEXT_SELECTORS:
        loc = page.locator(sel).first
        try:
            if loc.count() > 0:
                return loc
        except Exception:
            continue
    return None


def _count_module_records(capture: NetworkCapture, module_key: str) -> int:
    total = 0
    for resp in capture.for_module(module_key):
        total += len(extract_records_from_body(resp.body))
    return total


def detect_total_from_response(body: Any) -> int | None:
    """Read total record count from common pagination metadata."""
    if not isinstance(body, dict):
        return None
    for key in (
        "recordsTotal",
        "recordsFiltered",
        "total",
        "Total",
        "totalCount",
        "TotalCount",
        "count",
        "Count",
        "totalRecords",
    ):
        val = body.get(key)
        if isinstance(val, int) and val >= 0:
            return val
        if isinstance(val, str) and val.isdigit():
            return int(val)
    return None


def try_api_pagination(
    page: Page,
    capture: NetworkCapture,
    module_key: str,
    list_response: CapturedResponse,
    max_pages: int = 500,
) -> None:
    """
    Attempt to replay list endpoint with incremented page/offset params.
    Uses page.evaluate fetch() to stay in browser session context.
    """
    total = detect_total_from_response(list_response.body)
    records = extract_records_from_body(list_response.body)
    page_size = len(records) or 25

    if total is not None and len(records) >= total:
        return  # already have everything

    parsed = urlparse(list_response.url)
    query = parse_qs(parsed.query)

    param_name = _detect_pagination_param(query, list_response.body)
    if param_name is None:
        return

    current = _parse_int(query.get(param_name, ["0"])[0], 0)
    step = page_size if param_name in ("start", "offset", "skip") else 1

    for i in range(1, max_pages):
        next_val = current + (step * i)
        new_query = dict(query)
        new_query[param_name] = [str(next_val)]
        new_url = urlunparse(parsed._replace(query=urlencode(new_query, doseq=True)))

        try:
            result = page.evaluate(
                """async ({ url, method }) => {
                    const opts = { credentials: 'include', headers: { 'Accept': 'application/json' } };
                    const res = method === 'POST'
                        ? await fetch(url, { ...opts, method: 'POST' })
                        : await fetch(url, opts);
                    if (!res.ok) return null;
                    return await res.json();
                }""",
                {"url": new_url, "method": list_response.method},
            )
        except Exception as exc:
            logger.debug("API pagination fetch failed: %s", exc)
            break

        if not result:
            break

        new_records = extract_records_from_body(result)
        if not new_records:
            break

        capture.responses.append(
            CapturedResponse(
                url=new_url,
                method=list_response.method,
                status=200,
                content_type="application/json",
                body=result,
                module_key=module_key,
            )
        )

        if total is not None and _count_module_records(capture, module_key) >= total:
            break
        if len(new_records) < page_size:
            break


def _detect_pagination_param(query: dict[str, list[str]], body: Any) -> str | None:
    for key in PAGINATION_QUERY_KEYS:
        if key in query:
            return key
    if isinstance(body, dict) and "draw" in body:
        return "start"
    return "start" if query else None


def _parse_int(val: str, default: int) -> int:
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


def merge_all_records(responses: list[CapturedResponse]) -> list[dict[str, Any]]:
    all_records: list[dict[str, Any]] = []
    for resp in responses:
        all_records.extend(extract_records_from_body(resp.body))
    return dedupe_records(all_records)
