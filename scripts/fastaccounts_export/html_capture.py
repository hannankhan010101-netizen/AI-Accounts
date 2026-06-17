"""Fallback capture for HTML form / table pages without JSON listing APIs."""

from __future__ import annotations

from typing import Any

from playwright.sync_api import Page


def capture_form_fields(page: Page) -> list[dict[str, Any]]:
    """Extract visible form inputs from the current page."""
    fields = page.evaluate(
        """() => {
            return Array.from(document.querySelectorAll('input, select, textarea'))
                .map(el => ({
                    name: el.name || el.id || '',
                    value: el.value || el.innerText || '',
                    type: el.type || el.tagName.toLowerCase(),
                    label: (el.labels && el.labels[0] ? el.labels[0].innerText : '') || ''
                }))
                .filter(x => x.name && x.type !== 'hidden' && x.type !== 'password');
        }"""
    )
    if not fields:
        return []
    return [{"formFields": fields}]


def capture_html_tables(page: Page) -> list[dict[str, Any]]:
    """Extract simple HTML table rows when no DataTables JSON exists."""
    rows = page.evaluate(
        """() => {
            const tables = Array.from(document.querySelectorAll('table'));
            const out = [];
            for (const table of tables) {
                const headers = Array.from(table.querySelectorAll('thead th, thead td'))
                    .map(th => (th.innerText || '').trim()).filter(Boolean);
                const bodyRows = Array.from(table.querySelectorAll('tbody tr'));
                if (bodyRows.length === 0) continue;
                for (const tr of bodyRows) {
                    const cells = Array.from(tr.querySelectorAll('td'))
                        .map(td => (td.innerText || '').trim());
                    if (cells.length === 0) continue;
                    if (headers.length === cells.length) {
                        const row = {};
                        headers.forEach((h, i) => { row[h || ('col_' + i)] = cells[i]; });
                        out.push(row);
                    } else {
                        out.push({ cells });
                    }
                }
            }
            return out.slice(0, 500);
        }"""
    )
    return rows if isinstance(rows, list) else []
