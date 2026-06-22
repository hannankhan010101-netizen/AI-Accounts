"""Server-side assistant tool execution with RBAC."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
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


def _to_decimal(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    if parsed < 0:
        return None
    return parsed


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
            if not _has(perms, "sales.invoices.create") and not _has(perms, "sales.*"):
                if not any(_has(perms, p) for p in ("sales.invoices.*", "financial.*", "*")):
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
            if not _has(perms, "financial.reports.read") and not _has(perms, "*"):
                if not _has(perms, "financial.*"):
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

            product_name = str(arguments.get("name") or "").strip()
            if not product_name:
                return {"ok": False, "error": "Product name is required."}

            provided_code = str(arguments.get("code") or "").strip() or None
            price = _to_decimal(arguments.get("price") if arguments.get("price") is not None else arguments.get("salePrice"))
            cost = _to_decimal(arguments.get("cost"))
            is_stock_raw = arguments.get("isStock")
            is_stock = True if is_stock_raw is None else bool(is_stock_raw)

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
                    "error": f"Product code '{code}' already exists.",
                    "existingProduct": {
                        "id": row.id,
                        "code": row.code,
                        "name": row.name,
                    },
                }

            row = await self._products.create_product(
                company_id=company_id,
                code=code,
                name=product_name,
                is_stock=is_stock,
                cost=cost,
                sale_price=price,
            )
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

        if name == "explainAuditEntry":
            if not _has(perms, "settings.audit.read") and not _has(perms, "*"):
                if not _has(perms, "financial.*"):
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
