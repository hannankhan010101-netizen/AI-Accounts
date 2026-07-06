"""Server-side assistant tool execution with RBAC."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any

from app.core.exceptions import ForbiddenError, ValidationAppError
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.sales_invoice_repository import SalesInvoiceRepository
from app.services.auto_code_service import AutoCodeService
from app.services.permission_service import PermissionService


def _has(perms: list[str], code: str) -> bool:
    if "*" in perms:
        return True
    if code in perms:
        return True
    parts = code.split(".")
    for i in range(len(parts) - 1, 0, -1):
        if ".".join(parts[:i]) + ".*" in perms:
            return True
    return False


# Product cost/salePrice/lowStockLevel are Decimal(18,4): max 14 integer digits.
_QUANT = Decimal("0.0001")
_MONEY_MAX = Decimal("99999999999999.9999")


def _parse_amount(value: Any) -> tuple[Decimal | None, str | None]:
    """Parse a monetary/quantity argument from an LLM tool call.

    Returns ``(amount, error)``:
    - ``(None, None)``  -> not provided (caller should leave the field unset)
    - ``(None, msg)``   -> provided but invalid (caller should reject with ``msg``)
    - ``(Decimal, None)`` -> valid, normalized to 4 dp and within DB range
    """

    if value is None:
        return None, None
    if isinstance(value, str) and not value.strip():
        return None, None
    if isinstance(value, bool):  # bool is an int subclass; reject to avoid True->1
        return None, "must be a number, not true/false"
    try:
        parsed = Decimal(str(value).strip().replace(",", ""))
    except (InvalidOperation, ValueError):
        return None, "must be a valid number"
    if not parsed.is_finite():  # rejects NaN / Infinity (which slip past < 0)
        return None, "must be a finite number"
    if parsed < 0:
        return None, "cannot be negative"
    if parsed > _MONEY_MAX:
        return None, "is too large (maximum 99,999,999,999,999.9999)"
    return parsed.quantize(_QUANT, rounding=ROUND_HALF_UP), None


def _coerce_bool(value: Any, *, default: bool) -> bool:
    """Coerce an LLM-supplied flag to bool, treating string 'false'/'0'/'no' correctly."""

    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    s = str(value).strip().lower()
    if s in ("true", "1", "yes", "y", "on"):
        return True
    if s in ("false", "0", "no", "n", "off", ""):
        return False
    return default


def _clean_name(value: Any, *, limit: int = 200) -> str:
    """Collapse whitespace/newlines and cap length for a free-text name."""

    return " ".join(str(value or "").split())[:limit]


class AssistantToolHandlers:
    def __init__(
        self,
        *,
        permission_service: PermissionService,
        sales_invoice_repository: SalesInvoiceRepository,
        product_repository: ProductRepository,
        audit_log_repository: AuditLogRepository,
        auto_code_service: AutoCodeService,
    ) -> None:
        self._perms = permission_service
        self._invoices = sales_invoice_repository
        self._products = product_repository
        self._audit = audit_log_repository
        self._auto_code = auto_code_service

    async def execute(
        self,
        *,
        name: str,
        arguments: dict[str, Any],
        company_id: str,
        user_id: str,
        pathname: str,
    ) -> dict[str, Any]:
        perms = await self._perms.permissions_for(company_id=company_id, user_id=user_id)

        if name == "helpUser":
            return {
                "ok": True,
                "topic": arguments.get("topic", "general"),
                "pathname": pathname,
                "hint": "Use tours, sidebar navigation, or ask about a specific module.",
            }

        if name == "searchInvoices":
            if not any(
                _has(perms, p)
                for p in ("sales.read", "sales.invoices.read", "sales.invoices.create", "sales.*")
            ):
                return {"ok": False, "error": "Missing permission to view sales invoices."}
            q = str(arguments.get("query") or "").strip().lower()
            limit = min(int(arguments.get("limit") or 10), 20)
            rows = await self._invoices.list_invoices(company_id=company_id, take=50)
            out = []
            for inv in rows:
                num = (inv.invoiceNumber or "").lower()
                if q and q not in num:
                    continue
                out.append(
                    {
                        "id": inv.id,
                        "invoiceNumber": inv.invoiceNumber,
                        "status": inv.status,
                        "totalAmount": str(inv.totalAmount),
                        "invoiceDate": inv.invoiceDate.isoformat() if inv.invoiceDate else None,
                    }
                )
                if len(out) >= limit:
                    break
            if not q:
                out = out[:limit] if out else [
                    {
                        "id": inv.id,
                        "invoiceNumber": inv.invoiceNumber,
                        "status": inv.status,
                        "totalAmount": str(inv.totalAmount),
                    }
                    for inv in rows[:limit]
                ]
            return {"ok": True, "invoices": out}

        if name == "createInvoice":
            try:
                await self._perms.assert_allowed(
                    company_id=company_id,
                    user_id=user_id,
                    permission="sales.invoices.create",
                )
            except ForbiddenError as exc:
                detail = exc.detail if isinstance(exc.detail, dict) else {}
                return {"ok": False, "error": detail.get("message", "Forbidden")}
            return {
                "ok": True,
                "guidance": (
                    "Open Sales → Invoices → New. Select a customer, add lines, save as draft, "
                    "then post when ready. I cannot post without your confirmation."
                ),
                "href": "/sales/invoices/new",
                "customerId": arguments.get("customerId"),
            }

        if name == "fetchReports":
            if not any(_has(perms, p) for p in ("reports.read", "reports.*")):
                return {"ok": False, "error": "Missing permission to access reports."}
            return {
                "ok": True,
                "reports": [
                    {"id": "profit-loss", "title": "Profit & Loss", "href": "/reports/profit-loss"},
                    {"id": "balance-sheet", "title": "Balance Sheet", "href": "/reports/balance-sheet"},
                    {"id": "trial-balance", "title": "Trial Balance", "href": "/reports/trial-balance"},
                    {"id": "aged-receivables", "title": "Aged Receivables", "href": "/reports/aged-receivables"},
                ],
                "category": arguments.get("category"),
            }

        if name == "searchInventory":
            if not _has(perms, "inventory.products.read") and not _has(perms, "inventory.*") and "*" not in perms:
                return {"ok": False, "error": "Missing permission to view inventory."}
            q = str(arguments.get("query") or "").strip().lower()
            limit = min(int(arguments.get("limit") or 10), 20)
            products = await self._products.list_products(company_id=company_id, take=50)
            out = []
            for p in products:
                code = (getattr(p, "code", None) or getattr(p, "productCode", "") or "").lower()
                name_val = (getattr(p, "name", None) or "").lower()
                if q and q not in code and q not in name_val:
                    continue
                out.append(
                    {
                        "id": p.id,
                        "code": getattr(p, "code", None) or getattr(p, "productCode", None),
                        "name": getattr(p, "name", None),
                    }
                )
                if len(out) >= limit:
                    break
            if not q:
                out = [
                    {
                        "id": p.id,
                        "code": getattr(p, "code", None) or getattr(p, "productCode", None),
                        "name": getattr(p, "name", None),
                    }
                    for p in products[:limit]
                ]
            return {"ok": True, "products": out}

        if name == "createProduct":
            try:
                await self._perms.assert_allowed(
                    company_id=company_id,
                    user_id=user_id,
                    permission="inventory.products.create",
                )
            except ForbiddenError as exc:
                detail = exc.detail if isinstance(exc.detail, dict) else {}
                return {"ok": False, "error": detail.get("message", "Forbidden")}

            product_name = _clean_name(arguments.get("name"))
            if not product_name:
                return {"ok": False, "error": "Product name is required."}

            provided_code = _clean_name(arguments.get("code"), limit=64) or None

            price, price_err = _parse_amount(
                arguments.get("price")
                if arguments.get("price") is not None
                else arguments.get("salePrice")
            )
            if price_err:
                return {"ok": False, "error": f"Sale price {price_err}."}
            cost, cost_err = _parse_amount(arguments.get("cost"))
            if cost_err:
                return {"ok": False, "error": f"Cost {cost_err}."}
            is_stock = _coerce_bool(arguments.get("isStock"), default=True)

            try:
                code = await self._auto_code.resolve_code(
                    company_id=company_id,
                    entity_key="product",
                    provided=provided_code,
                )
            except ValidationAppError as exc:
                return {"ok": False, "error": str(exc)}

            existing = await self._products.get_by_codes(company_id=company_id, codes=[code])
            if existing:
                row = existing[0]
                return {
                    "ok": False,
                    "error": (
                        f"Product code '{code}' already exists. "
                        "To change its details (e.g. cost or price), call updateProduct instead."
                    ),
                    "existingProduct": {
                        "id": row.id,
                        "code": row.code,
                        "name": row.name,
                    },
                }

            try:
                row = await self._products.create_product(
                    company_id=company_id,
                    code=code,
                    name=product_name,
                    is_stock=is_stock,
                    cost=cost,
                    sale_price=price,
                )
            except Exception:  # noqa: BLE001 - surface a clean message, never a 500 to chat
                return {
                    "ok": False,
                    "error": (
                        f"Could not create product '{product_name}'. "
                        "The code may already be in use — try a different code."
                    ),
                }
            return {
                "ok": True,
                "product": {
                    "id": row.id,
                    "code": row.code,
                    "name": row.name,
                    "cost": str(row.cost),
                    "salePrice": str(row.salePrice),
                    "unit": row.unit,
                },
                "invalidate": ["products"],
            }

        if name == "updateProduct":
            try:
                await self._perms.assert_allowed(
                    company_id=company_id,
                    user_id=user_id,
                    permission="inventory.products.create",
                )
            except ForbiddenError as exc:
                detail = exc.detail if isinstance(exc.detail, dict) else {}
                return {"ok": False, "error": detail.get("message", "Forbidden")}

            product_id = str(arguments.get("id") or "").strip() or None
            code = _clean_name(arguments.get("code"), limit=64) or None

            row = None
            if product_id:
                row = await self._products.get_by_id(
                    company_id=company_id, product_id=product_id
                )
            elif code:
                matches = await self._products.get_by_codes(
                    company_id=company_id, codes=[code]
                )
                row = matches[0] if matches else None
            if row is None:
                return {
                    "ok": False,
                    "error": "Product not found. Provide the code or id of an existing product.",
                }

            data: dict[str, Any] = {}

            if "name" in arguments:
                new_name = _clean_name(arguments.get("name"))
                if not new_name:
                    return {"ok": False, "error": "Product name cannot be empty."}
                data["name"] = new_name

            if arguments.get("cost") is not None:
                cost, cost_err = _parse_amount(arguments.get("cost"))
                if cost_err:
                    return {"ok": False, "error": f"Cost {cost_err}."}
                data["cost"] = cost

            price_arg = (
                arguments.get("price")
                if arguments.get("price") is not None
                else arguments.get("salePrice")
            )
            if price_arg is not None:
                price, price_err = _parse_amount(price_arg)
                if price_err:
                    return {"ok": False, "error": f"Sale price {price_err}."}
                data["salePrice"] = price

            if arguments.get("isStock") is not None:
                data["isStock"] = _coerce_bool(arguments.get("isStock"), default=True)

            if not data:
                return {
                    "ok": False,
                    "error": "No fields to update. Specify at least one of name, cost, price, or isStock.",
                }

            try:
                updated = await self._products.update_product(
                    product_id=row.id,
                    company_id=company_id,
                    data=data,
                )
            except ValueError:
                return {"ok": False, "error": "Product not found."}
            except Exception:  # noqa: BLE001 - never surface a raw 500 to chat
                return {
                    "ok": False,
                    "error": f"Could not update product '{row.name}'. Please try again.",
                }

            return {
                "ok": True,
                "product": {
                    "id": updated.id,
                    "code": updated.code,
                    "name": updated.name,
                    "cost": str(updated.cost),
                    "salePrice": str(updated.salePrice),
                    "unit": updated.unit,
                },
                "invalidate": ["products"],
            }

        if name == "explainAuditEntry":
            if not any(_has(perms, p) for p in ("settings.users.read", "settings.read")):
                return {"ok": False, "error": "Missing permission to view audit log."}
            limit = min(int(arguments.get("limit") or 5), 20)
            tx_type = arguments.get("transactionType")
            rows = await self._audit.list_filtered(
                company_id=company_id,
                user_id=None,
                date_from=None,
                date_to=None,
                transaction_types=[tx_type] if tx_type else None,
                transaction_type_contains=None,
                transaction_id=None,
                take=limit,
            )
            entries = [
                {
                    "id": r.id,
                    "transactionType": r.transactionType,
                    "transactionId": r.transactionId,
                    "status": r.status,
                    "details": (r.details or "")[:200],
                    "createdAt": r.createdAt.isoformat() if r.createdAt else None,
                }
                for r in rows
            ]
            return {"ok": True, "entries": entries}

        return {"ok": False, "error": f"Unknown server tool: {name}"}
