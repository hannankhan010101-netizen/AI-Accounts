"""Groq function-calling tool definitions."""

from __future__ import annotations

from typing import Any

CLIENT_TOOLS = frozenset(
    {
        "navigate",
        "openModal",
        "highlightElement",
        "startTour",
        "explainScreen",
    }
)

SERVER_TOOLS = frozenset(
    {
        "helpUser",
        "searchInvoices",
        "createInvoice",
        "fetchReports",
        "searchInventory",
        "createProduct",
        "explainAuditEntry",
    }
)

# Tool names allowed per assistant mode (keeps Groq tool-calling reliable).
MODE_TOOL_NAMES: dict[str, frozenset[str]] = {
    "audit": frozenset(
        {
            "navigate",
            "explainScreen",
            "helpUser",
            "explainAuditEntry",
            "startTour",
        }
    ),
    "invoice": frozenset(
        {
            "navigate",
            "explainScreen",
            "helpUser",
            "searchInvoices",
            "createInvoice",
        }
    ),
    "reports": frozenset(
        {
            "navigate",
            "explainScreen",
            "helpUser",
            "fetchReports",
        }
    ),
    "inventory": frozenset(
        {
            "navigate",
            "explainScreen",
            "helpUser",
            "searchInventory",
            "createProduct",
        }
    ),
    "reconciliation": frozenset(
        {
            "navigate",
            "explainScreen",
            "helpUser",
        }
    ),
    "onboarding": frozenset(
        {
            "navigate",
            "startTour",
            "explainScreen",
            "helpUser",
            "highlightElement",
        }
    ),
    "erp_help": frozenset(
        {
            "navigate",
            "explainScreen",
            "helpUser",
            "searchInvoices",
            "createInvoice",
            "fetchReports",
            "searchInventory",
            "createProduct",
            "explainAuditEntry",
        }
    ),
}


def _fn(
    name: str,
    description: str,
    properties: dict[str, Any],
    required: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required or [],
            },
        },
    }


def _all_tool_defs() -> dict[str, dict[str, Any]]:
    return {
        "navigate": _fn(
            "navigate",
            "Navigate the user to an ERP route (must be an allowed app path).",
            {"route": {"type": "string", "description": "Path e.g. /sales/invoices"}},
            ["route"],
        ),
        "openModal": _fn(
            "openModal",
            "Open a known modal by id.",
            {"id": {"type": "string", "description": "Modal id e.g. keyboard-shortcuts"}},
            ["id"],
        ),
        "highlightElement": _fn(
            "highlightElement",
            "Highlight a DOM element by CSS selector for guidance.",
            {"selector": {"type": "string"}},
            ["selector"],
        ),
        "startTour": _fn(
            "startTour",
            "Start a guided onboarding tour.",
            {"id": {"type": "string", "description": "Tour id e.g. onboard.sell"}},
            ["id"],
        ),
        "explainScreen": _fn(
            "explainScreen",
            "Summarize what the current screen is for.",
            {"pathname": {"type": "string"}},
            [],
        ),
        "helpUser": _fn(
            "helpUser",
            "Return contextual help for the user's question.",
            {"topic": {"type": "string"}},
            [],
        ),
        "searchInvoices": _fn(
            "searchInvoices",
            "Search recent sales invoices (requires permission).",
            {
                "query": {"type": "string", "description": "Invoice number or customer hint"},
                "limit": {"type": "integer", "description": "Max rows", "default": 10},
            },
            [],
        ),
        "createInvoice": _fn(
            "createInvoice",
            "Explain how to create an invoice or return draft guidance (no auto-post).",
            {"customerId": {"type": "string"}},
            [],
        ),
        "fetchReports": _fn(
            "fetchReports",
            "List available financial reports metadata.",
            {"category": {"type": "string", "description": "Optional filter"}},
            [],
        ),
        "searchInventory": _fn(
            "searchInventory",
            "Search products/inventory items.",
            {
                "query": {"type": "string", "description": "Search text"},
                "limit": {"type": "integer", "description": "Max rows", "default": 10},
            },
            [],
        ),
        "createProduct": _fn(
            "createProduct",
            (
                "Create a product in inventory after the user confirms details. "
                "Requires inventory.products.create permission. "
                "Call this tool before claiming success — never invent product creation."
            ),
            {
                "name": {"type": "string", "description": "Product display name"},
                "code": {"type": "string", "description": "Product code (optional if auto-code enabled)"},
                "price": {
                    "type": "number",
                    "description": "Sale price / unit price (optional)",
                },
                "cost": {"type": "number", "description": "Cost price (optional)"},
                "isStock": {
                    "type": "boolean",
                    "description": "Whether the item is a stock product (default true)",
                },
            },
            ["name"],
        ),
        "explainAuditEntry": _fn(
            "explainAuditEntry",
            "Fetch recent audit log entries for the company.",
            {
                "transactionType": {
                    "type": "string",
                    "description": "Optional filter e.g. assistant.query",
                },
                "limit": {"type": "integer", "description": "Max rows", "default": 5},
            },
            [],
        ),
    }


def tools_for_mode(mode: str, pathname: str = "") -> list[dict[str, Any]]:
    """Return a small, mode-appropriate Groq tool list (max ~8 tools)."""

    resolved = mode if mode in MODE_TOOL_NAMES else "erp_help"
    if resolved == "erp_help" and pathname:
        if "/settings" in pathname and (
            "audit" in pathname or "user-log" in pathname
        ):
            resolved = "audit"
        elif "/sales/invoices" in pathname:
            resolved = "invoice"
        elif "/reports" in pathname:
            resolved = "reports"
        elif "/inventory" in pathname:
            resolved = "inventory"

    allowed = MODE_TOOL_NAMES.get(resolved, MODE_TOOL_NAMES["erp_help"])
    catalog = _all_tool_defs()
    return [catalog[name] for name in catalog if name in allowed]


def is_client_tool(name: str) -> bool:
    return name in CLIENT_TOOLS


def sanitize_tool_calls(tool_calls: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Drop malformed tool calls from the model."""

    out: list[dict[str, Any]] = []
    for tc in tool_calls:
        name = (tc.get("name") or "").strip()
        if not name:
            continue
        if name not in CLIENT_TOOLS and name not in SERVER_TOOLS:
            continue
        out.append(tc)
    return out
