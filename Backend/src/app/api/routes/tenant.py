"""Tenant-scoped routes under ``/api/v1/companies/{company_id}``."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Annotated, Any, Literal
from uuid import uuid4

from decimal import Decimal

from fastapi import APIRouter, Depends, File, Form, Header, Query, Request, Response, UploadFile
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.api.dependencies.deps import (
    get_approval_engine_service,
    get_approval_policy_service,
    get_grni_service,
    get_assembly_service,
    get_fx_revaluation_service,
    get_fbr_repository,
    get_fbr_service,
    get_paypro_service,
    get_kuickpay_service,
    get_clickhouse_schema_service,
    get_activity_service,
    get_my_tasks_service,
    get_aging_service,
    get_allocation_service,
    get_attachment_service,
    get_audit_log_service,
    get_security_audit_service,
    get_bank_payment_service,
    get_conversion_service,
    get_bank_receipt_repository,
    get_bank_repository,
    get_bank_transfer_repository,
    get_business_information_repository,
    get_coa_repository,
    get_customer_repository,
    get_project_repository,
    get_location_repository,
    get_budget_service,
    get_document_number_service,
    get_auto_code_service,
    get_last_rate_service,
    get_transaction_template_repository,
    get_batch_document_service,
    get_advance_return_service,
    get_recurring_schedule_repository,
    get_recurring_schedule_service,
    get_import_job_service,
    get_journal_repository,
    get_read_journal_repository,
    get_read_prisma,
    get_read_aging_service,
    get_dashboard_repository,
    get_journal_service,
    get_lock_date_repository,
    get_lock_date_service,
    get_bank_reconciliation_service,
    get_outbox_worker_service,
    get_posting_engine,
    get_posting_service,
    get_subledger_tieout_service,
    get_product_repository,
    get_purchase_order_repository,
    get_quotation_repository,
    get_report_service,
    get_sales_credit_repository,
    get_sales_invoice_repository,
    get_sales_order_repository,
    get_sales_receipt_repository,
    get_delivery_note_repository,
    get_extended_reports_service,
    get_goods_receipt_note_repository,
    get_goods_issue_repository,
    get_pdc_issued_repository,
    get_pdc_received_repository,
    get_pdc_service,
    get_product_batch_repository,
    get_smart_settings_repository,
    get_smart_settings_runtime,
    get_app_settings_service,
    get_onboarding_repository,
    get_onboarding_release_repository,
    get_platform_onboarding_release_repository,
    get_email_service,
    get_company_repository,
    get_stock_adjustment_repository,
    get_stock_transfer_repository,
    get_supplier_bill_repository,
    get_supplier_credit_repository,
    get_supplier_payment_repository,
    get_supplier_repository,
    get_taxes_config_repository,
    get_tax_calculation_service,
    get_prisma,
    get_membership_repository,
    get_user_repository,
    get_module_entitlement_service,
    get_custom_field_service,
    get_product_uom_service,
    resolve_tenant,
    get_permission_service,
    require_permission,
    require_module,
    require_module_access,
    require_module_list_read,
    require_module_reports,
    get_module_access_service,
    get_role_repository,
    get_user_invite_service,
    get_invite_email_template_service,
    get_subscription_billing_service,
    get_advance_users_service,
    get_field_masking_service,
    get_sales_invoice_email_service,
    get_document_reversal_service,
    get_inventory_quantity_service,
    get_inventory_stock_guard_service,
)
from app.api.dependencies.deps import JwtClaims
from app.models.requests.bank_reconciliation_requests import (
    BankReconciliationClearRequest,
    BankReconciliationStartRequest,
    JournalReverseRequest,
)
from app.models.requests.bank_requests import (
    BankPaymentCreateRequest,
    BankReceiptCreateRequest,
    BankTransferCreateRequest,
)
from app.models.requests.coa_requests import (
    CreateNominalRequest,
    CreateSectionRequest,
    MoveNominalRequest,
    ReorderSectionRequest,
    UpdateCategoryTypeRequest,
    UpdateNominalRequest,
)
from app.models.requests.journal_requests import JournalCreateRequest, JournalUpdateRequest
from app.models.requests.template_requests import TransactionTemplateCreateRequest
from app.models.requests.masters_requests import (
    CreateBankAccountRequest,
    CreateCustomerRequest,
    CreateProductRequest,
    CreateSupplierRequest,
)
from app.models.requests.delivery_requests import (
    DeliveryNoteCreateRequest,
    GoodsReceiptNoteCreateRequest,
)
from app.models.requests.inventory_requests import (
    ProductBatchCreateRequest,
    StockAdjustmentCreateRequest,
    StockTransferCreateRequest,
)
from app.models.requests.pdc_requests import (
    PdcClearIssuedRequest,
    PdcClearReceivedRequest,
    PdcIssuedCreateRequest,
    PdcReceivedCreateRequest,
    PdcStatusUpdateRequest,
)
from app.models.requests.advance_return_requests import AdvanceReturnRequest
from app.models.requests.purchases_requests import (
    BatchSupplierBillCreateRequest,
    PurchaseOrderCreateRequest,
    SupplierBillCreateRequest,
    SupplierCreditCreateRequest,
    SupplierPaymentCreateRequest,
)
from app.models.requests.sales_requests import (
    BatchSalesInvoiceCreateRequest,
    QuotationCreateRequest,
    SalesCreditCreateRequest,
    SalesInvoiceCreateRequest,
    SalesInvoiceEmailRequest,
    SalesOrderCreateRequest,
    SalesReceiptCreateRequest,
    StatusTransitionRequest,
)
from app.models.requests.recurring_requests import (
    RecurringScheduleCreateRequest,
    RecurringScheduleUpdateRequest,
)
from app.models.requests.approval_requests import ApprovalRequestCreate
from app.models.requests.budget_requests import BudgetCreateRequest, BudgetUpdateRequest
from app.models.requests.assembly_requests import (
    AssemblyJobCreateRequest,
    AssemblyTemplateCreateRequest,
)
from app.models.requests.fx_requests import FxRevaluationRequest
from app.models.requests.master_data_requests import (
    CreateLocationRequest,
    CreateProjectRequest,
    UpdateLocationRequest,
    UpdateProjectRequest,
)
from app.models.requests.paypro_requests import PayproInitiateRequest, PayproWebhookRequest
from app.models.requests.payment_allocate_requests import PaymentAllocateRequest
from app.models.requests.receipt_allocate_requests import ReceiptAllocateRequest
from app.models.requests.lock_date_requests import LockDatePerUserRequest
from app.models.requests.platform_requests import (
    CreateAttachmentRequest,
    CreateImportJobRequest,
    ReserveDocumentNumberRequest,
    UpsertApprovalPolicyRequest,
)
from app.models.requests.report_requests import (
    ReportExportRequest,
    ReportRunRequest,
    ReportSyncExportRequest,
)
from app.models.requests.p11_requests import (
    CustomFieldDefinitionCreateRequest,
    CustomFieldsPatchRequest,
    ModuleEntitlementsReplaceRequest,
    ProductUomUpsertRequest,
    BillingWebhookRequest,
    CheckoutSessionRequest,
    PortalSessionRequest,
    DocumentVoidRequest,
    GoodsIssueLineVoidRequest,
)
from app.services.module_entitlement_service import ModuleEntitlementService
from app.services.module_access_service import ModuleAccessService
from app.services.custom_field_service import CustomFieldService
from app.services.product_uom_service import ProductUomService
from app.constants.permission_catalog import PERMISSION_TREE
from app.repositories.role_repository import RoleRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.location_repository import LocationRepository
from app.models.requests.onboarding_requests import (
    OnboardingAssistantRequest,
    OnboardingEventsBody,
    OnboardingProgressBody,
)
from app.models.requests.onboarding_release_requests import (
    OnboardingReleaseCreateRequest,
    OnboardingReleaseUpdateRequest,
)
from app.models.requests.role_requests import (
    AssignUserRoleRequest,
    InviteUserRequest,
    ReinviteByEmailRequest,
    ReinviteUserRequest,
    BulkAssignRoleRequest,
    BulkUserIdsRequest,
    RoleCloneBatchRequest,
    RoleCloneRequest,
    RoleCreateRequest,
    RoleImportRequest,
    RoleUpdateRequest,
    UpdateIpAllowlistRequest,
)
from app.models.requests.invite_email_requests import (
    InviteEmailPreviewRequest,
    InviteEmailTemplateRequest,
)
from app.constants.invite_email_defaults import (
    DEFAULT_INVITE_EMAIL_TEMPLATE,
    DEFAULT_WELCOME_EMAIL_TEMPLATE,
)
from app.services.invite_email_template_service import (
    InviteEmailTemplateService,
    apply_placeholders,
)
from app.services.user_invite_service import UserInviteService
from app.services.role_import_parser import describe_role_import_file, parse_role_import_file
from app.constants.role_import import ROLE_IMPORT_ASYNC_THRESHOLD
from app.services.audit_log_csv import audit_log_entries_to_csv
from app.services.email_service import EmailService
from app.services.permission_service import PermissionService
from app.services.permission_validation_service import (
    known_codes_sorted,
    strict_validation_error,
    validate_role_permissions,
)
from app.core.security import hash_password
from app.services.document_reversal_service import DocumentReversalService
from app.services.inventory_quantity_service import InventoryQuantityService
from app.services.inventory_stock_guard_service import InventoryStockGuardService
from app.services.subscription_billing_service import SubscriptionBillingService
from app.services.advance_users_service import AdvanceUsersService
from app.services.field_masking_service import FieldMaskingService
from app.services.sales_invoice_email_service import SalesInvoiceEmailService
from app.repositories.bank_repository import BankRepository
from app.repositories.business_information_repository import BusinessInformationRepository
from app.repositories.bank_receipt_repository import BankReceiptRepository
from app.repositories.user_repository import UserRepository
from app.repositories.bank_transfer_repository import BankTransferRepository
from app.repositories.coa_repository import CoaRepository
from app.repositories.delivery_repository import (
    DeliveryNoteRepository,
    GoodsReceiptNoteRepository,
)
from app.repositories.inventory_repository import (
    ProductBatchRepository,
    StockAdjustmentRepository,
    StockTransferRepository,
)
from app.repositories.dashboard_repository import DashboardRepository
from app.repositories.journal_repository import JournalRepository
from app.repositories.goods_issue_repository import GoodsIssueRepository
from app.repositories.pdc_repository import (
    PdcIssuedRepository,
    PdcReceivedRepository,
)
from app.repositories.purchase_order_repository import PurchaseOrderRepository
from app.repositories.quotation_repository import QuotationRepository
from app.repositories.sales_credit_repository import SalesCreditRepository
from app.repositories.sales_order_repository import SalesOrderRepository
from app.repositories.sales_receipt_repository import SalesReceiptRepository
from app.repositories.supplier_credit_repository import SupplierCreditRepository
from app.repositories.supplier_payment_repository import SupplierPaymentRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.lock_date_repository import LockDateRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.sales_invoice_repository import SalesInvoiceRepository
from app.repositories.smart_settings_repository import SmartSettingsRepository
from app.repositories.company_repository import CompanyRepository
from app.repositories.onboarding_repository import OnboardingRepository
from app.repositories.onboarding_release_repository import OnboardingReleaseRepository
from app.repositories.platform_onboarding_release_repository import (
    PlatformOnboardingReleaseRepository,
)
from app.repositories.supplier_bill_repository import SupplierBillRepository
from app.repositories.supplier_repository import SupplierRepository
from app.repositories.taxes_config_repository import TaxesConfigRepository
from app.services.approval_engine_service import ApprovalEngineService
from app.services.smart_settings_runtime import SmartSettingsRuntime
from app.api.approval_post_guard import guard_document_post
from app.services.approval_policy_service import ApprovalPolicyService
from app.services.budget_service import BudgetService
from app.services.assembly_service import AssemblyService
from app.services.fx_revaluation_service import FxRevaluationService
from app.services.fbr_service import FbrService
from app.services.paypro_service import PayproService
from app.services.security_audit_service import SecurityAuditService
from app.services.kuickpay_service import KuickpayService
from app.services.clickhouse_schema_service import ClickHouseSchemaService
from app.services.grni_service import GrniService
from app.services.bank_payment_service import BankPaymentService
from app.services.attachment_service import AttachmentService
from app.services.audit_log_service import AuditLogService
from app.services.document_number_service import DocumentNumberService
from app.services.aging_service import AgingService
from app.services.allocation_service import AllocationLine, AllocationService
from app.services.conversion_service import ConversionService
from app.services.extended_reports_service import ExtendedReportsService
from app.services.import_excel_service import parse_upload
from app.services.import_job_service import ImportJobService
from app.services.journal_service import JournalService
from app.services.auto_code_service import AutoCodeService
from app.services.last_rate_service import LastRateService
from app.repositories.transaction_template_repository import TransactionTemplateRepository
from app.repositories.recurring_schedule_repository import RecurringScheduleRepository
from app.services.batch_document_service import BatchDocumentService
from app.services.advance_return_service import AdvanceReturnService
from app.services.recurring_schedule_service import RecurringScheduleService
from app.services.lock_date_service import LockDateService
from app.core.exceptions import NotFoundError, ValidationAppError
from app.core.http_cache import REFERENCE_CACHE_CONTROL
from app.services.activity_service import ActivityService
from app.services.my_tasks_service import MyTasksService
from app.services.app_settings_service import AppSettingsService
from app.services.bank_reconciliation_service import BankReconciliationService
from app.services.outbox_worker_service import OutboxWorkerService
from app.services.pdc_service import PdcService
from app.services.posting_engine import PostingEngine
from app.services.subledger_tieout_service import SubledgerTieoutService
from app.services.posting_service import PostingService
from app.services.report_service import ReportService
from app.services.tax_calculation_service import TaxCalculationService
from app.repositories.membership_repository import MembershipRepository
from prisma_generated import Prisma

router = APIRouter(
    prefix="/api/v1/companies/{company_id}",
    tags=["Tenant"],
    dependencies=[Depends(resolve_tenant)],
)


def _dump_rows(rows: list[Any]) -> list[dict[str, Any]]:
    """Serialize ORM rows to JSON-friendly dicts."""

    return [jsonable_encoder(r) for r in rows]


def _parse_datetime(value: Any) -> datetime | None:
    """Parse ISO-8601 strings from JSON bodies."""

    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    return None


async def _taxed_planning_lines(
    *,
    company_id: str,
    raw_lines: list[dict[str, Any]],
    tax_service: TaxCalculationService,
) -> list[dict[str, Any]]:
    """Apply GST from taxes config to quotation / order planning lines."""

    taxed = await tax_service.compute_sales_lines(
        company_id=company_id, raw_lines=raw_lines
    )
    return [line.to_repo_dict() for line in taxed.lines]


@router.get("/coa/categories")
async def list_coa_categories(
    company_id: str,
    coa_repository: Annotated[CoaRepository, Depends(get_coa_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    """Chart of accounts categories."""

    rows = await coa_repository.list_categories(company_id=company_id)
    return {"result": _dump_rows(rows)}


@router.put("/coa/categories/{category_id}/type")
async def update_coa_category_type(
    company_id: str,
    category_id: str,
    body: UpdateCategoryTypeRequest,
    coa_repository: Annotated[CoaRepository, Depends(get_coa_repository)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    """Set the P&L/BS classification on a category (§9.1.1, drives P&L + BS reports)."""

    try:
        row = await coa_repository.update_category_type(
            company_id=company_id,
            category_id=category_id,
            category_type=body.category_type,
        )
    except ValueError as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(row)}


@router.get("/coa/tree", response_model=None)
async def get_coa_tree(
    company_id: str,
    coa_repository: Annotated[CoaRepository, Depends(get_coa_repository)],
    if_none_match: str | None = Header(default=None, alias="If-None-Match"),
) -> Response | dict:
    """Hierarchical chart: category → section → nominal (§9.1.1)."""

    try:
        revision = await coa_repository.tree_revision_token(company_id=company_id)
    except Exception:  # noqa: BLE001
        tree = await coa_repository.list_tree(company_id=company_id)
        node_count = sum(
            1
            + len(cat.get("sections") or [])
            + sum(len(sec.get("nominals") or []) for sec in (cat.get("sections") or []))
            for cat in tree
        )
        revision = str(node_count)
        etag = CoaRepository.tree_etag(revision)
        cache_headers = {"ETag": f'"{etag}"', "Cache-Control": REFERENCE_CACHE_CONTROL}
        return JSONResponse(content={"result": tree}, headers=cache_headers)

    etag = CoaRepository.tree_etag(revision)
    cache_headers = {"ETag": f'"{etag}"', "Cache-Control": REFERENCE_CACHE_CONTROL}
    if if_none_match and if_none_match.strip('"') == etag:
        return Response(status_code=304, headers=cache_headers)
    tree = await coa_repository.list_tree(company_id=company_id)
    return JSONResponse(content={"result": tree}, headers=cache_headers)


@router.get("/coa/sections")
async def list_coa_sections(
    company_id: str,
    coa_repository: Annotated[CoaRepository, Depends(get_coa_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    """Sections joined with category for the Section listing (§9.1.4)."""

    rows = await coa_repository.list_sections(company_id=company_id)
    return {"result": rows}


@router.post("/coa/sections", status_code=201)
async def create_coa_section(
    company_id: str,
    body: CreateSectionRequest,
    coa_repository: Annotated[CoaRepository, Depends(get_coa_repository)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    """Create a section under a category (§9.1.4 Section New)."""

    try:
        row = await coa_repository.create_section(
            company_id=company_id,
            category_id=body.category_id,
            code=body.code,
            name=body.name,
        )
    except ValueError as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(row)}


@router.put("/coa/sections/{section_id}/reorder")
async def reorder_coa_section(
    company_id: str,
    section_id: str,
    body: ReorderSectionRequest,
    coa_repository: Annotated[CoaRepository, Depends(get_coa_repository)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    """Move a section up or down within its category (§9.1.4)."""

    try:
        row = await coa_repository.reorder_section(
            company_id=company_id,
            section_id=section_id,
            direction=body.direction,
        )
    except ValueError as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(row)}


@router.post("/coa/nominals", status_code=201)
async def create_coa_nominal(
    company_id: str,
    body: CreateNominalRequest,
    coa_repository: Annotated[CoaRepository, Depends(get_coa_repository)],
    auto_code_service: Annotated[AutoCodeService, Depends(get_auto_code_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    """Create a nominal account under a section (§9.1.2 Nominal Account New)."""

    from fastapi import HTTPException

    try:
        code = await auto_code_service.resolve_code(
            company_id=company_id, entity_key="nominal", provided=body.code
        )
        row = await coa_repository.create_nominal(
            company_id=company_id,
            section_id=body.section_id,
            code=code,
            name=body.name,
            description=body.description,
            is_charge_deduction=body.is_charge_deduction,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(row)}


@router.patch("/coa/nominals/{nominal_id}")
async def update_coa_nominal(
    company_id: str,
    nominal_id: str,
    body: UpdateNominalRequest,
    coa_repository: Annotated[CoaRepository, Depends(get_coa_repository)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    """Edit nominal name, description, or deduction flag (§9.1.2)."""

    try:
        row = await coa_repository.update_nominal(
            company_id=company_id,
            nominal_id=nominal_id,
            name=body.name,
            description=body.description,
            is_charge_deduction=body.is_charge_deduction,
        )
    except ValueError as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(row)}


@router.put("/coa/nominals/{nominal_id}/section")
async def move_coa_nominal(
    company_id: str,
    nominal_id: str,
    body: MoveNominalRequest,
    coa_repository: Annotated[CoaRepository, Depends(get_coa_repository)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    """Move a nominal to another section (§9.1.2)."""

    try:
        row = await coa_repository.move_nominal(
            company_id=company_id,
            nominal_id=nominal_id,
            section_id=body.section_id,
        )
    except ValueError as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(row)}


@router.delete("/coa/nominals/{nominal_id}", status_code=204)
async def delete_coa_nominal(
    company_id: str,
    nominal_id: str,
    coa_repository: Annotated[CoaRepository, Depends(get_coa_repository)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> None:
    """Delete an unused nominal (no journal lines) — FA §9.1.2."""

    from fastapi import HTTPException

    try:
        await coa_repository.delete_nominal(company_id=company_id, nominal_id=nominal_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/coa/nominals/bulk-delete")
async def bulk_delete_coa_nominals(
    company_id: str,
    body: dict[str, Any],
    coa_repository: Annotated[CoaRepository, Depends(get_coa_repository)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    """Bulk delete nominals with no journal usage."""

    ids = body.get("nominalIds") or body.get("ids") or []
    if not isinstance(ids, list):
        raise ValidationAppError("nominalIds must be a list")
    result = await coa_repository.bulk_delete_nominals(
        company_id=company_id,
        nominal_ids=[str(i) for i in ids],
    )
    return {"result": result}


@router.get("/smart-settings")
async def get_smart_settings(
    company_id: str,
    repo: Annotated[SmartSettingsRepository, Depends(get_smart_settings_repository)],
) -> dict:
    """Smart Settings JSON document."""

    row = await repo.get_for_company(company_id=company_id)
    payload = row.payload if row else {}
    return {"result": {"payload": payload}}


@router.get("/settings/invite-email-template")
async def get_invite_email_template(
    company_id: str,
    template_service: Annotated[
        InviteEmailTemplateService, Depends(get_invite_email_template_service)
    ],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    """Invite + welcome email copy and placeholders — P30."""

    invite = await template_service.get_invite_template(company_id=company_id)
    welcome = await template_service.get_welcome_template(company_id=company_id)
    return {
        "result": {
            "invite": invite,
            "welcome": welcome,
            "placeholders": {
                "invite": ["companyName", "resetLink", "code", "ttlMinutes"],
                "welcome": ["companyName", "loginUrl"],
            },
            "defaults": {
                "invite": DEFAULT_INVITE_EMAIL_TEMPLATE,
                "welcome": DEFAULT_WELCOME_EMAIL_TEMPLATE,
            },
        }
    }


@router.post("/settings/invite-email-template/preview")
async def preview_invite_email_template(
    company_id: str,
    body: InviteEmailPreviewRequest,
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    """Render invite/welcome copy with sample placeholders — P39."""

    overrides = body.as_dict()
    if body.kind == "invite":
        defaults = DEFAULT_INVITE_EMAIL_TEMPLATE
        sample = {
            "companyName": "Sample Company Ltd",
            "resetLink": "https://app.example.com/set-password?token=sample",
            "code": "123456",
            "ttlMinutes": "15",
        }
    else:
        defaults = DEFAULT_WELCOME_EMAIL_TEMPLATE
        sample = {
            "companyName": "Sample Company Ltd",
            "loginUrl": "https://app.example.com/login",
        }
    merged = {**defaults, **overrides}
    preview = apply_placeholders(merged, **sample)
    return {"result": {"preview": preview, "sampleValues": sample}}


@router.put("/settings/invite-email-template")
async def put_invite_email_template(
    company_id: str,
    body: InviteEmailTemplateRequest,
    template_service: Annotated[
        InviteEmailTemplateService, Depends(get_invite_email_template_service)
    ],
    _claims: Annotated[JwtClaims, Depends(require_permission("settings.users.invite"))],
) -> dict:
    """Update invite email template in Smart Settings — P30."""

    merged = await template_service.save_invite_template(
        company_id=company_id,
        template=body.as_dict(),
    )
    return {"result": {"invite": merged}}


@router.put("/settings/welcome-email-template")
async def put_welcome_email_template(
    company_id: str,
    body: InviteEmailTemplateRequest,
    template_service: Annotated[
        InviteEmailTemplateService, Depends(get_invite_email_template_service)
    ],
    _claims: Annotated[JwtClaims, Depends(require_permission("settings.users.invite"))],
) -> dict:
    """Update welcome email template in Smart Settings — P31."""

    merged = await template_service.save_welcome_template(
        company_id=company_id,
        template=body.as_dict(),
    )
    return {"result": {"welcome": merged}}


@router.put("/smart-settings")
async def put_smart_settings(
    company_id: str,
    body: dict,
    repo: Annotated[SmartSettingsRepository, Depends(get_smart_settings_repository)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    """Replace Smart Settings payload."""

    payload = body.get("payload") if isinstance(body.get("payload"), dict) else body
    row = await repo.upsert_payload(company_id=company_id, payload=payload)
    return {"result": {"payload": row.payload}}


@router.get("/settings/report-favorites")
async def get_report_favorites(
    company_id: str,
    repo: Annotated[SmartSettingsRepository, Depends(get_smart_settings_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    """Starred report hrefs persisted in Smart Settings — FA §10 favorites sync."""

    row = await repo.get_for_company(company_id=company_id)
    payload = row.payload if row and isinstance(row.payload, dict) else {}
    raw = payload.get("reportFavorites")
    hrefs = [str(h) for h in raw] if isinstance(raw, list) else []
    return {"result": {"hrefs": hrefs}}


@router.put("/settings/report-favorites")
async def put_report_favorites(
    company_id: str,
    body: dict,
    repo: Annotated[SmartSettingsRepository, Depends(get_smart_settings_repository)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    """Replace starred report hrefs (company-scoped)."""

    raw = body.get("hrefs")
    if not isinstance(raw, list):
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="hrefs must be a list")
    hrefs = [str(h).strip() for h in raw if str(h).strip()]
    row = await repo.merge_payload(company_id=company_id, patch={"reportFavorites": hrefs})
    stored = row.payload if isinstance(row.payload, dict) else {}
    out = stored.get("reportFavorites")
    return {"result": {"hrefs": out if isinstance(out, list) else hrefs}}


# =================== Settings — print, content, filters (catalog §12) ===================


def _settings_not_found(exc: NotFoundError) -> HTTPException:
    from fastapi import HTTPException

    return HTTPException(status_code=404, detail=str(exc))


@router.get("/print-templates")
async def list_print_templates(
    company_id: str,
    service: Annotated[AppSettingsService, Depends(get_app_settings_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    return {"result": service.list_print_templates()}


@router.get("/print-templates/{code}")
async def get_print_template(
    company_id: str,
    code: str,
    service: Annotated[AppSettingsService, Depends(get_app_settings_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    try:
        return {"result": await service.get_print_template(company_id=company_id, code=code)}
    except NotFoundError as exc:
        raise _settings_not_found(exc) from exc


@router.put("/print-templates/{code}")
async def put_print_template(
    company_id: str,
    code: str,
    body: dict,
    service: Annotated[AppSettingsService, Depends(get_app_settings_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    try:
        return {"result": await service.put_print_template(company_id=company_id, code=code, body=body)}
    except NotFoundError as exc:
        raise _settings_not_found(exc) from exc


@router.get("/content-settings/listings")
async def list_content_listings(
    company_id: str,
    service: Annotated[AppSettingsService, Depends(get_app_settings_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    return {"result": service.list_listings()}


@router.get("/content-settings/listings/{listing_id}")
async def get_content_listing(
    company_id: str,
    listing_id: str,
    service: Annotated[AppSettingsService, Depends(get_app_settings_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    try:
        return {"result": await service.get_listing_layout(company_id=company_id, listing_id=listing_id)}
    except NotFoundError as exc:
        raise _settings_not_found(exc) from exc


@router.put("/content-settings/listings/{listing_id}")
async def put_content_listing(
    company_id: str,
    listing_id: str,
    body: dict,
    service: Annotated[AppSettingsService, Depends(get_app_settings_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    try:
        row = await service.put_listing_layout(
            company_id=company_id, listing_id=listing_id, body=body
        )
        return {"result": row}
    except NotFoundError as exc:
        raise _settings_not_found(exc) from exc
    except ValidationAppError as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/content-settings/forms")
async def list_content_forms(
    company_id: str,
    service: Annotated[AppSettingsService, Depends(get_app_settings_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    return {"result": service.list_forms()}


@router.get("/content-settings/forms/{form_id}")
async def get_content_form(
    company_id: str,
    form_id: str,
    service: Annotated[AppSettingsService, Depends(get_app_settings_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    try:
        return {"result": await service.get_form_layout(company_id=company_id, form_id=form_id)}
    except NotFoundError as exc:
        raise _settings_not_found(exc) from exc


@router.put("/content-settings/forms/{form_id}")
async def put_content_form(
    company_id: str,
    form_id: str,
    body: dict,
    service: Annotated[AppSettingsService, Depends(get_app_settings_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    try:
        row = await service.put_form_layout(company_id=company_id, form_id=form_id, body=body)
        return {"result": row}
    except NotFoundError as exc:
        raise _settings_not_found(exc) from exc
    except ValidationAppError as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/content-settings/menu", response_model=None)
async def get_content_menu(
    company_id: str,
    service: Annotated[AppSettingsService, Depends(get_app_settings_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
    if_none_match: str | None = Header(default=None, alias="If-None-Match"),
) -> Response | dict:
    revision = await service.menu_revision_token(company_id=company_id)
    etag = AppSettingsService.menu_etag(revision)
    cache_headers = {"ETag": f'"{etag}"', "Cache-Control": REFERENCE_CACHE_CONTROL}
    if if_none_match and if_none_match.strip('"') == etag:
        return Response(status_code=304, headers=cache_headers)
    result = await service.get_menu_layout(company_id=company_id)
    return JSONResponse(content={"result": result}, headers=cache_headers)


@router.put("/content-settings/menu")
async def put_content_menu(
    company_id: str,
    body: dict,
    service: Annotated[AppSettingsService, Depends(get_app_settings_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    try:
        row = await service.put_menu_layout(company_id=company_id, body=body)
        return {"result": row}
    except ValidationAppError as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/application-settings/filters")
async def get_filters_settings(
    company_id: str,
    service: Annotated[AppSettingsService, Depends(get_app_settings_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    return {"result": await service.get_filters_settings(company_id=company_id)}


@router.put("/application-settings/filters")
async def put_filters_settings(
    company_id: str,
    body: dict,
    service: Annotated[AppSettingsService, Depends(get_app_settings_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    return {"result": await service.put_filters_settings(company_id=company_id, body=body)}


@router.get("/application-settings/columns")
async def get_columns_settings(
    company_id: str,
    service: Annotated[AppSettingsService, Depends(get_app_settings_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    return {"result": await service.get_columns_settings(company_id=company_id)}


@router.put("/application-settings/columns")
async def put_columns_settings(
    company_id: str,
    body: dict,
    service: Annotated[AppSettingsService, Depends(get_app_settings_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    return {"result": await service.put_columns_settings(company_id=company_id, body=body)}


@router.get("/application-settings/email")
async def get_email_settings(
    company_id: str,
    service: Annotated[AppSettingsService, Depends(get_app_settings_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    return {"result": await service.get_email_settings(company_id=company_id)}


@router.put("/application-settings/email")
async def put_email_settings(
    company_id: str,
    body: dict,
    service: Annotated[AppSettingsService, Depends(get_app_settings_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    return {"result": await service.put_email_settings(company_id=company_id, body=body)}


@router.get("/application-settings/dashboards")
async def get_dashboard_settings(
    company_id: str,
    service: Annotated[AppSettingsService, Depends(get_app_settings_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    return {"result": await service.get_dashboard_settings(company_id=company_id)}


@router.put("/application-settings/dashboards")
async def put_dashboard_settings(
    company_id: str,
    body: dict,
    service: Annotated[AppSettingsService, Depends(get_app_settings_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    return {"result": await service.put_dashboard_settings(company_id=company_id, body=body)}


@router.get("/application-settings/advance-users")
async def get_advance_users_settings(
    company_id: str,
    service: Annotated[AppSettingsService, Depends(get_app_settings_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    """Per-user data visibility fences — FA §12.5."""

    return {"result": await service.get_advance_users_settings(company_id=company_id)}


@router.put("/application-settings/advance-users")
async def put_advance_users_settings(
    company_id: str,
    body: dict,
    service: Annotated[AppSettingsService, Depends(get_app_settings_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    return {"result": await service.put_advance_users_settings(company_id=company_id, body=body)}


@router.get("/application-settings/op-methods")
async def get_op_methods_settings(
    company_id: str,
    service: Annotated[AppSettingsService, Depends(get_app_settings_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    return {"result": await service.get_op_methods_settings(company_id=company_id)}


@router.put("/application-settings/op-methods")
async def put_op_methods_settings(
    company_id: str,
    body: dict,
    service: Annotated[AppSettingsService, Depends(get_app_settings_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    return {"result": await service.put_op_methods_settings(company_id=company_id, body=body)}


@router.get("/application-settings/missed-recurrence")
async def get_missed_recurrence_settings(
    company_id: str,
    service: Annotated[AppSettingsService, Depends(get_app_settings_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    return {"result": await service.get_missed_recurrence_settings(company_id=company_id)}


@router.put("/application-settings/missed-recurrence")
async def put_missed_recurrence_settings(
    company_id: str,
    body: dict,
    service: Annotated[AppSettingsService, Depends(get_app_settings_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    return {"result": await service.put_missed_recurrence_settings(company_id=company_id, body=body)}


@router.get("/sent-emails")
async def list_sent_emails(
    company_id: str,
    service: Annotated[AppSettingsService, Depends(get_app_settings_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    """Outbound email log (tenant-scoped)."""

    return {"result": await service.list_sent_emails(company_id=company_id)}


# =================== P11 — Module entitlements, custom fields, UOM ===================


@router.get("/module-entitlements")
async def list_module_entitlements(
    company_id: str,
    service: Annotated[ModuleEntitlementService, Depends(get_module_entitlement_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    rows = await service.list_entitlements(company_id=company_id)
    return {"result": rows}


@router.put("/module-entitlements")
async def replace_module_entitlements(
    company_id: str,
    body: ModuleEntitlementsReplaceRequest,
    service: Annotated[ModuleEntitlementService, Depends(get_module_entitlement_service)],
    _claims: Annotated[JwtClaims, Depends(require_permission("settings.platform.process"))],
) -> dict:
    payload = [
        {"moduleCode": e.module_code, "enabled": e.enabled}
        for e in body.entitlements
    ]
    rows = await service.replace_entitlements(
        company_id=company_id, entitlements=payload
    )
    return {"result": rows}


@router.get("/custom-field-definitions")
async def list_custom_field_definitions(
    company_id: str,
    service: Annotated[CustomFieldService, Depends(get_custom_field_service)],
    entity_type: str | None = Query(default=None, alias="entityType"),
) -> dict:
    rows = await service.list_definitions(
        company_id=company_id, entity_type=entity_type
    )
    return {"result": rows}


@router.post("/custom-field-definitions", status_code=201)
async def create_custom_field_definition(
    company_id: str,
    body: CustomFieldDefinitionCreateRequest,
    service: Annotated[CustomFieldService, Depends(get_custom_field_service)],
    _claims: Annotated[JwtClaims, Depends(resolve_tenant)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    row = await service.create_definition(
        company_id=company_id,
        entity_type=body.entity_type,
        field_key=body.field_key,
        label=body.label,
        field_type=body.field_type,
        is_required=body.is_required,
        picklist_options=body.picklist_options,
    )
    return {"result": row}


@router.get("/module-access-matrix")
async def module_access_matrix(
    company_id: str,
    claims: Annotated[JwtClaims, Depends(resolve_tenant)],
    access: Annotated[ModuleAccessService, Depends(get_module_access_service)],
) -> dict:
    rows = await access.matrix_for_user(
        company_id=company_id, user_id=claims.user_id
    )
    return {"result": rows}


@router.get("/billing/status")
async def billing_status(
    company_id: str,
    billing: Annotated[SubscriptionBillingService, Depends(get_subscription_billing_service)],
    _claims: Annotated[JwtClaims, Depends(resolve_tenant)],
) -> dict:
    return {"result": await billing.get_status(company_id=company_id)}


@router.post("/billing/checkout-session")
async def billing_checkout_session(
    company_id: str,
    body: CheckoutSessionRequest,
    billing: Annotated[SubscriptionBillingService, Depends(get_subscription_billing_service)],
    _claims: Annotated[JwtClaims, Depends(resolve_tenant)],
) -> dict:
    from fastapi import HTTPException

    try:
        result = await billing.create_checkout_session(
            company_id=company_id,
            plan_code=body.plan_code,
            success_url=body.success_url,
            cancel_url=body.cancel_url,
        )
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"result": result}


@router.post("/billing/portal-session")
async def billing_portal_session(
    company_id: str,
    body: PortalSessionRequest,
    billing: Annotated[SubscriptionBillingService, Depends(get_subscription_billing_service)],
    _claims: Annotated[JwtClaims, Depends(resolve_tenant)],
) -> dict:
    from fastapi import HTTPException

    try:
        result = await billing.create_portal_session(
            company_id=company_id,
            return_url=body.return_url,
        )
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"result": result}


@router.post("/billing/webhook")
async def billing_webhook(
    company_id: str,
    body: BillingWebhookRequest,
    billing: Annotated[SubscriptionBillingService, Depends(get_subscription_billing_service)],
    x_billing_secret: Annotated[str | None, Header(alias="X-Billing-Secret")] = None,
) -> dict:
    from app.core.config import get_settings
    from fastapi import HTTPException

    secret = (get_settings().billing_webhook_secret or "").strip()
    if secret and x_billing_secret != secret:
        raise HTTPException(status_code=401, detail="Invalid billing webhook secret")
    if body.company_id != company_id:
        raise HTTPException(status_code=400, detail="companyId mismatch")
    result = await billing.apply_webhook_event(
        company_id=company_id,
        event_type=body.event_type,
        plan_code=body.plan_code,
        external_customer_id=body.external_customer_id,
    )
    return {"result": result}


@router.post("/billing/webhook/stripe")
async def billing_webhook_stripe(
    company_id: str,
    request: Request,
    billing: Annotated[SubscriptionBillingService, Depends(get_subscription_billing_service)],
    stripe_signature: Annotated[str | None, Header(alias="Stripe-Signature")] = None,
) -> dict:
    import json

    from app.core.config import get_settings
    from app.core.stripe_webhook import (
        StripeWebhookError,
        parse_stripe_webhook_event,
        verify_stripe_signature,
    )
    from fastapi import HTTPException

    raw = await request.body()
    secret = (get_settings().stripe_webhook_secret or "").strip()
    try:
        verify_stripe_signature(
            payload=raw,
            signature_header=stripe_signature or "",
            secret=secret,
        )
    except StripeWebhookError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    body = json.loads(raw.decode("utf-8"))
    parsed = parse_stripe_webhook_event(body)
    meta = {"stripeEventId": body.get("id"), "stripeType": parsed.get("rawType")}
    if parsed.get("companyId") and str(parsed["companyId"]) != company_id:
        raise HTTPException(status_code=400, detail="companyId metadata mismatch")
    if parsed.get("kind") == "invoice_failed" and parsed.get("externalCustomerId"):
        looked_up = await billing.resolve_company_by_stripe_customer(
            external_customer_id=str(parsed["externalCustomerId"])
        )
        if looked_up and looked_up != company_id:
            raise HTTPException(status_code=400, detail="Stripe customer company mismatch")

    if parsed.get("kind") == "checkout":
        result = await billing.apply_checkout_completed(
            company_id=company_id,
            plan_code=parsed.get("planCode"),
            external_customer_id=parsed.get("externalCustomerId"),
            subscription_id=parsed.get("subscriptionId"),
            metadata=meta,
        )
    elif parsed.get("kind") == "invoice_failed":
        result = await billing.apply_stripe_event(
            company_id=company_id,
            event_type="invoice.payment_failed",
            external_customer_id=parsed.get("externalCustomerId"),
            metadata=meta,
        )
    else:
        result = await billing.apply_stripe_event(
            company_id=company_id,
            event_type=str(parsed.get("eventType") or "unknown"),
            plan_code=parsed.get("planCode"),
            external_customer_id=parsed.get("externalCustomerId"),
            period_end_unix=parsed.get("periodEndUnix"),
            metadata=meta,
        )
    return {"result": result}


@router.patch("/customers/{customer_id}/custom-fields")
async def patch_customer_custom_fields(
    company_id: str,
    customer_id: str,
    body: CustomFieldsPatchRequest,
    service: Annotated[CustomFieldService, Depends(get_custom_field_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("sales"))],
) -> dict:
    row = await service.patch_customer_fields(
        company_id=company_id,
        customer_id=customer_id,
        custom_fields=body.custom_fields,
    )
    return {"result": row}


@router.patch("/products/{product_id}/custom-fields")
async def patch_product_custom_fields(
    company_id: str,
    product_id: str,
    body: CustomFieldsPatchRequest,
    service: Annotated[CustomFieldService, Depends(get_custom_field_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("inventory"))],
) -> dict:
    row = await service.patch_product_fields(
        company_id=company_id,
        product_id=product_id,
        custom_fields=body.custom_fields,
    )
    return {"result": row}


@router.get("/products/{product_id}/uoms")
async def list_product_uoms(
    company_id: str,
    product_id: str,
    service: Annotated[ProductUomService, Depends(get_product_uom_service)],
) -> dict:
    rows = await service.list_uoms(company_id=company_id, product_id=product_id)
    return {"result": rows}


@router.post("/products/{product_id}/uoms", status_code=201)
async def upsert_product_uom(
    company_id: str,
    product_id: str,
    body: ProductUomUpsertRequest,
    service: Annotated[ProductUomService, Depends(get_product_uom_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("inventory"))],
) -> dict:
    row = await service.upsert_uom(
        company_id=company_id,
        product_id=product_id,
        unit_code=body.unit_code,
        conversion_factor=body.conversion_factor,
        sale_price=body.sale_price,
        is_default=body.is_default,
    )
    return {"result": row}


@router.get("/taxes-year-end")
async def get_taxes_year_end(
    company_id: str,
    repo: Annotated[TaxesConfigRepository, Depends(get_taxes_config_repository)],
) -> dict:
    """Taxes and year-end configuration."""

    row = await repo.get_for_company(company_id=company_id)
    if row is None:
        return {"result": None}
    return {"result": jsonable_encoder(row)}


@router.put("/taxes-year-end")
async def put_taxes_year_end(
    company_id: str,
    body: dict,
    repo: Annotated[TaxesConfigRepository, Depends(get_taxes_config_repository)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    """Replace tax configuration (pass-through JSON for now)."""

    row = await repo.upsert_full(
        company_id=company_id,
        year_end_date=_parse_datetime(body.get("yearEndDate")),
        tax_display=body.get("taxDisplay") or {},
        gst_rates=body.get("gstRates") or [],
        fed_rates=body.get("fedRates") or [],
        adt_rates=body.get("adtRates") or [],
        wht_rates=body.get("whtRates") or [],
        tax_regions=body.get("taxRegions") or [],
    )
    return {"result": jsonable_encoder(row)}


@router.get("/lock-date")
async def get_lock_date(
    company_id: str,
    repo: Annotated[LockDateRepository, Depends(get_lock_date_repository)],
) -> dict:
    """Global lock date and per-user extensions."""

    row = await repo.get_for_company(company_id=company_id)
    extensions = await repo.list_user_extensions(company_id=company_id)
    if row is None:
        return {"result": {"globalLockDate": None, "perUserExtensions": extensions}}
    payload = jsonable_encoder(row)
    if isinstance(payload, dict):
        payload["perUserExtensions"] = extensions
    return {"result": payload}


@router.put("/lock-date")
async def put_lock_date(
    company_id: str,
    body: dict,
    repo: Annotated[LockDateRepository, Depends(get_lock_date_repository)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    """Update global lock date."""

    row = await repo.upsert_global(
        company_id=company_id,
        global_lock_date=_parse_datetime(body.get("globalLockDate")),
    )
    return {"result": jsonable_encoder(row)}


@router.put("/lock-date/users/{user_id}")
async def put_lock_date_per_user(
    company_id: str,
    user_id: str,
    body: LockDatePerUserRequest,
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    await lock_date_service.set_user_extension(
        company_id=company_id,
        user_id=user_id,
        extended_lock_date=body.extended_lock_date,
    )
    return {"result": {"userId": user_id, "extendedLockDate": body.extended_lock_date.isoformat()}}


@router.get("/business-information")
async def get_business_information(
    company_id: str,
    repo: Annotated[BusinessInformationRepository, Depends(get_business_information_repository)],
) -> dict:
    """Business profile for prints."""

    row = await repo.get_for_company(company_id=company_id)
    if row is None:
        return {"result": None}
    return {"result": jsonable_encoder(row)}


@router.put("/business-information")
async def put_business_information(
    company_id: str,
    body: dict,
    repo: Annotated[BusinessInformationRepository, Depends(get_business_information_repository)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    """Update business profile fields (partial keys)."""

    row = await repo.upsert_fields(company_id=company_id, fields=body)
    return {"result": jsonable_encoder(row)}


@router.get("/bank-accounts")
async def list_bank_accounts(
    company_id: str,
    repo: Annotated[BankRepository, Depends(get_bank_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("bank"))],
) -> dict:
    """Bank and cash accounts."""

    rows = await repo.list_accounts(company_id=company_id)
    return {"result": _dump_rows(rows)}


@router.get("/bank-payments")
async def list_bank_payments(
    company_id: str,
    repo: Annotated[BankRepository, Depends(get_bank_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("bank"))],
) -> dict:
    """Bank payments listing."""

    rows = await repo.list_payments(company_id=company_id)
    return {"result": _dump_rows(rows)}


@router.get("/bank-payments/{payment_id}")
async def get_bank_payment(
    company_id: str,
    payment_id: str,
    repo: Annotated[BankRepository, Depends(get_bank_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("bank"))],
) -> dict:
    """Single bank payment — P42."""

    from fastapi import HTTPException

    row = await repo.get_payment(company_id=company_id, payment_id=payment_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Bank payment not found")
    return {"result": jsonable_encoder(row)}


@router.post("/bank-payments/{payment_id}/post")
async def post_bank_payment_draft(
    company_id: str,
    payment_id: str,
    svc: Annotated[BankPaymentService, Depends(get_bank_payment_service)],
    repo: Annotated[BankRepository, Depends(get_bank_repository)],
    approval_engine: Annotated[ApprovalEngineService, Depends(get_approval_engine_service)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    claims: Annotated[JwtClaims, Depends(require_permission("bank.payments.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("bank"))],
) -> dict:
    """Post a draft bank payment to the GL (Template/Draft workflow)."""

    from app.domain.document_workflow import SOURCE_BANK_PAYMENT
    from fastapi import HTTPException

    existing = await repo.get_payment(company_id=company_id, payment_id=payment_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Bank payment not found")
    try:
        await guard_document_post(
            approval_engine,
            company_id=company_id,
            entity_type="bank_payment",
            entity_id=payment_id,
            amount=existing.totalAmount,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    try:
        row = await svc.post_draft_payment(
            company_id=company_id, payment_id=payment_id
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    await audit_service.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type=SOURCE_BANK_PAYMENT,
        transaction_id=row.id,
        status="posted",
        details=f"voucher={row.voucherNumber} posted from draft",
    )
    return {"result": jsonable_encoder(row), "posted": True}


@router.post("/bank-payments/{payment_id}/copy", status_code=201)
async def copy_bank_payment(
    company_id: str,
    payment_id: str,
    repo: Annotated[BankRepository, Depends(get_bank_repository)],
    svc: Annotated[BankPaymentService, Depends(get_bank_payment_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("bank"))],
) -> dict:
    """Copy a bank payment with the same nominal split (FA §3.9)."""

    from fastapi import HTTPException

    source = await repo.get_payment(company_id=company_id, payment_id=payment_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Bank payment not found")
    row = await svc.create_payment(
        company_id=company_id,
        bank_account_id=source.bankAccountId,
        payment_date=source.paymentDate,
        total_amount=source.totalAmount,
        nominal_code=getattr(source, "nominalCode", None),
    )
    return {"result": jsonable_encoder(row), "copiedFromId": payment_id}


@router.get("/sales-receipts")
async def list_sales_receipts(
    company_id: str,
    repo: Annotated[SalesReceiptRepository, Depends(get_sales_receipt_repository)],
    advance_service: Annotated[AdvanceReturnService, Depends(get_advance_return_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("sales"))],
) -> dict:
    """Customer receipts (§5.8)."""

    rows = await repo.list_receipts(company_id=company_id)
    balances = await advance_service.list_receipt_balances(
        company_id=company_id,
        receipt_ids=[r.id for r in rows],
    )
    result = []
    for row in rows:
        encoded = jsonable_encoder(row)
        if isinstance(encoded, dict):
            encoded["unallocatedBalance"] = str(balances.get(row.id, row.totalAmount))
        result.append(encoded)
    return {"result": result}


@router.get("/sales-receipts/{receipt_id}")
async def get_sales_receipt(
    company_id: str,
    receipt_id: str,
    repo: Annotated[SalesReceiptRepository, Depends(get_sales_receipt_repository)],
    advance_service: Annotated[AdvanceReturnService, Depends(get_advance_return_service)],
) -> dict:
    from fastapi import HTTPException

    row = await repo.get_receipt(company_id=company_id, receipt_id=receipt_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Receipt not found")
    allocations = await repo.list_allocations(receipt_id=receipt_id)
    try:
        balances = await advance_service.receipt_balance(
            company_id=company_id, receipt_id=receipt_id
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    returns = await advance_service.list_customer_returns(receipt_id=receipt_id)
    return {
        "result": jsonable_encoder(row),
        "allocations": allocations,
        "balance": {k: str(v) for k, v in balances.items()},
        "advanceReturns": jsonable_encoder(returns),
    }


@router.post("/sales-receipts/{receipt_id}/post")
async def post_sales_receipt_draft(
    company_id: str,
    receipt_id: str,
    repo: Annotated[SalesReceiptRepository, Depends(get_sales_receipt_repository)],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    posting_service: Annotated[PostingService, Depends(get_posting_service)],
    tax_service: Annotated[TaxCalculationService, Depends(get_tax_calculation_service)],
    approval_engine: Annotated[ApprovalEngineService, Depends(get_approval_engine_service)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    claims: Annotated[JwtClaims, Depends(require_permission("sales.receipts.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("sales"))],
) -> dict:
    """Post a draft customer receipt to the GL (import / template workflow)."""

    from app.domain.document_workflow import SOURCE_SALES_RECEIPT
    from fastapi import HTTPException

    row = await repo.get_receipt(company_id=company_id, receipt_id=receipt_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Sales receipt not found")
    if row.journalId:
        raise HTTPException(status_code=400, detail="Receipt is already posted")
    if row.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft receipts can be posted")
    try:
        await guard_document_post(
            approval_engine,
            company_id=company_id,
            entity_type="sales_receipt",
            entity_id=receipt_id,
            amount=row.totalAmount,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    await lock_date_service.assert_not_locked(
        company_id=company_id,
        document_date=row.receiptDate,
        document_label="sales receipt",
    )
    fields = row.customFields if isinstance(row.customFields, dict) else {}
    wht_code = fields.get("whtCode") or fields.get("wht_code")
    wht_amount_raw = fields.get("whtAmount") or fields.get("wht_amount")
    wht_amount = Decimal(str(wht_amount_raw)) if wht_amount_raw else None
    wht_nominal = None
    if wht_code and wht_amount and wht_amount > 0:
        wht_nominal = await tax_service.wht_nominal_for_code(
            company_id=company_id, wht_code=str(wht_code)
        )
    journal = await posting_service.post_sales_receipt(
        company_id=company_id,
        receipt_date=row.receiptDate,
        receipt_number=row.receiptNumber,
        bank_account_id=row.bankAccountId,
        total_amount=row.totalAmount,
        wht_amount=wht_amount,
        wht_nominal_code=wht_nominal,
    )
    if journal is None:
        raise HTTPException(
            status_code=400,
            detail="Could not post: configure receivables nominal and bank account nominal.",
        )
    updated = await repo.link_receipt_journal(
        receipt_id=receipt_id, journal_id=journal.id
    )
    await audit_service.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type=SOURCE_SALES_RECEIPT,
        transaction_id=updated.id,
        status="posted",
        details=f"receipt={row.receiptNumber} posted from draft",
    )
    return {"result": jsonable_encoder(updated), "posted": True}


@router.post("/sales-receipts/{receipt_id}/allocate")
async def allocate_sales_receipt(
    company_id: str,
    receipt_id: str,
    body: ReceiptAllocateRequest,
    repo: Annotated[SalesReceiptRepository, Depends(get_sales_receipt_repository)],
    allocation_service: Annotated[AllocationService, Depends(get_allocation_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("sales"))],
) -> dict:
    from fastapi import HTTPException

    from app.services.allocation_service import AllocationLine

    row = await repo.get_receipt(company_id=company_id, receipt_id=receipt_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Receipt not found")
    explicit = None
    if body.allocations:
        explicit = [
            AllocationLine(document_id=line.invoice_id, amount=line.amount)
            for line in body.allocations
        ]
    try:
        result = await allocation_service.allocate_sales_receipt(
            company_id=company_id,
            receipt_id=receipt_id,
            customer_id=row.customerId,
            receipt_total=row.totalAmount,
            auto_fifo=body.auto_fifo and not explicit,
            explicit=explicit,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "allocations": [
            {"id": a.id, "salesInvoiceId": a.salesInvoiceId, "amount": str(a.amount)}
            for a in result.allocations
        ],
        "totalAllocated": str(result.total_allocated),
        "unallocatedBalance": str(result.unallocated_balance),
    }


@router.post("/sales-receipts/{receipt_id}/return-advance", status_code=201)
async def return_customer_advance(
    company_id: str,
    receipt_id: str,
    body: AdvanceReturnRequest,
    advance_service: Annotated[AdvanceReturnService, Depends(get_advance_return_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("sales"))],
) -> dict:
    """Return unallocated customer advance via bank payment — FA §5.8."""

    from fastapi import HTTPException

    try:
        result = await advance_service.return_customer_advance(
            company_id=company_id,
            receipt_id=receipt_id,
            return_date=body.return_date,
            amount=body.amount,
            bank_account_id=body.bank_account_id,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "result": jsonable_encoder(result["advanceReturn"]),
        "bankPayment": jsonable_encoder(result["bankPayment"]),
        "posted": result["posted"],
    }


@router.post("/sales-receipts", status_code=201)
async def create_sales_receipt(
    company_id: str,
    body: SalesReceiptCreateRequest,
    repo: Annotated[SalesReceiptRepository, Depends(get_sales_receipt_repository)],
    document_number_service: Annotated[
        DocumentNumberService, Depends(get_document_number_service)
    ],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    posting_service: Annotated[PostingService, Depends(get_posting_service)],
    tax_service: Annotated[TaxCalculationService, Depends(get_tax_calculation_service)],
    allocation_service: Annotated[AllocationService, Depends(get_allocation_service)],
    approval_engine: Annotated[ApprovalEngineService, Depends(get_approval_engine_service)],
    smart_runtime: Annotated[SmartSettingsRuntime, Depends(get_smart_settings_runtime)],
    _claims: Annotated[Any, Depends(require_permission("sales.receipts.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("sales"))],
) -> dict:
    """Create a customer receipt; GL-post against AR; optionally allocate to invoices."""

    from fastapi import HTTPException

    await lock_date_service.assert_not_locked(
        company_id=company_id,
        document_date=body.receipt_date,
        document_label="sales receipt",
    )
    receipt_number = str(
        await document_number_service.reserve_next(company_id=company_id, sequence_key="SR")
    )
    from app.utils.document_custom_fields import document_custom_fields

    receipt_id = str(uuid4())
    try:
        await guard_document_post(
            approval_engine,
            company_id=company_id,
            entity_type="sales_receipt",
            entity_id=receipt_id,
            amount=body.total_amount,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    post_gl = await smart_runtime.post_gl_on_create(
        company_id=company_id, module_key="saleReceipts"
    )
    wht_nominal = None
    if body.wht_code and body.wht_amount and body.wht_amount > 0:
        wht_nominal = await tax_service.wht_nominal_for_code(
            company_id=company_id, wht_code=body.wht_code
        )
    journal = None
    if post_gl:
        journal = await posting_service.post_sales_receipt(
            company_id=company_id,
            receipt_date=body.receipt_date,
            receipt_number=receipt_number,
            bank_account_id=body.bank_account_id,
            total_amount=body.total_amount,
            wht_amount=body.wht_amount,
            wht_nominal_code=wht_nominal,
        )
    doc_status = "posted" if journal else "draft"
    row = await repo.create_receipt(
        company_id=company_id,
        receipt_number=receipt_number,
        receipt_date=body.receipt_date,
        customer_id=body.customer_id,
        bank_account_id=body.bank_account_id,
        total_amount=body.total_amount,
        journal_id=journal.id if journal else None,
        custom_fields=document_custom_fields(
            smart_filters=body.smart_filters,
            payment_method=body.payment_method,
        ),
        receipt_id=receipt_id,
        status=doc_status,
    )

    explicit_lines = (
        [
            AllocationLine(document_id=line.invoice_id, amount=line.amount)
            for line in body.allocations
        ]
        if body.allocations
        else None
    )
    alloc = await allocation_service.allocate_sales_receipt(
        company_id=company_id,
        receipt_id=row.id,
        customer_id=body.customer_id,
        receipt_total=body.total_amount,
        auto_fifo=body.auto_fifo,
        explicit=explicit_lines,
    )

    return {
        "result": jsonable_encoder(row),
        "posted": journal is not None,
        "postingWarning": None
        if journal
        else (
            "Saved as draft (Template/Draft setting). Post when ready."
            if not post_gl
            else "Set the receivables nominal in Smart Settings → Defaults and a nominal on the bank account to enable GL posting."
        ),
        "allocations": alloc.allocations,
        "totalAllocated": str(alloc.total_allocated),
        "unallocatedBalance": str(alloc.unallocated_balance),
    }


@router.get("/supplier-payments")
async def list_supplier_payments(
    company_id: str,
    repo: Annotated[SupplierPaymentRepository, Depends(get_supplier_payment_repository)],
    advance_service: Annotated[AdvanceReturnService, Depends(get_advance_return_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("purchases"))],
) -> dict:
    """Supplier payments (§6.4)."""

    rows = await repo.list_payments(company_id=company_id)
    balances = await advance_service.list_payment_balances(
        company_id=company_id,
        payment_ids=[r.id for r in rows],
    )
    result = []
    for row in rows:
        encoded = jsonable_encoder(row)
        if isinstance(encoded, dict):
            encoded["unallocatedBalance"] = str(balances.get(row.id, row.totalAmount))
        result.append(encoded)
    return {"result": result}


@router.get("/supplier-payments/{payment_id}")
async def get_supplier_payment(
    company_id: str,
    payment_id: str,
    repo: Annotated[SupplierPaymentRepository, Depends(get_supplier_payment_repository)],
    advance_service: Annotated[AdvanceReturnService, Depends(get_advance_return_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("purchases"))],
) -> dict:
    from fastapi import HTTPException

    row = await repo.get_payment(company_id=company_id, payment_id=payment_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Supplier payment not found")
    allocations = await repo.list_allocations(payment_id=payment_id)
    try:
        balances = await advance_service.payment_balance(
            company_id=company_id, payment_id=payment_id
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    returns = await advance_service.list_supplier_returns(payment_id=payment_id)
    return {
        "result": jsonable_encoder(row),
        "allocations": allocations,
        "balance": {k: str(v) for k, v in balances.items()},
        "advanceReturns": jsonable_encoder(returns),
    }


@router.post("/supplier-payments/{payment_id}/post")
async def post_supplier_payment_draft(
    company_id: str,
    payment_id: str,
    repo: Annotated[SupplierPaymentRepository, Depends(get_supplier_payment_repository)],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    posting_service: Annotated[PostingService, Depends(get_posting_service)],
    tax_service: Annotated[TaxCalculationService, Depends(get_tax_calculation_service)],
    approval_engine: Annotated[ApprovalEngineService, Depends(get_approval_engine_service)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    claims: Annotated[JwtClaims, Depends(require_permission("purchases.payments.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("purchases"))],
) -> dict:
    """Post a draft supplier payment to the GL (import / template workflow)."""

    from app.domain.document_workflow import SOURCE_SUPPLIER_PAYMENT
    from fastapi import HTTPException

    row = await repo.get_payment(company_id=company_id, payment_id=payment_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Supplier payment not found")
    if row.journalId:
        raise HTTPException(status_code=400, detail="Payment is already posted")
    if row.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft payments can be posted")
    try:
        await guard_document_post(
            approval_engine,
            company_id=company_id,
            entity_type="supplier_payment",
            entity_id=payment_id,
            amount=row.totalAmount,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    await lock_date_service.assert_not_locked(
        company_id=company_id,
        document_date=row.paymentDate,
        document_label="supplier payment",
    )
    fields = row.customFields if isinstance(row.customFields, dict) else {}
    wht_code = fields.get("whtCode") or fields.get("wht_code")
    wht_amount_raw = fields.get("whtAmount") or fields.get("wht_amount")
    wht_amount = Decimal(str(wht_amount_raw)) if wht_amount_raw else None
    wht_nominal = None
    if wht_code and wht_amount and wht_amount > 0:
        wht_nominal = await tax_service.wht_nominal_for_code(
            company_id=company_id, wht_code=str(wht_code)
        )
    journal = await posting_service.post_supplier_payment(
        company_id=company_id,
        payment_date=row.paymentDate,
        voucher_number=row.voucherNumber,
        bank_account_id=row.bankAccountId,
        total_amount=row.totalAmount,
        wht_amount=wht_amount,
        wht_nominal_code=wht_nominal,
    )
    if journal is None:
        raise HTTPException(
            status_code=400,
            detail="Could not post: configure payables nominal and bank account nominal.",
        )
    updated = await repo.link_payment_journal(
        payment_id=payment_id, journal_id=journal.id
    )
    await audit_service.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type=SOURCE_SUPPLIER_PAYMENT,
        transaction_id=updated.id,
        status="posted",
        details=f"payment={row.voucherNumber} posted from draft",
    )
    return {"result": jsonable_encoder(updated), "posted": True}


@router.post("/supplier-payments/{payment_id}/allocate")
async def allocate_supplier_payment(
    company_id: str,
    payment_id: str,
    body: PaymentAllocateRequest,
    repo: Annotated[SupplierPaymentRepository, Depends(get_supplier_payment_repository)],
    allocation_service: Annotated[AllocationService, Depends(get_allocation_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("purchases"))],
) -> dict:
    from fastapi import HTTPException

    from app.services.allocation_service import AllocationLine

    row = await repo.get_payment(company_id=company_id, payment_id=payment_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Supplier payment not found")
    explicit = None
    if body.allocations:
        explicit = [
            AllocationLine(document_id=line.bill_id, amount=line.amount)
            for line in body.allocations
        ]
    try:
        result = await allocation_service.allocate_supplier_payment(
            company_id=company_id,
            payment_id=payment_id,
            supplier_id=row.supplierId,
            payment_total=row.totalAmount,
            auto_fifo=body.auto_fifo and not explicit,
            explicit=explicit,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "allocations": [
            {
                "id": a["id"],
                "supplierBillId": a["supplierBillId"],
                "amount": a["amount"],
            }
            for a in result.allocations
        ],
        "totalAllocated": str(result.total_allocated),
        "unallocatedBalance": str(result.unallocated_balance),
    }


@router.post("/supplier-payments/{payment_id}/return-advance", status_code=201)
async def return_supplier_advance(
    company_id: str,
    payment_id: str,
    body: AdvanceReturnRequest,
    advance_service: Annotated[AdvanceReturnService, Depends(get_advance_return_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("purchases"))],
) -> dict:
    """Return unallocated supplier advance via bank receipt — FA §6.4."""

    from fastapi import HTTPException

    try:
        result = await advance_service.return_supplier_advance(
            company_id=company_id,
            payment_id=payment_id,
            return_date=body.return_date,
            amount=body.amount,
            bank_account_id=body.bank_account_id,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "result": jsonable_encoder(result["advanceReturn"]),
        "bankReceipt": jsonable_encoder(result["bankReceipt"]),
        "posted": result["posted"],
    }


@router.post("/supplier-payments", status_code=201)
async def create_supplier_payment(
    company_id: str,
    body: SupplierPaymentCreateRequest,
    repo: Annotated[SupplierPaymentRepository, Depends(get_supplier_payment_repository)],
    document_number_service: Annotated[
        DocumentNumberService, Depends(get_document_number_service)
    ],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    posting_service: Annotated[PostingService, Depends(get_posting_service)],
    tax_service: Annotated[TaxCalculationService, Depends(get_tax_calculation_service)],
    allocation_service: Annotated[AllocationService, Depends(get_allocation_service)],
    approval_engine: Annotated[ApprovalEngineService, Depends(get_approval_engine_service)],
    smart_runtime: Annotated[SmartSettingsRuntime, Depends(get_smart_settings_runtime)],
    _claims: Annotated[Any, Depends(require_permission("purchases.payments.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("purchases"))],
) -> dict:
    """Create a supplier payment; GL-post against AP; optionally allocate to bills."""

    from fastapi import HTTPException

    await lock_date_service.assert_not_locked(
        company_id=company_id,
        document_date=body.payment_date,
        document_label="supplier payment",
    )
    voucher_number = str(
        await document_number_service.reserve_next(company_id=company_id, sequence_key="VP")
    )
    from app.utils.document_custom_fields import document_custom_fields

    payment_id = str(uuid4())
    try:
        await guard_document_post(
            approval_engine,
            company_id=company_id,
            entity_type="supplier_payment",
            entity_id=payment_id,
            amount=body.total_amount,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    post_gl = await smart_runtime.post_gl_on_create(
        company_id=company_id, module_key="supplierPayments"
    )
    wht_nominal = None
    if body.wht_code and body.wht_amount and body.wht_amount > 0:
        wht_nominal = await tax_service.wht_nominal_for_code(
            company_id=company_id, wht_code=body.wht_code
        )
    journal = None
    if post_gl:
        journal = await posting_service.post_supplier_payment(
            company_id=company_id,
            payment_date=body.payment_date,
            voucher_number=voucher_number,
            bank_account_id=body.bank_account_id,
            total_amount=body.total_amount,
            wht_amount=body.wht_amount,
            wht_nominal_code=wht_nominal,
        )
    doc_status = "posted" if journal else "draft"
    row = await repo.create_payment(
        company_id=company_id,
        voucher_number=voucher_number,
        payment_date=body.payment_date,
        supplier_id=body.supplier_id,
        bank_account_id=body.bank_account_id,
        total_amount=body.total_amount,
        journal_id=journal.id if journal else None,
        custom_fields=document_custom_fields(
            smart_filters=body.smart_filters,
            payment_method=body.payment_method,
        ),
        payment_id=payment_id,
        status=doc_status,
    )

    explicit_lines = (
        [
            AllocationLine(document_id=line.bill_id, amount=line.amount)
            for line in body.allocations
        ]
        if body.allocations
        else None
    )
    alloc = await allocation_service.allocate_supplier_payment(
        company_id=company_id,
        payment_id=row.id,
        supplier_id=body.supplier_id,
        payment_total=body.total_amount,
        auto_fifo=body.auto_fifo,
        explicit=explicit_lines,
    )

    return {
        "result": jsonable_encoder(row),
        "posted": journal is not None,
        "postingWarning": None
        if journal
        else (
            "Saved as draft (Template/Draft setting). Post when ready."
            if not post_gl
            else "Set the payables nominal in Smart Settings → Defaults and a nominal on the bank account to enable GL posting."
        ),
        "allocations": alloc.allocations,
        "totalAllocated": str(alloc.total_allocated),
        "unallocatedBalance": str(alloc.unallocated_balance),
    }


@router.get("/bank-receipts")
async def list_bank_receipts(
    company_id: str,
    repo: Annotated[BankReceiptRepository, Depends(get_bank_receipt_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("bank"))],
) -> dict:
    """Bank receipts (§4.3)."""

    rows = await repo.list_receipts(company_id=company_id)
    return {"result": _dump_rows(rows)}


@router.get("/bank-receipts/{receipt_id}")
async def get_bank_receipt(
    company_id: str,
    receipt_id: str,
    repo: Annotated[BankReceiptRepository, Depends(get_bank_receipt_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("bank"))],
) -> dict:
    """Single bank receipt — P41."""

    from fastapi import HTTPException

    row = await repo.get_receipt(company_id=company_id, receipt_id=receipt_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Bank receipt not found")
    return {"result": jsonable_encoder(row)}


@router.post("/bank-receipts", status_code=201)
async def create_bank_receipt(
    company_id: str,
    body: BankReceiptCreateRequest,
    repo: Annotated[BankReceiptRepository, Depends(get_bank_receipt_repository)],
    document_number_service: Annotated[
        DocumentNumberService, Depends(get_document_number_service)
    ],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    posting_service: Annotated[PostingService, Depends(get_posting_service)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    approval_engine: Annotated[ApprovalEngineService, Depends(get_approval_engine_service)],
    smart_runtime: Annotated[SmartSettingsRuntime, Depends(get_smart_settings_runtime)],
    _claims: Annotated[Any, Depends(require_permission("bank.payments.create"))],
    claims: Annotated[JwtClaims, Depends(require_module_access("bank"))],
) -> dict:
    """Create a bank receipt with optional counterpart nominal for GL posting."""

    from app.domain.document_workflow import SOURCE_BANK_RECEIPT
    from fastapi import HTTPException

    receipt_id = str(uuid4())
    try:
        await guard_document_post(
            approval_engine,
            company_id=company_id,
            entity_type="bank_receipt",
            entity_id=receipt_id,
            amount=body.total_amount,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    await lock_date_service.assert_not_locked(
        company_id=company_id,
        document_date=body.receipt_date,
        document_label="bank receipt",
    )
    voucher_number = str(
        await document_number_service.reserve_next(company_id=company_id, sequence_key="IR")
    )
    post_gl = await smart_runtime.post_gl_on_create(
        company_id=company_id, module_key="bankReceipt"
    )
    journal = None
    if post_gl:
        journal = await posting_service.post_bank_receipt(
            company_id=company_id,
            receipt_date=body.receipt_date,
            voucher_number=voucher_number,
            bank_account_id=body.bank_account_id,
            counterpart_nominal_code=body.nominal_code,
            total_amount=body.total_amount,
        )
    doc_status = "posted" if journal else "draft"
    row = await repo.create_receipt(
        company_id=company_id,
        voucher_number=voucher_number,
        receipt_date=body.receipt_date,
        bank_account_id=body.bank_account_id,
        total_amount=body.total_amount,
        nominal_code=body.nominal_code,
        journal_id=journal.id if journal else None,
        receipt_id=receipt_id,
        status=doc_status,
    )
    await audit_service.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type=SOURCE_BANK_RECEIPT,
        transaction_id=row.id,
        status="posted" if journal else "ok",
        details=(
            f"voucher={voucher_number} amount={body.total_amount} "
            f"posted={journal is not None}"
        ),
    )
    return {
        "result": jsonable_encoder(row),
        "posted": journal is not None,
        "postingWarning": None
        if journal
        else (
            "Saved as draft (Template/Draft setting). Post when ready."
            if not post_gl
            else "Set a counterpart nominal on the receipt and a nominal on the bank account to enable GL posting."
        ),
    }


@router.post("/bank-receipts/{receipt_id}/post")
async def post_bank_receipt_draft(
    company_id: str,
    receipt_id: str,
    repo: Annotated[BankReceiptRepository, Depends(get_bank_receipt_repository)],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    posting_service: Annotated[PostingService, Depends(get_posting_service)],
    approval_engine: Annotated[ApprovalEngineService, Depends(get_approval_engine_service)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    claims: Annotated[JwtClaims, Depends(require_permission("bank.payments.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("bank"))],
) -> dict:
    """Post a draft bank receipt to the GL."""

    from app.domain.document_workflow import SOURCE_BANK_RECEIPT
    from fastapi import HTTPException

    row = await repo.get_receipt(company_id=company_id, receipt_id=receipt_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Bank receipt not found")
    if row.journalId:
        raise HTTPException(status_code=400, detail="Receipt is already posted")
    if row.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft receipts can be posted")
    try:
        await guard_document_post(
            approval_engine,
            company_id=company_id,
            entity_type="bank_receipt",
            entity_id=receipt_id,
            amount=row.totalAmount,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    await lock_date_service.assert_not_locked(
        company_id=company_id,
        document_date=row.receiptDate,
        document_label="bank receipt",
    )
    journal = await posting_service.post_bank_receipt(
        company_id=company_id,
        receipt_date=row.receiptDate,
        voucher_number=row.voucherNumber,
        bank_account_id=row.bankAccountId,
        counterpart_nominal_code=row.nominalCode,
        total_amount=row.totalAmount,
    )
    if journal is None:
        raise HTTPException(
            status_code=400,
            detail="Could not post: set counterpart nominal and bank account nominal.",
        )
    updated = await repo.link_receipt_journal(
        receipt_id=receipt_id, journal_id=journal.id
    )
    await audit_service.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type=SOURCE_BANK_RECEIPT,
        transaction_id=updated.id,
        status="posted",
        details=f"voucher={row.voucherNumber} posted from draft",
    )
    return {"result": jsonable_encoder(updated), "posted": True}


@router.get("/bank-transfers")
async def list_bank_transfers(
    company_id: str,
    repo: Annotated[BankTransferRepository, Depends(get_bank_transfer_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("bank"))],
) -> dict:
    """Bank transfers (§4.4)."""

    rows = await repo.list_transfers(company_id=company_id)
    return {"result": _dump_rows(rows)}


@router.get("/bank-transfers/{transfer_id}")
async def get_bank_transfer(
    company_id: str,
    transfer_id: str,
    repo: Annotated[BankTransferRepository, Depends(get_bank_transfer_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("bank"))],
) -> dict:
    """Single bank transfer — P43."""

    from fastapi import HTTPException

    row = await repo.get_transfer(company_id=company_id, transfer_id=transfer_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Bank transfer not found")
    return {"result": jsonable_encoder(row)}


@router.post("/bank-transfers", status_code=201)
async def create_bank_transfer(
    company_id: str,
    body: BankTransferCreateRequest,
    repo: Annotated[BankTransferRepository, Depends(get_bank_transfer_repository)],
    document_number_service: Annotated[
        DocumentNumberService, Depends(get_document_number_service)
    ],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    posting_service: Annotated[PostingService, Depends(get_posting_service)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    approval_engine: Annotated[ApprovalEngineService, Depends(get_approval_engine_service)],
    smart_runtime: Annotated[SmartSettingsRuntime, Depends(get_smart_settings_runtime)],
    _claims: Annotated[Any, Depends(require_permission("bank.payments.create"))],
    claims: Annotated[JwtClaims, Depends(require_module_access("bank"))],
) -> dict:
    """Create a bank transfer; posts a journal when both bank accounts have nominals."""

    from app.domain.document_workflow import SOURCE_BANK_TRANSFER
    from fastapi import HTTPException

    transfer_id = str(uuid4())
    try:
        await guard_document_post(
            approval_engine,
            company_id=company_id,
            entity_type="bank_transfer",
            entity_id=transfer_id,
            amount=body.total_amount,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    await lock_date_service.assert_not_locked(
        company_id=company_id,
        document_date=body.transfer_date,
        document_label="bank transfer",
    )
    voucher_number = str(
        await document_number_service.reserve_next(company_id=company_id, sequence_key="BT")
    )
    post_gl = await smart_runtime.post_gl_on_create(
        company_id=company_id, module_key="bankTransfer"
    )
    journal = None
    if post_gl:
        journal = await posting_service.post_bank_transfer(
            company_id=company_id,
            transfer_date=body.transfer_date,
            voucher_number=voucher_number,
            from_bank_account_id=body.from_bank_account_id,
            to_bank_account_id=body.to_bank_account_id,
            total_amount=body.total_amount,
        )
    doc_status = "posted" if journal else "draft"
    try:
        row = await repo.create_transfer(
            company_id=company_id,
            voucher_number=voucher_number,
            transfer_date=body.transfer_date,
            from_bank_account_id=body.from_bank_account_id,
            to_bank_account_id=body.to_bank_account_id,
            total_amount=body.total_amount,
            journal_id=journal.id if journal else None,
            transfer_id=transfer_id,
            status=doc_status,
        )
    except ValueError as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=str(exc)) from exc
    await audit_service.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type=SOURCE_BANK_TRANSFER,
        transaction_id=row.id,
        status="posted" if journal else "ok",
        details=(
            f"voucher={voucher_number} amount={body.total_amount} "
            f"posted={journal is not None}"
        ),
    )
    return {
        "result": jsonable_encoder(row),
        "posted": journal is not None,
        "postingWarning": None
        if journal
        else (
            "Saved as draft (Template/Draft setting). Post when ready."
            if not post_gl
            else "Both bank accounts must have a nominal code for GL posting."
        ),
    }


@router.post("/bank-transfers/{transfer_id}/post")
async def post_bank_transfer_draft(
    company_id: str,
    transfer_id: str,
    repo: Annotated[BankTransferRepository, Depends(get_bank_transfer_repository)],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    posting_service: Annotated[PostingService, Depends(get_posting_service)],
    approval_engine: Annotated[ApprovalEngineService, Depends(get_approval_engine_service)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    claims: Annotated[JwtClaims, Depends(require_permission("bank.payments.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("bank"))],
) -> dict:
    """Post a draft bank transfer to the GL."""

    from app.domain.document_workflow import SOURCE_BANK_TRANSFER
    from fastapi import HTTPException

    row = await repo.get_transfer(company_id=company_id, transfer_id=transfer_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Bank transfer not found")
    if row.journalId:
        raise HTTPException(status_code=400, detail="Transfer is already posted")
    if row.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft transfers can be posted")
    try:
        await guard_document_post(
            approval_engine,
            company_id=company_id,
            entity_type="bank_transfer",
            entity_id=transfer_id,
            amount=row.totalAmount,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    await lock_date_service.assert_not_locked(
        company_id=company_id,
        document_date=row.transferDate,
        document_label="bank transfer",
    )
    journal = await posting_service.post_bank_transfer(
        company_id=company_id,
        transfer_date=row.transferDate,
        voucher_number=row.voucherNumber,
        from_bank_account_id=row.fromBankAccountId,
        to_bank_account_id=row.toBankAccountId,
        total_amount=row.totalAmount,
    )
    if journal is None:
        raise HTTPException(
            status_code=400,
            detail="Both bank accounts must have nominal codes to post.",
        )
    updated = await repo.link_transfer_journal(
        transfer_id=transfer_id, journal_id=journal.id
    )
    await audit_service.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type=SOURCE_BANK_TRANSFER,
        transaction_id=updated.id,
        status="posted",
        details=f"voucher={row.voucherNumber} posted from draft",
    )
    return {"result": jsonable_encoder(updated), "posted": True}


@router.post("/bank-payments", status_code=201)
async def create_bank_payment(
    company_id: str,
    body: BankPaymentCreateRequest,
    svc: Annotated[BankPaymentService, Depends(get_bank_payment_service)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    approval_engine: Annotated[ApprovalEngineService, Depends(get_approval_engine_service)],
    smart_runtime: Annotated[SmartSettingsRuntime, Depends(get_smart_settings_runtime)],
    _claims: Annotated[Any, Depends(require_permission("bank.payments.create"))],
    claims: Annotated[JwtClaims, Depends(require_module_access("bank"))],
) -> dict:
    """Create a bank payment with optional counterpart nominal for GL posting."""

    from app.domain.document_workflow import SOURCE_BANK_PAYMENT
    from fastapi import HTTPException

    payment_id = str(uuid4())
    try:
        await guard_document_post(
            approval_engine,
            company_id=company_id,
            entity_type="bank_payment",
            entity_id=payment_id,
            amount=body.total_amount,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    split_lines = None
    if body.nominal_lines:
        split_lines = [(ln.nominal_code, ln.amount) for ln in body.nominal_lines]
    from app.utils.smart_filters import smart_filters_custom_fields

    post_gl = await smart_runtime.post_gl_on_create(
        company_id=company_id, module_key="bankPayment"
    )
    row = await svc.create_payment(
        company_id=company_id,
        bank_account_id=body.bank_account_id,
        payment_date=body.payment_date,
        total_amount=body.total_amount,
        nominal_code=body.nominal_code,
        nominal_lines=split_lines,
        custom_fields=smart_filters_custom_fields(body.smart_filters),
        payment_id=payment_id,
        post_gl=post_gl,
    )
    posted = row.journalId is not None
    await audit_service.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type=SOURCE_BANK_PAYMENT,
        transaction_id=row.id,
        status="posted" if posted else "ok",
        details=(
            f"voucher={row.voucherNumber} amount={body.total_amount} posted={posted}"
        ),
    )
    return jsonable_encoder(row)


@router.get("/customers")
async def list_customers(
    company_id: str,
    repo: Annotated[CustomerRepository, Depends(get_customer_repository)],
    advance_users: Annotated[AdvanceUsersService, Depends(get_advance_users_service)],
    field_masking: Annotated[FieldMaskingService, Depends(get_field_masking_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("sales"))],
) -> dict:
    """Customers."""

    rows = await repo.list_customers(company_id=company_id)
    rows = await advance_users.filter_customers(
        company_id=company_id, user_id=_read.user_id, rows=rows
    )
    dumped = _dump_rows(rows)
    masked = await field_masking.mask_for_user(
        company_id=company_id, user_id=_read.user_id, rows=dumped, entity="customer"
    )
    return {"result": masked}


@router.post("/customers", status_code=201)
async def create_customer(
    company_id: str,
    body: CreateCustomerRequest,
    repo: Annotated[CustomerRepository, Depends(get_customer_repository)],
    supplier_repo: Annotated[SupplierRepository, Depends(get_supplier_repository)],
    auto_code_service: Annotated[AutoCodeService, Depends(get_auto_code_service)],
    smart_runtime: Annotated[SmartSettingsRuntime, Depends(get_smart_settings_runtime)],
    _claims: Annotated[Any, Depends(require_permission("sales.customers.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("sales"))],
) -> dict:
    """Create a customer (§5.1)."""

    from fastapi import HTTPException

    try:
        code = await auto_code_service.resolve_code(
            company_id=company_id, entity_key="customer", provided=body.code
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    row = await repo.create_customer(
        company_id=company_id,
        code=code,
        name=body.name,
        email=body.email,
        phone=body.phone,
    )
    if await smart_runtime.others_flag(
        company_id=company_id, key="setCustomerAsSupplier"
    ):
        existing = await supplier_repo.find_by_code(company_id=company_id, code=code)
        if existing is None:
            await supplier_repo.create_supplier(
                company_id=company_id,
                code=code,
                name=body.name,
                email=body.email,
                phone=body.phone,
            )
    return {"result": jsonable_encoder(row)}


@router.get("/suppliers")
async def list_suppliers(
    company_id: str,
    repo: Annotated[SupplierRepository, Depends(get_supplier_repository)],
    advance_users: Annotated[AdvanceUsersService, Depends(get_advance_users_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("purchases"))],
) -> dict:
    """Suppliers (§6.1)."""

    rows = await repo.list_suppliers(company_id=company_id)
    rows = await advance_users.filter_suppliers(
        company_id=company_id, user_id=_read.user_id, rows=rows
    )
    return {"result": _dump_rows(rows)}


@router.post("/suppliers", status_code=201)
async def create_supplier(
    company_id: str,
    body: CreateSupplierRequest,
    repo: Annotated[SupplierRepository, Depends(get_supplier_repository)],
    auto_code_service: Annotated[AutoCodeService, Depends(get_auto_code_service)],
    _claims: Annotated[Any, Depends(require_permission("purchases.suppliers.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("purchases"))],
) -> dict:
    """Create a supplier (§6.1)."""

    from fastapi import HTTPException

    try:
        code = await auto_code_service.resolve_code(
            company_id=company_id, entity_key="supplier", provided=body.code
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    row = await repo.create_supplier(
        company_id=company_id,
        code=code,
        name=body.name,
        email=body.email,
        phone=body.phone,
    )
    return {"result": jsonable_encoder(row)}


@router.get("/products")
async def list_products(
    company_id: str,
    repo: Annotated[ProductRepository, Depends(get_product_repository)],
    advance_users: Annotated[AdvanceUsersService, Depends(get_advance_users_service)],
    field_masking: Annotated[FieldMaskingService, Depends(get_field_masking_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("inventory"))],
) -> dict:
    """Products."""

    rows = await repo.list_products(company_id=company_id)
    rows = await advance_users.filter_products(
        company_id=company_id, user_id=_read.user_id, rows=rows
    )
    dumped = _dump_rows(rows)
    masked = await field_masking.mask_for_user(
        company_id=company_id, user_id=_read.user_id, rows=dumped, entity="product"
    )
    return {"result": masked}

@router.post("/products", status_code=201)
async def create_product(
    company_id: str,
    body: CreateProductRequest,
    repo: Annotated[ProductRepository, Depends(get_product_repository)],
    auto_code_service: Annotated[AutoCodeService, Depends(get_auto_code_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("inventory"))],
) -> dict:
    """Create a product (§7.1 minimal — full master extends in Phase 6.1)."""

    from fastapi import HTTPException

    try:
        code = await auto_code_service.resolve_code(
            company_id=company_id, entity_key="product", provided=body.code
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    row = await repo.create_product(
        company_id=company_id,
        code=code,
        name=body.name,
        is_stock=body.is_stock,
    )
    return {"result": jsonable_encoder(row)}


@router.post("/bank-accounts", status_code=201)
async def create_bank_account(
    company_id: str,
    body: CreateBankAccountRequest,
    repo: Annotated[BankRepository, Depends(get_bank_repository)],
    _access: Annotated[JwtClaims, Depends(require_module_access("bank"))],
) -> dict:
    """Create a bank / cash account (§4.1)."""

    row = await repo.create_account(
        company_id=company_id,
        name=body.name,
        nominal_code=body.nominal_code,
        currency=body.currency,
    )
    return {"result": jsonable_encoder(row)}


@router.get("/supplier-bills")
async def list_supplier_bills(
    company_id: str,
    repo: Annotated[SupplierBillRepository, Depends(get_supplier_bill_repository)],
    field_masking: Annotated[FieldMaskingService, Depends(get_field_masking_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("purchases"))],
) -> dict:
    """Supplier bills."""

    rows = await repo.list_bills(company_id=company_id)
    dumped = _dump_rows(rows)
    masked = await field_masking.mask_for_user(
        company_id=company_id, user_id=_read.user_id, rows=dumped, entity="bill"
    )
    return {"result": masked}


@router.post("/supplier-bills/batch", status_code=201)
async def create_batch_supplier_bills(
    company_id: str,
    body: BatchSupplierBillCreateRequest,
    batch_service: Annotated[BatchDocumentService, Depends(get_batch_document_service)],
    prisma: Annotated[Prisma, Depends(get_prisma)],
    _claims: Annotated[Any, Depends(require_permission("purchases.bills.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("purchases"))],
) -> dict:
    """Batch supplier bill entry — one draft bill per supplier (§3.9)."""

    result = await batch_service.create_batch_supplier_bills(
        company_id=company_id,
        bill_date=body.bill_date,
        entries=body.entries,
        smart_filters=body.smart_filters,
        prisma=prisma,
    )
    return {"result": result}


@router.get("/supplier-bills/{bill_id}")
async def get_supplier_bill(
    company_id: str,
    bill_id: str,
    repo: Annotated[SupplierBillRepository, Depends(get_supplier_bill_repository)],
) -> dict:
    """Single supplier bill with lines."""

    row = await repo.get_bill(company_id=company_id, bill_id=bill_id)
    if row is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Bill not found")
    return {"result": jsonable_encoder(row)}


@router.post("/supplier-bills", status_code=201)
async def create_supplier_bill(
    company_id: str,
    body: SupplierBillCreateRequest,
    repo: Annotated[SupplierBillRepository, Depends(get_supplier_bill_repository)],
    document_number_service: Annotated[
        DocumentNumberService, Depends(get_document_number_service)
    ],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    tax_service: Annotated[TaxCalculationService, Depends(get_tax_calculation_service)],
    smart_runtime: Annotated[SmartSettingsRuntime, Depends(get_smart_settings_runtime)],
    prisma: Annotated[Prisma, Depends(get_prisma)],
    _claims: Annotated[Any, Depends(require_permission("purchases.bills.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("purchases"))],
) -> dict:
    """Create a supplier bill as draft (§6.3). Post to GL via approve endpoint."""

    await lock_date_service.assert_not_locked(
        company_id=company_id,
        document_date=body.bill_date,
        document_label="supplier bill",
    )

    bill_number = str(
        await document_number_service.reserve_next(company_id=company_id, sequence_key="VI")
    )
    taxed = await tax_service.compute_purchase_lines(
        company_id=company_id, raw_lines=body.to_raw_lines()
    )
    repo_lines = [line.to_repo_dict() for line in taxed.lines]
    from app.utils.line_description import merge_line_description_fields

    repo_lines = merge_line_description_fields(repo_lines, body.lines)
    pd_labels = await smart_runtime.product_description_labels(
        company_id=company_id, doc_type="VI"
    )
    repo_lines = smart_runtime.apply_product_description_defaults(
        repo_lines=repo_lines,
        request_lines=body.lines,
        labels=pd_labels,
    )

    from app.utils.smart_filters import smart_filters_custom_fields

    row = await repo.create_bill(
        company_id=company_id,
        bill_number=bill_number,
        bill_date=body.bill_date,
        supplier_id=body.supplier_id,
        lines=repo_lines,
        journal_id=None,
        custom_fields=smart_filters_custom_fields(body.smart_filters),
    )
    if taxed.summaries:
        await tax_service.persist_tax_summaries(
            company_id=company_id,
            document_kind="VI",
            document_id=row.id,
            summaries=taxed.summaries,
            db=prisma,
        )
    return {
        "result": jsonable_encoder(row),
        "posted": False,
        "taxTotal": str(taxed.tax_total),
        "postingWarning": "Bill saved as draft. POST .../supplier-bills/{id}/approve to post to the GL.",
    }


@router.patch("/supplier-bills/{bill_id}")
async def update_supplier_bill(
    company_id: str,
    bill_id: str,
    body: SupplierBillCreateRequest,
    repo: Annotated[SupplierBillRepository, Depends(get_supplier_bill_repository)],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    tax_service: Annotated[TaxCalculationService, Depends(get_tax_calculation_service)],
    prisma: Annotated[Prisma, Depends(get_prisma)],
    _claims: Annotated[Any, Depends(require_permission("purchases.bills.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("purchases"))],
) -> dict:
    """Update a draft supplier bill (header + lines). Posted bills are immutable."""

    from fastapi import HTTPException

    existing = await repo.get_bill(company_id=company_id, bill_id=bill_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Bill not found")
    if existing.status != "draft" or existing.journalId is not None:
        raise HTTPException(
            status_code=409,
            detail="Only draft bills can be edited",
        )

    await lock_date_service.assert_not_locked(
        company_id=company_id,
        document_date=body.bill_date,
        document_label="supplier bill",
    )

    taxed = await tax_service.compute_purchase_lines(
        company_id=company_id, raw_lines=body.to_raw_lines()
    )
    repo_lines = [line.to_repo_dict() for line in taxed.lines]
    from app.utils.line_description import merge_line_description_fields

    repo_lines = merge_line_description_fields(repo_lines, body.lines)

    try:
        row = await repo.update_draft(
            company_id=company_id,
            bill_id=bill_id,
            bill_date=body.bill_date,
            supplier_id=body.supplier_id,
            lines=repo_lines,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    await prisma.documenttaxsummary.delete_many(
        where={
            "companyId": company_id,
            "documentKind": "VI",
            "documentId": bill_id,
        }
    )
    if taxed.summaries:
        await tax_service.persist_tax_summaries(
            company_id=company_id,
            document_kind="VI",
            document_id=bill_id,
            summaries=taxed.summaries,
            db=prisma,
        )
    return {"result": jsonable_encoder(row), "taxTotal": str(taxed.tax_total)}


@router.get("/sales-invoices")
async def list_sales_invoices(
    company_id: str,
    repo: Annotated[SalesInvoiceRepository, Depends(get_sales_invoice_repository)],
    field_masking: Annotated[FieldMaskingService, Depends(get_field_masking_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("sales"))],
) -> dict:
    """Sales invoices."""

    rows = await repo.list_invoices(company_id=company_id)
    dumped = _dump_rows(rows)
    masked = await field_masking.mask_for_user(
        company_id=company_id, user_id=_read.user_id, rows=dumped, entity="invoice"
    )
    return {"result": masked}


@router.post("/sales-invoices/batch", status_code=201)
async def create_batch_sales_invoices(
    company_id: str,
    body: BatchSalesInvoiceCreateRequest,
    batch_service: Annotated[BatchDocumentService, Depends(get_batch_document_service)],
    prisma: Annotated[Prisma, Depends(get_prisma)],
    _claims: Annotated[Any, Depends(require_permission("sales.invoices.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("sales"))],
) -> dict:
    """Batch sales invoice entry — one draft invoice per customer (§3.9)."""

    result = await batch_service.create_batch_sales_invoices(
        company_id=company_id,
        invoice_date=body.invoice_date,
        entries=body.entries,
        smart_filters=body.smart_filters,
        prisma=prisma,
    )
    return {"result": result}


@router.get("/my-tasks")
async def list_my_tasks(
    company_id: str,
    service: Annotated[MyTasksService, Depends(get_my_tasks_service)],
    _claims: Annotated[JwtClaims, Depends(resolve_tenant)],
) -> dict:
    """Draft documents and items needing attention (FastAccounts My Tasks)."""

    return {"result": await service.list_tasks(company_id=company_id)}


@router.get("/sales-activity")
async def list_sales_activity(
    company_id: str,
    service: Annotated[ActivityService, Depends(get_activity_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("sales"))],
    include_planning: bool = Query(default=False, alias="includePlanning"),
    date_from: str | None = Query(default=None, alias="dateFrom"),
    date_to: str | None = Query(default=None, alias="dateTo"),
    party_id: str | None = Query(default=None, alias="partyId"),
    doc_type: str | None = Query(default=None, alias="docType"),
    status: str | None = Query(default=None),
) -> dict:
    """Unified sales invoices, receipts, and credits (FastAccounts Sales All)."""

    return {
        "result": await service.list_sales_activity(
            company_id=company_id,
            include_planning=include_planning,
            date_from=date_from,
            date_to=date_to,
            party_id=party_id,
            doc_type=doc_type,
            status=status,
        )
    }


@router.get("/purchases-activity")
async def list_purchases_activity(
    company_id: str,
    service: Annotated[ActivityService, Depends(get_activity_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("purchases"))],
    include_planning: bool = Query(default=False, alias="includePlanning"),
    date_from: str | None = Query(default=None, alias="dateFrom"),
    date_to: str | None = Query(default=None, alias="dateTo"),
    party_id: str | None = Query(default=None, alias="partyId"),
    doc_type: str | None = Query(default=None, alias="docType"),
    status: str | None = Query(default=None),
) -> dict:
    """Unified supplier bills, payments, and credits (FastAccounts Purchases All)."""

    return {
        "result": await service.list_purchases_activity(
            company_id=company_id,
            include_planning=include_planning,
            date_from=date_from,
            date_to=date_to,
            party_id=party_id,
            doc_type=doc_type,
            status=status,
        )
    }


@router.get("/sales-invoices/{invoice_id}")
async def get_sales_invoice(
    company_id: str,
    invoice_id: str,
    repo: Annotated[SalesInvoiceRepository, Depends(get_sales_invoice_repository)],
) -> dict:
    """Single invoice with lines."""

    row = await repo.get_invoice(company_id=company_id, invoice_id=invoice_id)
    if row is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Invoice not found")
    return {"result": jsonable_encoder(row)}


@router.patch("/sales-invoices/{invoice_id}")
async def update_sales_invoice(
    company_id: str,
    invoice_id: str,
    body: SalesInvoiceCreateRequest,
    repo: Annotated[SalesInvoiceRepository, Depends(get_sales_invoice_repository)],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    tax_service: Annotated[TaxCalculationService, Depends(get_tax_calculation_service)],
    prisma: Annotated[Prisma, Depends(get_prisma)],
    _claims: Annotated[Any, Depends(require_permission("sales.invoices.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("sales"))],
) -> dict:
    """Update a draft sales invoice (header + lines). Posted invoices are immutable."""

    from fastapi import HTTPException

    existing = await repo.get_invoice(company_id=company_id, invoice_id=invoice_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if existing.status != "draft" or existing.journalId is not None:
        raise HTTPException(
            status_code=409,
            detail="Only draft invoices can be edited",
        )

    await lock_date_service.assert_not_locked(
        company_id=company_id,
        document_date=body.invoice_date,
        document_label="sales invoice",
    )

    taxed = await tax_service.compute_sales_lines(
        company_id=company_id, raw_lines=body.to_raw_lines()
    )
    repo_lines = [line.to_repo_dict() for line in taxed.lines]
    from app.utils.line_description import merge_line_description_fields

    repo_lines = merge_line_description_fields(repo_lines, body.lines)

    try:
        row = await repo.update_draft(
            company_id=company_id,
            invoice_id=invoice_id,
            invoice_date=body.invoice_date,
            customer_id=body.customer_id,
            lines=repo_lines,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    await prisma.documenttaxsummary.delete_many(
        where={
            "companyId": company_id,
            "documentKind": "SI",
            "documentId": invoice_id,
        }
    )
    if taxed.summaries:
        await tax_service.persist_tax_summaries(
            company_id=company_id,
            document_kind="SI",
            document_id=invoice_id,
            summaries=taxed.summaries,
            db=prisma,
        )
    return {"result": jsonable_encoder(row), "taxTotal": str(taxed.tax_total)}


@router.post("/sales-invoices", status_code=201)
async def create_sales_invoice(
    company_id: str,
    body: SalesInvoiceCreateRequest,
    repo: Annotated[SalesInvoiceRepository, Depends(get_sales_invoice_repository)],
    document_number_service: Annotated[
        DocumentNumberService, Depends(get_document_number_service)
    ],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    tax_service: Annotated[TaxCalculationService, Depends(get_tax_calculation_service)],
    smart_runtime: Annotated[SmartSettingsRuntime, Depends(get_smart_settings_runtime)],
    prisma: Annotated[Prisma, Depends(get_prisma)],
    _claims: Annotated[Any, Depends(require_permission("sales.invoices.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("sales"))],
) -> dict:
    """Create a sales invoice as draft (§5.4). Post to GL via approve endpoint."""

    await lock_date_service.assert_not_locked(
        company_id=company_id,
        document_date=body.invoice_date,
        document_label="sales invoice",
    )

    invoice_number = str(
        await document_number_service.reserve_next(company_id=company_id, sequence_key="SI")
    )
    taxed = await tax_service.compute_sales_lines(
        company_id=company_id, raw_lines=body.to_raw_lines()
    )
    repo_lines = [line.to_repo_dict() for line in taxed.lines]
    from app.utils.line_description import merge_line_description_fields

    repo_lines = merge_line_description_fields(repo_lines, body.lines)
    pd_labels = await smart_runtime.product_description_labels(
        company_id=company_id, doc_type="SI"
    )
    repo_lines = smart_runtime.apply_product_description_defaults(
        repo_lines=repo_lines,
        request_lines=body.lines,
        labels=pd_labels,
    )

    from app.utils.smart_filters import smart_filters_custom_fields

    row = await repo.create_invoice(
        company_id=company_id,
        invoice_number=invoice_number,
        invoice_date=body.invoice_date,
        customer_id=body.customer_id,
        lines=repo_lines,
        journal_id=None,
        custom_fields=smart_filters_custom_fields(body.smart_filters),
    )
    if taxed.summaries:
        await tax_service.persist_tax_summaries(
            company_id=company_id,
            document_kind="SI",
            document_id=row.id,
            summaries=taxed.summaries,
            db=prisma,
        )
    return {
        "result": jsonable_encoder(row),
        "posted": False,
        "taxTotal": str(taxed.tax_total),
        "postingWarning": "Invoice saved as draft. POST .../sales-invoices/{id}/approve to post to the GL.",
    }


@router.post("/sales-invoices/{invoice_id}/approve")
async def approve_sales_invoice(
    company_id: str,
    invoice_id: str,
    posting_engine: Annotated[PostingEngine, Depends(get_posting_engine)],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    repo: Annotated[SalesInvoiceRepository, Depends(get_sales_invoice_repository)],
    approval_engine: Annotated[ApprovalEngineService, Depends(get_approval_engine_service)],
    smart_runtime: Annotated[SmartSettingsRuntime, Depends(get_smart_settings_runtime)],
    claims: Annotated[JwtClaims, Depends(require_permission("sales.invoices.approve"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("sales"))],
) -> dict:
    """Post a draft sales invoice to the GL (P0 workflow)."""

    from fastapi import HTTPException

    row = await repo.get_invoice(company_id=company_id, invoice_id=invoice_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    await lock_date_service.assert_not_locked(
        company_id=company_id,
        document_date=row.invoiceDate,
        document_label="sales invoice",
        user_id=claims.user_id,
    )
    try:
        await smart_runtime.assert_credit_limit(
            company_id=company_id,
            customer_id=row.customerId,
            additional_amount=Decimal(str(row.totalAmount)),
        )
        await approval_engine.assert_can_post(
            company_id=company_id,
            entity_type="sales_invoice",
            entity_id=invoice_id,
            amount=Decimal(str(row.totalAmount)),
        )
        posted = await posting_engine.approve_sales_invoice(
            company_id=company_id, invoice_id=invoice_id
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(posted), "posted": True}


@router.post("/sales-invoices/{invoice_id}/email")
async def email_sales_invoice(
    company_id: str,
    invoice_id: str,
    body: SalesInvoiceEmailRequest,
    email_service: Annotated[
        SalesInvoiceEmailService, Depends(get_sales_invoice_email_service)
    ],
    _claims: Annotated[JwtClaims, Depends(require_permission("sales.invoices.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("sales"))],
) -> dict:
    """Email invoice PDF summary to the customer — P5."""

    from fastapi import HTTPException

    try:
        result = await email_service.send_invoice_email(
            company_id=company_id,
            invoice_id=invoice_id,
            to_email=body.to,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": result}


@router.post("/sales-invoices/{invoice_id}/copy", status_code=201)
async def copy_sales_invoice(
    company_id: str,
    invoice_id: str,
    repo: Annotated[SalesInvoiceRepository, Depends(get_sales_invoice_repository)],
    document_number_service: Annotated[
        DocumentNumberService, Depends(get_document_number_service)
    ],
    tax_service: Annotated[TaxCalculationService, Depends(get_tax_calculation_service)],
    prisma: Annotated[Prisma, Depends(get_prisma)],
    _access: Annotated[JwtClaims, Depends(require_module_access("sales"))],
) -> dict:
    """Copy a sales invoice as a new draft (FA §3.9)."""

    from fastapi import HTTPException

    source = await repo.get_invoice(company_id=company_id, invoice_id=invoice_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    invoice_number = str(
        await document_number_service.reserve_next(company_id=company_id, sequence_key="SI")
    )
    raw_lines = [
        {
            "productCode": line.productCode,
            "quantity": line.quantity,
            "rate": line.rate,
            "gstCode": line.gstCode,
            "gstRate": line.gstRate,
            "projectCode": line.projectCode,
        }
        for line in source.lines or []
    ]
    taxed = await tax_service.compute_sales_lines(
        company_id=company_id, raw_lines=raw_lines
    )
    repo_lines = [line.to_repo_dict() for line in taxed.lines]
    row = await repo.create_invoice(
        company_id=company_id,
        invoice_number=invoice_number,
        invoice_date=source.invoiceDate,
        customer_id=source.customerId,
        lines=repo_lines,
        journal_id=None,
    )
    if taxed.summaries:
        await tax_service.persist_tax_summaries(
            company_id=company_id,
            document_kind="SI",
            document_id=row.id,
            summaries=taxed.summaries,
            db=prisma,
        )
    return {
        "result": jsonable_encoder(row),
        "posted": False,
        "copiedFromId": invoice_id,
    }


@router.post("/sales-invoices/{invoice_id}/void")
async def void_sales_invoice(
    company_id: str,
    invoice_id: str,
    body: DocumentVoidRequest,
    reversal_service: Annotated[
        DocumentReversalService, Depends(get_document_reversal_service)
    ],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    _claims: Annotated[Any, Depends(require_permission("sales.invoices.approve"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("sales"))],
) -> dict:
    from fastapi import HTTPException

    if body.reversal_date:
        await lock_date_service.assert_not_locked(
            company_id=company_id,
            document_date=body.reversal_date,
            document_label="sales invoice void",
        )
    try:
        out = await reversal_service.void_sales_invoice(
            company_id=company_id,
            invoice_id=invoice_id,
            reversal_date=body.reversal_date,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(out)}


@router.post("/sales-invoices/{invoice_id}/void-goods-issue")
async def void_sales_invoice_goods_issue_only(
    company_id: str,
    invoice_id: str,
    body: DocumentVoidRequest,
    reversal_service: Annotated[
        DocumentReversalService, Depends(get_document_reversal_service)
    ],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    _claims: Annotated[Any, Depends(require_permission("sales.invoices.approve"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("sales"))],
) -> dict:
    from fastapi import HTTPException

    if body.reversal_date:
        await lock_date_service.assert_not_locked(
            company_id=company_id,
            document_date=body.reversal_date,
            document_label="goods issue void",
        )
    try:
        out = await reversal_service.void_goods_issue_only(
            company_id=company_id,
            invoice_id=invoice_id,
            reversal_date=body.reversal_date,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(out)}


@router.post("/sales-invoices/{invoice_id}/goods-issue/lines/{line_id}/void")
async def void_sales_invoice_goods_issue_line(
    company_id: str,
    invoice_id: str,
    line_id: str,
    body: GoodsIssueLineVoidRequest,
    reversal_service: Annotated[
        DocumentReversalService, Depends(get_document_reversal_service)
    ],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    _claims: Annotated[Any, Depends(require_permission("sales.invoices.approve"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("sales"))],
) -> dict:
    from fastapi import HTTPException

    if body.reversal_date:
        await lock_date_service.assert_not_locked(
            company_id=company_id,
            document_date=body.reversal_date,
            document_label="goods issue line void",
        )
    try:
        out = await reversal_service.void_goods_issue_line(
            company_id=company_id,
            invoice_id=invoice_id,
            line_id=line_id,
            reversal_date=body.reversal_date,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(out)}


@router.post("/sales-invoices/{invoice_id}/goods-issue/repost-remaining-cogs")
async def repost_sales_invoice_goods_issue_cogs(
    company_id: str,
    invoice_id: str,
    body: GoodsIssueLineVoidRequest,
    reversal_service: Annotated[
        DocumentReversalService, Depends(get_document_reversal_service)
    ],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("sales"))],
) -> dict:
    from fastapi import HTTPException

    journal_date = body.reversal_date
    if journal_date:
        await lock_date_service.assert_not_locked(
            company_id=company_id,
            document_date=journal_date,
            document_label="goods issue COGS repost",
        )
    try:
        out = await reversal_service.repost_remaining_goods_issue_cogs(
            company_id=company_id,
            invoice_id=invoice_id,
            journal_date=journal_date,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(out)}


@router.get("/sales-invoices/{invoice_id}/goods-issue")
async def get_goods_issue_for_invoice(
    company_id: str,
    invoice_id: str,
    repo: Annotated[GoodsIssueRepository, Depends(get_goods_issue_repository)],
) -> dict:
    """Goods issue voucher linked to a posted sales invoice (P2)."""

    from fastapi import HTTPException

    row = await repo.get_by_invoice(
        company_id=company_id, sales_invoice_id=invoice_id
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Goods issue not found")
    return {"result": jsonable_encoder(row)}


@router.post("/sales-invoices/{invoice_id}/goods-issue", status_code=201)
async def create_goods_issue_for_invoice(
    company_id: str,
    invoice_id: str,
    posting_engine: Annotated[PostingEngine, Depends(get_posting_engine)],
    stock_guard: Annotated[
        InventoryStockGuardService, Depends(get_inventory_stock_guard_service)
    ],
    _claims: Annotated[Any, Depends(require_permission("sales.invoices.approve"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("sales"))],
    skip_stock_movement: bool = Query(default=False, alias="skipStockMovement"),
) -> dict:
    """Issue stock / post COGS for a posted sales invoice (P2)."""

    from fastapi import HTTPException

    try:
        await stock_guard.assert_goods_issue_allowed(
            company_id=company_id,
            invoice_id=invoice_id,
            skip_stock_movement=skip_stock_movement,
        )
        row = await posting_engine.issue_goods_for_invoice(
            company_id=company_id, invoice_id=invoice_id
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "result": jsonable_encoder(row),
        "posted": True,
        "stockGuardSkipped": skip_stock_movement,
    }


@router.post("/supplier-bills/{bill_id}/approve")
async def approve_supplier_bill(
    company_id: str,
    bill_id: str,
    posting_engine: Annotated[PostingEngine, Depends(get_posting_engine)],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    repo: Annotated[SupplierBillRepository, Depends(get_supplier_bill_repository)],
    approval_engine: Annotated[ApprovalEngineService, Depends(get_approval_engine_service)],
    claims: Annotated[JwtClaims, Depends(require_permission("purchases.bills.approve"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("purchases"))],
) -> dict:
    """Post a draft supplier bill to the GL (P0 workflow)."""

    from fastapi import HTTPException

    row = await repo.get_bill(company_id=company_id, bill_id=bill_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Bill not found")
    await lock_date_service.assert_not_locked(
        company_id=company_id,
        document_date=row.billDate,
        document_label="supplier bill",
        user_id=claims.user_id,
    )
    try:
        await approval_engine.assert_can_post(
            company_id=company_id,
            entity_type="supplier_bill",
            entity_id=bill_id,
            amount=Decimal(str(row.totalAmount)),
        )
        posted = await posting_engine.approve_supplier_bill(
            company_id=company_id, bill_id=bill_id
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(posted), "posted": True}


@router.post("/supplier-bills/{bill_id}/void")
async def void_supplier_bill(
    company_id: str,
    bill_id: str,
    body: DocumentVoidRequest,
    reversal_service: Annotated[
        DocumentReversalService, Depends(get_document_reversal_service)
    ],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    _claims: Annotated[Any, Depends(require_permission("purchases.bills.approve"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("purchases"))],
) -> dict:
    from fastapi import HTTPException

    if body.reversal_date:
        await lock_date_service.assert_not_locked(
            company_id=company_id,
            document_date=body.reversal_date,
            document_label="supplier bill void",
        )
    try:
        out = await reversal_service.void_supplier_bill(
            company_id=company_id,
            bill_id=bill_id,
            reversal_date=body.reversal_date,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(out)}


@router.get("/journals")
async def list_journals(
    company_id: str,
    journal_service: Annotated[JournalService, Depends(get_journal_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    """General journals."""

    rows = await journal_service.list_journals(company_id=company_id)
    return {"result": _dump_rows(rows)}


@router.get("/journals/{journal_id}")
async def get_journal(
    company_id: str,
    journal_id: str,
    journal_repository: Annotated[JournalRepository, Depends(get_journal_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    """Single journal voucher with line grid."""

    row = await journal_repository.get_by_id(
        company_id=company_id, journal_id=journal_id
    )
    if row is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Journal not found")
    return {"result": jsonable_encoder(row)}


@router.post("/journals", status_code=201)
async def create_journal(
    company_id: str,
    body: JournalCreateRequest,
    journal_service: Annotated[JournalService, Depends(get_journal_service)],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    approval_engine: Annotated[ApprovalEngineService, Depends(get_approval_engine_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    """Create balanced journal after enforcing the company lock date."""

    from fastapi import HTTPException

    if body.status != "draft":
        await lock_date_service.assert_not_locked(
            company_id=company_id,
            document_date=body.journal_date,
            document_label="journal",
        )
    lines = body.to_prisma_lines()
    total_debit = sum(Decimal(str(line.get("debit", 0))) for line in lines)
    journal_id = str(uuid4())
    try:
        if body.status != "draft":
            await approval_engine.assert_can_post(
                company_id=company_id,
                entity_type="journal",
                entity_id=journal_id,
                amount=total_debit,
            )
        row = await journal_service.create_journal(
            company_id=company_id,
            journal_date=body.journal_date,
            ref_no=body.ref_no,
            lines=lines,
            journal_id=journal_id,
            status=body.status,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(row)}


@router.patch("/journals/{journal_id}")
async def update_journal(
    company_id: str,
    journal_id: str,
    body: JournalUpdateRequest,
    journal_service: Annotated[JournalService, Depends(get_journal_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    """Replace a draft journal header and line grid."""

    from fastapi import HTTPException

    try:
        row = await journal_service.update_draft(
            company_id=company_id,
            journal_id=journal_id,
            journal_date=body.journal_date,
            ref_no=body.ref_no,
            lines=body.to_prisma_lines(),
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(row)}


@router.post("/journals/{journal_id}/post")
async def post_journal(
    company_id: str,
    journal_id: str,
    journal_service: Annotated[JournalService, Depends(get_journal_service)],
    approval_engine: Annotated[ApprovalEngineService, Depends(get_approval_engine_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    """Post a draft journal to the GL."""

    from fastapi import HTTPException

    existing = await journal_service.get_journal(
        company_id=company_id, journal_id=journal_id
    )
    if existing is None:
        raise HTTPException(status_code=404, detail="Journal not found")
    try:
        await approval_engine.assert_can_post(
            company_id=company_id,
            entity_type="journal",
            entity_id=journal_id,
            amount=existing.totalAmount,
        )
        row = await journal_service.post_draft(
            company_id=company_id, journal_id=journal_id
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(row)}


@router.post("/journals/{journal_id}/reverse", status_code=201)
async def reverse_journal(
    company_id: str,
    journal_id: str,
    body: JournalReverseRequest,
    journal_service: Annotated[JournalService, Depends(get_journal_service)],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    _claims: Annotated[Any, Depends(require_permission("settings.journals.reverse"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    """Reverse a posted journal (immutable ledger — storno entry)."""

    from fastapi import HTTPException

    await lock_date_service.assert_not_locked(
        company_id=company_id,
        document_date=body.reversal_date,
        document_label="journal reversal",
    )
    try:
        row = await journal_service.reverse_journal(
            company_id=company_id,
            journal_id=journal_id,
            reversal_date=body.reversal_date,
            ref_no=body.ref_no,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(row)}


@router.post("/journals/{journal_id}/copy", status_code=201)
async def copy_journal(
    company_id: str,
    journal_id: str,
    journal_service: Annotated[JournalService, Depends(get_journal_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    """Copy a journal voucher with a new number (FA §3.9)."""

    from fastapi import HTTPException

    try:
        row = await journal_service.copy_journal(
            company_id=company_id, journal_id=journal_id
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(row)}


@router.post("/journals/bulk-delete")
async def bulk_delete_journals(
    company_id: str,
    body: dict[str, Any],
    journal_service: Annotated[JournalService, Depends(get_journal_service)],
    _claims: Annotated[Any, Depends(require_permission("settings.journals.delete"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    """Delete manual draft journals (FA bulk delete)."""

    ids = body.get("journalIds") or body.get("ids") or []
    if not isinstance(ids, list):
        raise ValidationAppError("journalIds must be a list")
    result = await journal_service.bulk_delete_drafts(
        company_id=company_id,
        journal_ids=[str(i) for i in ids],
    )
    return {"result": result}


@router.get("/budgets")
async def list_budgets(
    company_id: str,
    service: Annotated[BudgetService, Depends(get_budget_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    """Budget headers and lines — FA §9.3."""

    rows = await service.list_budgets(company_id=company_id)
    return {"result": _dump_rows(rows)}


@router.get("/budgets/{budget_id}")
async def get_budget(
    company_id: str,
    budget_id: str,
    service: Annotated[BudgetService, Depends(get_budget_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    from fastapi import HTTPException

    row = await service.get_budget(company_id=company_id, budget_id=budget_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Budget not found")
    return {"result": jsonable_encoder(row)}


@router.post("/budgets", status_code=201)
async def create_budget(
    company_id: str,
    body: BudgetCreateRequest,
    service: Annotated[BudgetService, Depends(get_budget_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    from fastapi import HTTPException

    try:
        row = await service.create_budget(
            company_id=company_id,
            code=body.code,
            name=body.name,
            fiscal_year=body.fiscal_year,
            lines=body.lines,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(row)}


@router.patch("/budgets/{budget_id}")
async def update_budget(
    company_id: str,
    budget_id: str,
    body: BudgetUpdateRequest,
    service: Annotated[BudgetService, Depends(get_budget_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    from fastapi import HTTPException

    row = await service.update_budget(
        company_id=company_id,
        budget_id=budget_id,
        name=body.name,
        is_active=body.is_active,
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Budget not found")
    return {"result": jsonable_encoder(row)}


@router.get("/reports/trial-balance")
async def report_trial_balance(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    journal_repository: Annotated[JournalRepository, Depends(get_read_journal_repository)],
    as_of_date: datetime | None = Query(default=None, alias="asOfDate"),
) -> dict:
    """Trial balance aggregated from posted journal lines (catalog §10 Financial)."""

    rows = await journal_repository.trial_balance(
        company_id=company_id,
        as_of_date=as_of_date,
    )
    return {"result": rows}


@router.get("/reports/profit-and-loss")
async def report_profit_and_loss(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    journal_repository: Annotated[JournalRepository, Depends(get_read_journal_repository)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    """
    Profit & Loss derived from posted journals, classified by
    ``CoaCategory.categoryType`` (Income vs Expense).
    """

    from decimal import Decimal

    rows = await journal_repository.classified_balances(
        company_id=company_id,
        date_from=date_from,
        date_to=date_to,
    )

    income_rows = [r for r in rows if r["categoryType"] == "Income"]
    expense_rows = [r for r in rows if r["categoryType"] == "Expense"]

    # Income is naturally a credit balance; show as a positive figure on the P&L.
    income_total = sum(
        (Decimal(r["credit"]) - Decimal(r["debit"]) for r in income_rows),
        Decimal(0),
    )
    expense_total = sum(
        (Decimal(r["debit"]) - Decimal(r["credit"]) for r in expense_rows),
        Decimal(0),
    )
    net_profit = income_total - expense_total

    return {
        "result": {
            "income": [
                {
                    "nominalCode": r["nominalCode"],
                    "name": r["name"],
                    "categoryName": r["categoryName"],
                    "amount": str(Decimal(r["credit"]) - Decimal(r["debit"])),
                }
                for r in income_rows
            ],
            "expense": [
                {
                    "nominalCode": r["nominalCode"],
                    "name": r["name"],
                    "categoryName": r["categoryName"],
                    "amount": str(Decimal(r["debit"]) - Decimal(r["credit"])),
                }
                for r in expense_rows
            ],
            "totals": {
                "income": str(income_total),
                "expense": str(expense_total),
                "netProfit": str(net_profit),
            },
        }
    }


@router.get("/reports/comparative-profit-and-loss")
async def report_comparative_profit_and_loss(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
    period_count: int = Query(default=12, alias="periodCount", ge=1, le=36),
    as_of_date: datetime | None = Query(default=None, alias="asOfDate"),
) -> dict:
    from app.services.report_query_service import ReportQueryService

    criteria: dict = {"periodCount": period_count}
    if as_of_date:
        criteria["dateTo"] = as_of_date.isoformat()
    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="FIN_CMP", criteria=criteria
    )
    return {"result": rows}


@router.get("/reports/comparative-pnl-by-category")
async def report_comparative_pnl_by_category(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
    period_count: int = Query(default=12, alias="periodCount", ge=1, le=36),
    as_of_date: datetime | None = Query(default=None, alias="asOfDate"),
) -> dict:
    from app.services.report_query_service import ReportQueryService

    criteria: dict = {"periodCount": period_count}
    if as_of_date:
        criteria["dateTo"] = as_of_date.isoformat()
    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="FIN_PNL_CAT", criteria=criteria
    )
    return {"result": rows}


@router.get("/reports/comparative-pnl-by-category/pivot")
async def report_comparative_pnl_by_category_pivot(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
    period_count: int = Query(default=12, alias="periodCount", ge=1, le=36),
    as_of_date: datetime | None = Query(default=None, alias="asOfDate"),
) -> dict:
    from app.services.report_query_service import ReportQueryService

    criteria: dict = {"periodCount": period_count}
    if as_of_date:
        criteria["dateTo"] = as_of_date.isoformat()
    flat = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="FIN_PNL_CAT", criteria=criteria
    )
    from app.services.report_pivot_service import build_pnl_category_pivot

    return {"result": build_pnl_category_pivot(flat)}


@router.get("/reports/comparative-pnl-by-category/pivot/export")
async def export_comparative_pnl_by_category_pivot(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
    period_count: int = Query(default=12, alias="periodCount", ge=1, le=36),
    as_of_date: datetime | None = Query(default=None, alias="asOfDate"),
) -> Any:
    from fastapi.responses import Response

    from app.services.report_pivot_service import (
        build_pnl_category_pivot,
        pivot_pnl_category_to_csv,
    )
    from app.services.report_query_service import ReportQueryService

    criteria: dict = {"periodCount": period_count}
    if as_of_date:
        criteria["dateTo"] = as_of_date.isoformat()
    flat = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="FIN_PNL_CAT", criteria=criteria
    )
    pivot = build_pnl_category_pivot(flat)
    csv_text = pivot_pnl_category_to_csv(pivot)
    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="comparative-pnl-by-category.csv"'
        },
    )


@router.get("/reports/balance-sheet")
async def report_balance_sheet(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    journal_repository: Annotated[JournalRepository, Depends(get_read_journal_repository)],
    as_of_date: datetime | None = Query(default=None, alias="asOfDate"),
) -> dict:
    """
    Balance Sheet at ``as_of_date`` (inclusive). Assets show as positive debit
    balances; liabilities and equity as positive credit balances. Retained
    earnings = net of Income − Expense through the same cutoff.
    """

    from decimal import Decimal

    rows = await journal_repository.classified_balances(
        company_id=company_id,
        date_from=None,
        date_to=as_of_date,
    )

    asset_rows = [r for r in rows if r["categoryType"] == "Asset"]
    liability_rows = [r for r in rows if r["categoryType"] == "Liability"]
    equity_rows = [r for r in rows if r["categoryType"] == "Equity"]
    income_rows = [r for r in rows if r["categoryType"] == "Income"]
    expense_rows = [r for r in rows if r["categoryType"] == "Expense"]
    other_rows = [r for r in rows if r["categoryType"] not in {
        "Asset", "Liability", "Equity", "Income", "Expense",
    }]

    asset_total = sum(
        (Decimal(r["debit"]) - Decimal(r["credit"]) for r in asset_rows),
        Decimal(0),
    )
    liability_total = sum(
        (Decimal(r["credit"]) - Decimal(r["debit"]) for r in liability_rows),
        Decimal(0),
    )
    equity_total = sum(
        (Decimal(r["credit"]) - Decimal(r["debit"]) for r in equity_rows),
        Decimal(0),
    )
    retained_earnings = sum(
        (Decimal(r["credit"]) - Decimal(r["debit"]) for r in income_rows),
        Decimal(0),
    ) - sum(
        (Decimal(r["debit"]) - Decimal(r["credit"]) for r in expense_rows),
        Decimal(0),
    )
    other_net = sum(
        (Decimal(r["debit"]) - Decimal(r["credit"]) for r in other_rows),
        Decimal(0),
    )

    rhs_total = liability_total + equity_total + retained_earnings
    difference = asset_total - rhs_total - other_net

    return {
        "result": {
            "assets": [
                {
                    "nominalCode": r["nominalCode"],
                    "name": r["name"],
                    "categoryName": r["categoryName"],
                    "amount": str(Decimal(r["debit"]) - Decimal(r["credit"])),
                }
                for r in asset_rows
            ],
            "liabilities": [
                {
                    "nominalCode": r["nominalCode"],
                    "name": r["name"],
                    "categoryName": r["categoryName"],
                    "amount": str(Decimal(r["credit"]) - Decimal(r["debit"])),
                }
                for r in liability_rows
            ],
            "equity": [
                {
                    "nominalCode": r["nominalCode"],
                    "name": r["name"],
                    "categoryName": r["categoryName"],
                    "amount": str(Decimal(r["credit"]) - Decimal(r["debit"])),
                }
                for r in equity_rows
            ],
            "uncategorized": [
                {
                    "nominalCode": r["nominalCode"],
                    "name": r["name"],
                    "categoryName": r["categoryName"],
                    "amount": str(Decimal(r["debit"]) - Decimal(r["credit"])),
                }
                for r in other_rows
            ],
            "totals": {
                "assets": str(asset_total),
                "liabilities": str(liability_total),
                "equity": str(equity_total),
                "retainedEarnings": str(retained_earnings),
                "uncategorized": str(other_net),
                "difference": str(difference),
            },
        }
    }


@router.get("/reports/ar-aging")
async def report_ar_aging(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    aging_service: Annotated[AgingService, Depends(get_read_aging_service)],
    as_of_date: datetime | None = Query(default=None, alias="asOfDate"),
) -> dict:
    """Accounts receivable aging — per customer bucketed by oldest open invoice (§10.9)."""

    result = await aging_service.ar_aging(company_id=company_id, as_of_date=as_of_date)
    return {"result": result}


@router.get("/reports/ap-aging")
async def report_ap_aging(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    aging_service: Annotated[AgingService, Depends(get_read_aging_service)],
    as_of_date: datetime | None = Query(default=None, alias="asOfDate"),
) -> dict:
    """Accounts payable aging — per supplier bucketed by oldest open bill (§10.9)."""

    result = await aging_service.ap_aging(company_id=company_id, as_of_date=as_of_date)
    return {"result": result}


@router.get("/reports/customer-statement")
async def report_customer_statement(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    aging_service: Annotated[AgingService, Depends(get_read_aging_service)],
    customer_id: str = Query(..., alias="customerId"),
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    """Per-customer ledger with running balance (catalog §5.9)."""

    result = await aging_service.customer_statement(
        company_id=company_id,
        customer_id=customer_id,
        date_from=date_from,
        date_to=date_to,
    )
    return {"result": result}


@router.get("/reports/supplier-statement")
async def report_supplier_statement(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    aging_service: Annotated[AgingService, Depends(get_read_aging_service)],
    supplier_id: str = Query(..., alias="supplierId"),
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    """Per-supplier ledger with running balance (catalog §6 supplier statement)."""

    result = await aging_service.supplier_statement(
        company_id=company_id,
        supplier_id=supplier_id,
        date_from=date_from,
        date_to=date_to,
    )
    return {"result": result}


@router.get("/reports/general-ledger")
async def report_general_ledger(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    journal_repository: Annotated[JournalRepository, Depends(get_read_journal_repository)],
    nominal_code: str = Query(..., alias="nominalCode"),
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    """Opening + activity + closing for one nominal (catalog §10 Financial)."""

    result = await journal_repository.general_ledger(
        company_id=company_id,
        nominal_code=nominal_code,
        date_from=date_from,
        date_to=date_to,
    )
    return {"result": result}


@router.get("/reports/definitions", response_model=None)
async def list_report_definitions(
    company_id: str,
    report_service: Annotated[ReportService, Depends(get_report_service)],
    category: str | None = None,
    hub: Literal["standard", "analytical"] | None = None,
    favourites_only: bool = Query(default=False, alias="favouritesOnly"),
    if_none_match: str | None = Header(default=None, alias="If-None-Match"),
) -> Response:
    """Report catalog."""

    etag = report_service.definitions_etag(
        category=category,
        hub=hub,
        favourites_only=favourites_only,
    )
    cache_headers = {"ETag": f'"{etag}"', "Cache-Control": REFERENCE_CACHE_CONTROL}
    if if_none_match and if_none_match.strip('"') == etag:
        return Response(status_code=304, headers=cache_headers)
    rows = report_service.list_definitions(
        category=category,
        hub=hub,
        favourites_only=favourites_only,
    )
    body = {
        "result": [r.model_dump(mode="json", by_alias=True) for r in rows],
    }
    return JSONResponse(
        content=body,
        headers=cache_headers,
    )


@router.get("/reports/execute")
async def execute_report_sync(
    request: Request,
    company_id: str,
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
    report_id: str = Query(alias="reportId"),
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
    customer_id: str | None = Query(default=None, alias="customerId"),
    supplier_id: str | None = Query(default=None, alias="supplierId"),
    product_code: str | None = Query(default=None, alias="productCode"),
    status: str | None = Query(default=None),
    budget_id: str | None = Query(default=None, alias="budgetId"),
    as_of_date: datetime | None = Query(default=None, alias="asOfDate"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=200, alias="pageSize", ge=1, le=5000),
    cursor_date: str | None = Query(default=None, alias="cursorDate"),
    cursor_id: str | None = Query(default=None, alias="cursorId"),
    cursor_code: str | None = Query(default=None, alias="cursorCode"),
    include_pagination_meta: bool = Query(default=False, alias="includePaginationMeta"),
) -> dict:
    """Run a catalog report synchronously (for interactive UI)."""

    from app.core.rate_limit import check_rate_limit_async
    from app.services.report_query_service import ReportQueryService

    await check_rate_limit_async(request, group="reports", subject=company_id)

    criteria: dict[str, object] = {"page": page, "pageSize": page_size}
    if cursor_date:
        criteria["cursorDate"] = cursor_date
    if cursor_id:
        criteria["cursorId"] = cursor_id
    if cursor_code:
        criteria["cursorCode"] = cursor_code
    if include_pagination_meta:
        criteria["includePaginationMeta"] = True
    if date_from is not None:
        criteria["dateFrom"] = date_from.date().isoformat()
    if date_to is not None:
        criteria["dateTo"] = date_to.date().isoformat()
    if customer_id:
        criteria["customerId"] = customer_id
    if supplier_id:
        criteria["supplierId"] = supplier_id
    if product_code:
        criteria["productCode"] = product_code
    if status:
        criteria["status"] = status
    if budget_id:
        criteria["budgetId"] = budget_id
    if as_of_date is not None:
        criteria["asOfDate"] = as_of_date.date().isoformat()
    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id,
        report_id=report_id,
        criteria=criteria,
    )
    return {"result": rows}


@router.post("/reports/export")
async def export_report_sync(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    body: ReportSyncExportRequest,
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
    report_service: Annotated[ReportService, Depends(get_report_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    """Execute a catalog report and return CSV/JSON/PDF export payload (§4.6)."""

    from app.services.report_query_service import ReportQueryService

    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id,
        report_id=body.report_id,
        criteria=body.criteria,
    )
    data_rows = [r for r in rows if isinstance(r, dict) and "_meta" not in r]
    result = report_service.format_rows_export(
        rows=data_rows,
        export_format=body.export_format,
        title=f"Report {body.report_id}",
    )
    return {"result": result.model_dump(mode="json", by_alias=True)}


@router.get("/reports/catalog-coverage")
async def report_catalog_coverage(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    report_service: Annotated[ReportService, Depends(get_report_service)],
) -> dict:
    return {"result": report_service.catalog_coverage_summary()}


@router.post("/reports/runs", status_code=202)
async def create_report_run(
    company_id: str,
    body: ReportRunRequest,
    report_service: Annotated[ReportService, Depends(get_report_service)],
    prisma: Annotated[Prisma, Depends(get_prisma)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
    sync: bool = Query(default=False),
) -> dict:
    """Start report run. Pass ``sync=true`` to execute immediately without outbox."""

    from app.services.report_query_service import ReportQueryService

    accepted = await report_service.create_run(
        company_id=company_id,
        report_id=body.report_id,
        criteria=body.criteria,
    )
    if not sync:
        return accepted.model_dump(mode="json", by_alias=True)

    from app.core.database import get_read_prisma_client

    rows = await ReportQueryService(prisma=get_read_prisma_client()).execute(
        company_id=company_id,
        report_id=body.report_id,
        criteria=body.criteria,
    )
    await report_service.complete_run(
        company_id=company_id,
        run_id=accepted.run_id,
        rows=rows,
    )
    detail = await report_service.get_run(company_id=company_id, run_id=accepted.run_id)
    return detail.model_dump(mode="json", by_alias=True)


@router.get("/reports/runs/{run_id}")
async def get_report_run(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    run_id: str,
    report_service: Annotated[ReportService, Depends(get_report_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    """Report run status."""

    detail = await report_service.get_run(company_id=company_id, run_id=run_id)
    return detail.model_dump(mode="json", by_alias=True)


@router.post("/reports/runs/{run_id}/export")
async def export_report_run(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    run_id: str,
    body: ReportExportRequest,
    report_service: Annotated[ReportService, Depends(get_report_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    """Export stub."""

    result = await report_service.export_run(
        company_id=company_id,
        run_id=run_id,
        export_format=body.export_format,
    )
    return result.model_dump(mode="json", by_alias=True)


@router.post("/reports/runs/{run_id}/export-clickhouse")
async def export_report_run_clickhouse(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    run_id: str,
    report_service: Annotated[ReportService, Depends(get_report_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    """Push a completed report run to ClickHouse when configured (P6)."""

    from fastapi import HTTPException

    try:
        result = await report_service.export_run_to_clickhouse(
            company_id=company_id, run_id=run_id
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": result}


@router.get("/reports/subledger-tieout/ar")
async def report_ar_subledger_tieout(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    service: Annotated[SubledgerTieoutService, Depends(get_subledger_tieout_service)],
    as_of: datetime | None = Query(default=None, alias="asOf"),
) -> dict:
    """AR control account vs open invoice sub-ledger (P1.3)."""

    return {"result": await service.ar_tieout(company_id=company_id, as_of_date=as_of)}


@router.get("/reports/subledger-tieout/ap")
async def report_ap_subledger_tieout(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    service: Annotated[SubledgerTieoutService, Depends(get_subledger_tieout_service)],
    as_of: datetime | None = Query(default=None, alias="asOf"),
) -> dict:
    """AP control account vs open bill sub-ledger (P1.3)."""

    return {"result": await service.ap_tieout(company_id=company_id, as_of_date=as_of)}


@router.get("/dashboard/summary")
async def get_dashboard_summary(
    company_id: str,
    dashboard_repository: Annotated[
        DashboardRepository, Depends(get_dashboard_repository)
    ],
) -> dict:
    """
    Aggregated counts and totals for the dashboard cards (§10.9 first slice).

    Replaces the empty layout stub. Full widget catalog with AR/AP aging,
    bank cash flow charts, and P&L roll-up lands with Phase 7.5.
    """

    result = await dashboard_repository.summary(company_id=company_id)
    return {"result": result}


@router.get("/dashboard/overview")
async def get_dashboard_overview(
    company_id: str,
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
) -> dict:
    """
    Business Overview bundle — bank balances, cash flow, P&L snapshot,
    sales trend, inventory counts, AR/AP top parties (§10.9 Phase 7.5).
    """

    from app.repositories.dashboard_overview_repository import DashboardOverviewRepository

    result = await DashboardOverviewRepository(prisma).overview(company_id=company_id)
    return {"result": result}


@router.get("/dashboard/command-center")
async def get_dashboard_command_center(
    company_id: str,
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
    period: str = Query(default="fy", pattern="^(mtd|qtd|ytd|fy)$"),
    sales_granularity: str = Query(
        default="month",
        alias="salesGranularity",
        pattern="^(day|week|month)$",
    ),
) -> dict:
    """Business command center — executive KPIs, health, inventory, insights."""

    from app.repositories.command_center_repository import CommandCenterRepository

    result = await CommandCenterRepository(prisma).command_center(
        company_id=company_id,
        period=period,
        sales_granularity=sales_granularity,
    )
    return {"result": result}


@router.get("/dashboard/layout")
async def get_dashboard_layout(
    company_id: str,
    service: Annotated[AppSettingsService, Depends(get_app_settings_service)],
) -> dict:
    """Widget layout — views, grid positions, and active view."""

    settings = await service.get_dashboard_settings(company_id=company_id)
    return {"result": {**settings, "companyId": company_id}}


@router.put("/dashboard/layout")
async def put_dashboard_layout(
    company_id: str,
    body: dict,
    service: Annotated[AppSettingsService, Depends(get_app_settings_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    saved = await service.put_dashboard_settings(company_id=company_id, body=body)
    return {"result": {**saved, "companyId": company_id}}


@router.get("/attachments")
async def list_attachments(
    company_id: str,
    service: Annotated[AttachmentService, Depends(get_attachment_service)],
    entity_type: str = Query(..., alias="entityType"),
    entity_id: str = Query(..., alias="entityId"),
) -> dict:
    """Attachments for one entity."""

    rows = await service.list_attachments(
        company_id=company_id,
        entity_type=entity_type,
        entity_id=entity_id,
    )
    return {"result": _dump_rows(rows)}


@router.post("/attachments", status_code=201)
async def create_attachment(
    company_id: str,
    body: CreateAttachmentRequest,
    service: Annotated[AttachmentService, Depends(get_attachment_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    """Register attachment metadata."""

    row = await service.register_attachment(
        company_id=company_id,
        entity_type=body.entity_type,
        entity_id=body.entity_id,
        file_name=body.file_name,
        storage_key=body.storage_key,
        mime_type=body.mime_type,
        byte_size=body.byte_size,
    )
    return {"result": jsonable_encoder(row)}


@router.post("/attachments/upload", status_code=201)
async def upload_attachment(
    company_id: str,
    service: Annotated[AttachmentService, Depends(get_attachment_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
    entity_type: str = Form(..., alias="entityType"),
    entity_id: str = Form(..., alias="entityId"),
    file: UploadFile = File(...),
) -> dict:
    """Upload a file and register attachment metadata."""

    data = await file.read()
    if not data:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="Empty file")
    row = await service.upload_file(
        company_id=company_id,
        entity_type=entity_type,
        entity_id=entity_id,
        file_name=file.filename or "attachment",
        data=data,
        mime_type=file.content_type,
    )
    return {"result": jsonable_encoder(row)}


@router.get("/attachments/{attachment_id}/download")
async def download_attachment(
    company_id: str,
    attachment_id: str,
    service: Annotated[AttachmentService, Depends(get_attachment_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
):
    from fastapi import HTTPException
    from fastapi.responses import FileResponse

    row, path = await service.open_file(company_id=company_id, attachment_id=attachment_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Attachment not found")
    if path is None:
        raise HTTPException(status_code=404, detail="File missing on disk")
    return FileResponse(
        path,
        filename=row.fileName,
        media_type=row.mimeType or "application/octet-stream",
    )


@router.post("/document-numbers/next")
async def reserve_document_number(
    company_id: str,
    body: ReserveDocumentNumberRequest,
    service: Annotated[DocumentNumberService, Depends(get_document_number_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    """Reserve next sequence value."""

    value = await service.reserve_next(company_id=company_id, sequence_key=body.sequence_key)
    return {"result": {"nextNumber": value}}


@router.get("/auto-codes/{entity_key}/peek")
async def peek_auto_code(
    company_id: str,
    entity_key: str,
    auto_code_service: Annotated[AutoCodeService, Depends(get_auto_code_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    """Preview next auto-generated master code (§12.2.8)."""

    code = await auto_code_service.peek_next(company_id=company_id, entity_key=entity_key)
    enabled = await auto_code_service.is_enabled(company_id=company_id, entity_key=entity_key)
    return {"result": {"enabled": enabled, "nextCode": code}}


@router.get("/sales/last-rate")
async def sales_last_rate(
    company_id: str,
    last_rate_service: Annotated[LastRateService, Depends(get_last_rate_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("sales"))],
    customer_id: str = Query(..., alias="customerId"),
    product_code: str = Query(..., alias="productCode"),
    doc_type: str = Query("SI", alias="docType"),
    for_edit: bool = Query(True, alias="forEdit"),
) -> dict:
    """Last sold rate for customer + product when Last Rate is enabled (§12.2.7)."""

    row = await last_rate_service.sales_last_rate(
        company_id=company_id,
        customer_id=customer_id,
        product_code=product_code,
        doc_type=doc_type,
        for_edit=for_edit,
    )
    return {"result": row}


@router.get("/purchases/last-rate")
async def purchase_last_rate(
    company_id: str,
    last_rate_service: Annotated[LastRateService, Depends(get_last_rate_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("purchases"))],
    supplier_id: str = Query(..., alias="supplierId"),
    product_code: str = Query(..., alias="productCode"),
    doc_type: str = Query("VI", alias="docType"),
    for_edit: bool = Query(True, alias="forEdit"),
) -> dict:
    """Last purchase rate for supplier + product when Last Rate is enabled."""

    row = await last_rate_service.purchase_last_rate(
        company_id=company_id,
        supplier_id=supplier_id,
        product_code=product_code,
        doc_type=doc_type,
        for_edit=for_edit,
    )
    return {"result": row}


@router.get("/transaction-templates")
async def list_transaction_templates(
    company_id: str,
    repo: Annotated[TransactionTemplateRepository, Depends(get_transaction_template_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
    module: str = Query(...),
) -> dict:
    """List saved transaction templates for a module (§3.3)."""

    rows = await repo.list_for_module(company_id=company_id, module=module)
    return {"result": _dump_rows(rows)}


@router.post("/transaction-templates", status_code=201)
async def create_transaction_template(
    company_id: str,
    body: TransactionTemplateCreateRequest,
    repo: Annotated[TransactionTemplateRepository, Depends(get_transaction_template_repository)],
    claims: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    """Save a transaction template."""

    row = await repo.create(
        company_id=company_id,
        module=body.module,
        name=body.name,
        payload=body.payload,
        created_by=claims.user_id,
    )
    return {"result": jsonable_encoder(row)}


@router.get("/transaction-templates/{template_id}")
async def get_transaction_template(
    company_id: str,
    template_id: str,
    repo: Annotated[TransactionTemplateRepository, Depends(get_transaction_template_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    """Load one transaction template."""

    from fastapi import HTTPException

    row = await repo.get_by_id(company_id=company_id, template_id=template_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"result": jsonable_encoder(row)}


@router.delete("/transaction-templates/{template_id}", status_code=204)
async def delete_transaction_template(
    company_id: str,
    template_id: str,
    repo: Annotated[TransactionTemplateRepository, Depends(get_transaction_template_repository)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> Response:
    """Remove a saved template."""

    from fastapi import HTTPException

    try:
        await repo.delete(company_id=company_id, template_id=template_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return Response(status_code=204)


@router.get("/recurring-schedules")
async def list_recurring_schedules(
    company_id: str,
    repo: Annotated[RecurringScheduleRepository, Depends(get_recurring_schedule_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    """List recurring document schedules (§3.3)."""

    rows = await repo.list_for_company(company_id=company_id)
    return {"result": _dump_rows(rows)}


@router.post("/recurring-schedules", status_code=201)
async def create_recurring_schedule(
    company_id: str,
    body: RecurringScheduleCreateRequest,
    repo: Annotated[RecurringScheduleRepository, Depends(get_recurring_schedule_repository)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    row = await repo.create(
        company_id=company_id,
        name=body.name,
        module=body.module,
        frequency=body.frequency,
        interval=body.interval,
        next_run_date=body.next_run_date,
        end_date=body.end_date,
        is_active=body.is_active,
        payload=body.payload,
    )
    return {"result": jsonable_encoder(row)}


@router.patch("/recurring-schedules/{schedule_id}")
async def update_recurring_schedule(
    company_id: str,
    schedule_id: str,
    body: RecurringScheduleUpdateRequest,
    repo: Annotated[RecurringScheduleRepository, Depends(get_recurring_schedule_repository)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    from fastapi import HTTPException

    data = body.model_dump(exclude_unset=True, by_alias=False)
    alias_map = {
        "next_run_date": "nextRunDate",
        "end_date": "endDate",
        "is_active": "isActive",
    }
    prisma_data = {alias_map.get(k, k): v for k, v in data.items()}
    try:
        row = await repo.update(
            company_id=company_id, schedule_id=schedule_id, data=prisma_data
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"result": jsonable_encoder(row)}


@router.delete("/recurring-schedules/{schedule_id}", status_code=204)
async def delete_recurring_schedule(
    company_id: str,
    schedule_id: str,
    repo: Annotated[RecurringScheduleRepository, Depends(get_recurring_schedule_repository)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> Response:
    from fastapi import HTTPException

    try:
        await repo.delete(company_id=company_id, schedule_id=schedule_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return Response(status_code=204)


@router.post("/recurring-schedules/run-due")
async def run_due_recurring_schedules(
    company_id: str,
    service: Annotated[RecurringScheduleService, Depends(get_recurring_schedule_service)],
    prisma: Annotated[Prisma, Depends(get_prisma)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    """Execute all due recurring schedules (manual / cron trigger)."""

    result = await service.run_due(company_id=company_id, prisma=prisma)
    return {"result": result}


@router.get("/import-jobs")
async def list_import_jobs(
    company_id: str,
    service: Annotated[ImportJobService, Depends(get_import_job_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    """Import jobs."""

    rows = await service.list_jobs(company_id=company_id)
    return {"result": _dump_rows(rows)}


@router.post("/import-jobs", status_code=202)
async def create_import_job(
    company_id: str,
    body: CreateImportJobRequest,
    service: Annotated[ImportJobService, Depends(get_import_job_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    """Enqueue import."""

    extra: dict = {}
    if body.post_gl:
        extra["postGl"] = True
    row = await service.enqueue(
        company_id=company_id,
        job_type=body.job_type,
        file_name=body.file_name,
        rows=body.rows or None,
        extra_payload=extra or None,
    )
    return {"result": jsonable_encoder(row)}


@router.post("/import-jobs/upload", status_code=202)
async def upload_import_job(
    company_id: str,
    service: Annotated[ImportJobService, Depends(get_import_job_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
    job_type: str = Query(..., alias="jobType"),
    post_gl: bool = Query(False, alias="postGl"),
    file: UploadFile = File(...),
) -> dict:
    """Enqueue import from Excel (.xlsx) or CSV upload."""

    from fastapi import HTTPException

    content = await file.read()
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename required")
    try:
        row = await service.enqueue_from_file(
            company_id=company_id,
            job_type=job_type,
            filename=file.filename,
            content=content,
            post_gl=post_gl,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(row)}


@router.post("/bank-statement-import", status_code=201)
async def import_bank_statement(
    company_id: str,
    service: Annotated[BankReconciliationService, Depends(get_bank_reconciliation_service)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    claims: Annotated[JwtClaims, Depends(require_permission("bank.reconciliation.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("bank"))],
    bank_account_id: str = Form(..., alias="bankAccountId"),
    statement_date: str = Form(..., alias="statementDate"),
    statement_balance: str | None = Form(default=None, alias="statementBalance"),
    file: UploadFile = File(...),
) -> dict:
    """Import a bank statement CSV/XLSX and open reconciliation (catalog §4.5a)."""

    from fastapi import HTTPException

    from app.domain.document_workflow import SOURCE_BANK_RECONCILIATION

    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename required")
    content = await file.read()
    try:
        parsed = parse_upload(filename=file.filename, content=content)
        stmt_dt = _parse_datetime(statement_date)
        if stmt_dt is None:
            raise ValidationAppError("Invalid statementDate")
        balance = Decimal(statement_balance) if statement_balance else None
        session = await service.import_statement(
            company_id=company_id,
            bank_account_id=bank_account_id,
            statement_date=stmt_dt,
            statement_balance=balance,
            rows=parsed,
            notes=f"Statement import: {file.filename}",
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    session_id = getattr(session, "id", None)
    await audit_service.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type=SOURCE_BANK_RECONCILIATION,
        transaction_id=str(session_id) if session_id else None,
        status="open",
        details=f"statementImport bankAccountId={bank_account_id} file={file.filename}",
    )
    return {"result": jsonable_encoder(session)}


@router.post("/platform/process-outbox")
async def process_outbox(
    company_id: str,
    worker: Annotated[OutboxWorkerService, Depends(get_outbox_worker_service)],
    _claims: Annotated[Any, Depends(require_permission("settings.platform.process"))],
    limit: int = Query(default=20, ge=1, le=100),
) -> dict:
    """Process pending async jobs (imports, report runs). Admin/operators."""

    stats = await worker.process_batch(limit=limit)
    return {"result": stats}


@router.get("/bank-reconciliations")
async def list_bank_reconciliations(
    company_id: str,
    service: Annotated[BankReconciliationService, Depends(get_bank_reconciliation_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("bank"))],
    bank_account_id: str | None = Query(default=None, alias="bankAccountId"),
) -> dict:
    rows = await service.list_sessions(
        company_id=company_id, bank_account_id=bank_account_id
    )
    return {"result": _dump_rows(rows)}


@router.post("/bank-reconciliations", status_code=201)
async def start_bank_reconciliation(
    company_id: str,
    body: BankReconciliationStartRequest,
    service: Annotated[BankReconciliationService, Depends(get_bank_reconciliation_service)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    claims: Annotated[JwtClaims, Depends(require_permission("bank.reconciliation.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("bank"))],
) -> dict:
    from fastapi import HTTPException

    from app.domain.document_workflow import SOURCE_BANK_RECONCILIATION

    try:
        session = await service.start_reconciliation(
            company_id=company_id,
            bank_account_id=body.bank_account_id,
            statement_date=body.statement_date,
            statement_balance=body.statement_balance,
            notes=body.notes,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    session_id = getattr(session, "id", None) or (
        session.get("id") if isinstance(session, dict) else None
    )
    await audit_service.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type=SOURCE_BANK_RECONCILIATION,
        transaction_id=str(session_id) if session_id else None,
        status="open",
        details=(
            f"bankAccountId={body.bank_account_id} "
            f"balance={body.statement_balance}"
        ),
    )
    return {"result": jsonable_encoder(session)}


@router.get("/bank-reconciliations/{reconciliation_id}")
async def get_bank_reconciliation(
    company_id: str,
    reconciliation_id: str,
    service: Annotated[BankReconciliationService, Depends(get_bank_reconciliation_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("bank"))],
) -> dict:
    from fastapi import HTTPException

    row = await service.get_session(
        company_id=company_id, reconciliation_id=reconciliation_id
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Reconciliation not found")
    return {"result": jsonable_encoder(row)}


@router.post("/bank-reconciliations/{reconciliation_id}/clear-items")
async def clear_bank_reconciliation_items(
    company_id: str,
    reconciliation_id: str,
    body: BankReconciliationClearRequest,
    service: Annotated[BankReconciliationService, Depends(get_bank_reconciliation_service)],
    _claims: Annotated[Any, Depends(require_permission("bank.reconciliation.update"))],
) -> dict:
    from fastapi import HTTPException

    try:
        session = await service.update_cleared_items(
            company_id=company_id,
            reconciliation_id=reconciliation_id,
            item_ids=body.item_ids,
            cleared=body.cleared,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(session)}


@router.post("/bank-reconciliations/{reconciliation_id}/auto-match")
async def auto_match_bank_reconciliation(
    company_id: str,
    reconciliation_id: str,
    service: Annotated[BankReconciliationService, Depends(get_bank_reconciliation_service)],
    _claims: Annotated[Any, Depends(require_permission("bank.reconciliation.update"))],
) -> dict:
    from fastapi import HTTPException

    try:
        session = await service.auto_match_items(
            company_id=company_id, reconciliation_id=reconciliation_id
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(session)}


@router.post("/bank-reconciliations/{reconciliation_id}/complete")
async def complete_bank_reconciliation(
    company_id: str,
    reconciliation_id: str,
    service: Annotated[BankReconciliationService, Depends(get_bank_reconciliation_service)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    claims: Annotated[JwtClaims, Depends(require_permission("bank.reconciliation.complete"))],
) -> dict:
    from fastapi import HTTPException

    from app.domain.document_workflow import SOURCE_BANK_RECONCILIATION

    try:
        result = await service.complete_reconciliation(
            company_id=company_id, reconciliation_id=reconciliation_id
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    await audit_service.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type=SOURCE_BANK_RECONCILIATION,
        transaction_id=reconciliation_id,
        status="completed",
        details="reconciliation completed",
    )
    return {"result": jsonable_encoder(result)}


@router.get("/audit-log/rbac-types")
async def list_rbac_audit_types(
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    """Transaction types for RBAC / users & roles filter — P31."""

    from app.constants.rbac_audit_types import RBAC_AUDIT_TYPES_SORTED

    return {"result": list(RBAC_AUDIT_TYPES_SORTED)}


@router.get("/audit-log/transaction-types")
async def list_audit_transaction_types(
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    """Grouped transaction types for User Log filter (FA §12.15)."""

    from app.constants.audit_transaction_types import audit_transaction_type_groups

    return {"result": audit_transaction_type_groups()}


@router.get("/audit-log/export")
async def export_audit_log_csv(
    company_id: str,
    service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
    user_id: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    transaction_type: str | None = Query(None, alias="transactionType"),
    transaction_id: str | None = Query(None, alias="transactionId"),
    type_contains: str | None = Query(None, alias="typeContains"),
    rbac_only: bool = Query(False, alias="rbacOnly"),
) -> Response:
    """Download user log as CSV — P32."""

    from app.constants.rbac_audit_types import RBAC_AUDIT_TYPES

    types_filter: list[str] | None = None
    contains_filter: str | None = None
    if rbac_only:
        types_filter = sorted(RBAC_AUDIT_TYPES)
    elif transaction_type:
        types_filter = [transaction_type.strip()]
    elif type_contains:
        contains_filter = type_contains.strip()
    rows = await service.list_entries(
        company_id=company_id,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
        transaction_types=types_filter,
        transaction_type_contains=contains_filter,
        transaction_id=transaction_id,
        take=5000,
    )
    csv_text = audit_log_entries_to_csv(rows)
    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="audit-log.csv"'},
    )


@router.get("/audit-log")
async def list_audit_log(
    company_id: str,
    service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
    user_id: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    transaction_type: str | None = Query(None, alias="transactionType"),
    transaction_id: str | None = Query(None, alias="transactionId"),
    type_contains: str | None = Query(None, alias="typeContains"),
    rbac_only: bool = Query(False, alias="rbacOnly"),
) -> dict:
    """User log with optional RBAC transaction filter — P31."""

    from app.constants.rbac_audit_types import RBAC_AUDIT_TYPES

    types_filter: list[str] | None = None
    contains_filter: str | None = None
    if rbac_only:
        types_filter = sorted(RBAC_AUDIT_TYPES)
    elif transaction_type:
        types_filter = [transaction_type.strip()]
    elif type_contains:
        contains_filter = type_contains.strip()
    rows = await service.list_entries(
        company_id=company_id,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
        transaction_types=types_filter,
        transaction_type_contains=contains_filter,
        transaction_id=transaction_id,
    )
    return {"result": _dump_rows(rows)}


@router.get("/approval-policies")
async def list_approval_policies(
    company_id: str,
    service: Annotated[ApprovalPolicyService, Depends(get_approval_policy_service)],
) -> dict:
    """Approval policies."""

    rows = await service.list_policies(company_id=company_id)
    return {"result": _dump_rows(rows)}


@router.put("/approval-policies")
async def put_approval_policy(
    company_id: str,
    body: UpsertApprovalPolicyRequest,
    service: Annotated[ApprovalPolicyService, Depends(get_approval_policy_service)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    claims: Annotated[JwtClaims, Depends(resolve_tenant)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    """Upsert one policy."""

    import json

    before_rows = await service.list_policies(company_id=company_id)
    before = next(
        (p for p in before_rows if p.entityType == body.entity_type),
        None,
    )
    row = await service.upsert_policy(
        company_id=company_id,
        entity_type=body.entity_type,
        rules=body.rules,
    )
    await audit_service.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type="APPROVAL_POLICY_CHANGE",
        transaction_id=row.id,
        status="ok",
        details=json.dumps(
            {
                "entityType": body.entity_type,
                "before": before.rules if before is not None else None,
                "after": body.rules,
            }
        ),
    )
    return {"result": jsonable_encoder(row)}


@router.get("/approval-requests")
async def list_approval_requests(
    company_id: str,
    service: Annotated[ApprovalEngineService, Depends(get_approval_engine_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
    status: str | None = Query(default=None),
) -> dict:
    rows = await service.list_requests(company_id=company_id, status=status)
    return {"result": _dump_rows(rows)}


@router.post("/approval-requests", status_code=201)
async def create_approval_request(
    company_id: str,
    body: ApprovalRequestCreate,
    service: Annotated[ApprovalEngineService, Depends(get_approval_engine_service)],
    claims: Annotated[JwtClaims, Depends(resolve_tenant)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    from fastapi import HTTPException

    try:
        row = await service.submit_request(
            company_id=company_id,
            entity_type=body.entity_type,
            entity_id=body.entity_id,
            amount=body.amount,
            requested_by_id=claims.user_id,
            notes=body.notes,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(row)}


@router.post("/approval-requests/{request_id}/approve")
async def approve_approval_request(
    company_id: str,
    request_id: str,
    service: Annotated[ApprovalEngineService, Depends(get_approval_engine_service)],
    claims: Annotated[JwtClaims, Depends(resolve_tenant)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    from fastapi import HTTPException

    try:
        pending = await service.get_request(
            company_id=company_id, request_id=request_id
        )
        if pending is not None:
            await service.assert_can_approve(
                company_id=company_id,
                user_id=claims.user_id,
                entity_type=pending.entityType,
                amount=Decimal(str(pending.amount)),
            )
        row = await service.approve_request(
            company_id=company_id,
            request_id=request_id,
            approved_by_id=claims.user_id,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(row)}


@router.post("/approval-requests/{request_id}/reject")
async def reject_approval_request(
    company_id: str,
    request_id: str,
    service: Annotated[ApprovalEngineService, Depends(get_approval_engine_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    from fastapi import HTTPException

    try:
        row = await service.reject_request(
            company_id=company_id, request_id=request_id
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(row)}


@router.get("/reports/grni")
async def report_grni(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    service: Annotated[GrniService, Depends(get_grni_service)],
) -> dict:
    rows = await service.report(company_id=company_id)
    return {"result": rows}


# =================== P4 — Assembly ===================


@router.get("/assembly/templates")
async def list_assembly_templates(
    company_id: str,
    service: Annotated[AssemblyService, Depends(get_assembly_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("assembly"))],
) -> dict:
    rows = await service.list_templates(company_id=company_id)
    return {"result": _dump_rows(rows)}


@router.post("/assembly/templates", status_code=201)
async def create_assembly_template(
    company_id: str,
    body: AssemblyTemplateCreateRequest,
    service: Annotated[AssemblyService, Depends(get_assembly_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("assembly"))],
) -> dict:
    lines = [
        {
            "componentProductCode": line.component_product_code,
            "quantity": line.quantity,
        }
        for line in body.lines
    ]
    row = await service.create_template(
        company_id=company_id,
        code=body.code,
        name=body.name,
        finished_product_code=body.finished_product_code,
        lines=lines,
    )
    return {"result": jsonable_encoder(row)}


@router.get("/assembly/jobs")
async def list_assembly_jobs(
    company_id: str,
    service: Annotated[AssemblyService, Depends(get_assembly_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("assembly"))],
) -> dict:
    rows = await service.list_jobs(company_id=company_id)
    return {"result": _dump_rows(rows)}


@router.post("/assembly/jobs", status_code=201)
async def create_assembly_job(
    company_id: str,
    body: AssemblyJobCreateRequest,
    service: Annotated[AssemblyService, Depends(get_assembly_service)],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("assembly"))],
) -> dict:
    await lock_date_service.assert_not_locked(
        company_id=company_id,
        document_date=body.job_date,
        document_label="assembly job",
    )
    row = await service.create_job_from_template(
        company_id=company_id,
        template_id=body.template_id,
        job_date=body.job_date,
        quantity=body.quantity,
        batch_number=body.batch_number,
        expiry_date=body.expiry_date,
    )
    return {"result": jsonable_encoder(row)}


@router.post("/assembly/jobs/{job_id}/finish")
async def finish_assembly_job(
    company_id: str,
    job_id: str,
    service: Annotated[AssemblyService, Depends(get_assembly_service)],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    claims: Annotated[JwtClaims, Depends(resolve_tenant)],
    _access: Annotated[JwtClaims, Depends(require_module_access("assembly"))],
) -> dict:
    from fastapi import HTTPException

    job = await service.get_job(company_id=company_id, job_id=job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    await lock_date_service.assert_not_locked(
        company_id=company_id,
        document_date=job.jobDate,
        document_label="assembly job",
        user_id=claims.user_id,
    )
    try:
        row = await service.finish_job(company_id=company_id, job_id=job_id)
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(row), "posted": True}


# =================== P4 — FX revaluation ===================


@router.get("/bank/fx-revaluations")
async def list_fx_revaluations(
    company_id: str,
    service: Annotated[FxRevaluationService, Depends(get_fx_revaluation_service)],
) -> dict:
    rows = await service.list_runs(company_id=company_id)
    return {"result": _dump_rows(rows)}


@router.post("/bank/fx-revaluations", status_code=201)
async def create_fx_revaluation(
    company_id: str,
    body: FxRevaluationRequest,
    service: Annotated[FxRevaluationService, Depends(get_fx_revaluation_service)],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    claims: Annotated[JwtClaims, Depends(resolve_tenant)],
    _access: Annotated[JwtClaims, Depends(require_module_access("bank"))],
) -> dict:
    from fastapi import HTTPException

    await lock_date_service.assert_not_locked(
        company_id=company_id,
        document_date=body.revaluation_date,
        document_label="FX revaluation",
        user_id=claims.user_id,
    )
    try:
        row = await service.run_revaluation(
            company_id=company_id,
            bank_account_id=body.bank_account_id,
            revaluation_date=body.revaluation_date,
            foreign_balance=body.foreign_balance,
            exchange_rate=body.exchange_rate,
            book_balance_base=body.book_balance_base,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(row), "posted": True}


# =================== Projects & locations ===================


@router.get("/projects")
async def list_projects(
    company_id: str,
    repo: Annotated[ProjectRepository, Depends(get_project_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    rows = await repo.list_projects(company_id=company_id)
    return {"result": _dump_rows(rows)}


@router.post("/projects", status_code=201)
async def create_project(
    company_id: str,
    body: CreateProjectRequest,
    repo: Annotated[ProjectRepository, Depends(get_project_repository)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    row = await repo.create_project(company_id=company_id, code=body.code, name=body.name)
    return {"result": jsonable_encoder(row)}


@router.patch("/projects/{project_id}")
async def update_project(
    company_id: str,
    project_id: str,
    body: UpdateProjectRequest,
    repo: Annotated[ProjectRepository, Depends(get_project_repository)],
    _access: Annotated[JwtClaims, Depends(require_module_access("financial"))],
) -> dict:
    from fastapi import HTTPException

    row = await repo.update_project(
        company_id=company_id,
        project_id=project_id,
        name=body.name,
        is_active=body.is_active,
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"result": jsonable_encoder(row)}


@router.get("/locations")
async def list_locations(
    company_id: str,
    repo: Annotated[LocationRepository, Depends(get_location_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("inventory"))],
) -> dict:
    rows = await repo.list_locations(company_id=company_id)
    return {"result": _dump_rows(rows)}


@router.post("/locations", status_code=201)
async def create_location(
    company_id: str,
    body: CreateLocationRequest,
    repo: Annotated[LocationRepository, Depends(get_location_repository)],
    _access: Annotated[JwtClaims, Depends(require_module_access("inventory"))],
) -> dict:
    row = await repo.create_location(
        company_id=company_id,
        code=body.code,
        name=body.name,
        is_main=body.is_main,
    )
    return {"result": jsonable_encoder(row)}


@router.patch("/locations/{location_id}")
async def update_location(
    company_id: str,
    location_id: str,
    body: UpdateLocationRequest,
    repo: Annotated[LocationRepository, Depends(get_location_repository)],
    _access: Annotated[JwtClaims, Depends(require_module_access("inventory"))],
) -> dict:
    from fastapi import HTTPException

    row = await repo.update_location(
        company_id=company_id,
        location_id=location_id,
        name=body.name,
        is_main=body.is_main,
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return {"result": jsonable_encoder(row)}


# =================== Integrations readiness ===================


@router.get("/integrations/readiness")
async def get_integrations_readiness(
    company_id: str,
    fbr_repo: Annotated[Any, Depends(get_fbr_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    """FBR/PayPro/Kuickpay configuration flags and FBR queue counts (no secrets)."""

    from app.core.config import get_settings
    from app.services.integrations_readiness_service import build_integrations_readiness

    settings = get_settings()
    errors = await fbr_repo.list_errors(company_id=company_id)
    due = await fbr_repo.list_due_retries(company_id=company_id)
    payload = build_integrations_readiness(
        settings,
        fbr_error_count=len(errors),
        fbr_due_retry_count=len(due),
    )
    return {"result": payload}


# =================== P4 — FBR digital invoicing (stub) ===================


@router.get("/sales-invoices/{invoice_id}/fbr")
async def get_fbr_submission(
    company_id: str,
    invoice_id: str,
    service: Annotated[FbrService, Depends(get_fbr_service)],
) -> dict:
    row = await service.get_status(company_id=company_id, sales_invoice_id=invoice_id)
    return {"result": jsonable_encoder(row) if row else None}


@router.post("/sales-invoices/{invoice_id}/fbr/submit")
async def submit_fbr_invoice(
    company_id: str,
    invoice_id: str,
    service: Annotated[FbrService, Depends(get_fbr_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("fbr"))],
) -> dict:
    from fastapi import HTTPException

    try:
        out = await service.submit_invoice(
            company_id=company_id, sales_invoice_id=invoice_id
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(out)}


@router.post("/sales-invoices/{invoice_id}/fbr/poll")
async def poll_fbr_invoice(
    company_id: str,
    invoice_id: str,
    service: Annotated[FbrService, Depends(get_fbr_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("fbr"))],
) -> dict:
    from fastapi import HTTPException

    try:
        out = await service.poll_status(
            company_id=company_id, sales_invoice_id=invoice_id
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(out)}


@router.get("/fbr/submissions/errors")
async def list_fbr_errors(
    company_id: str,
    service: Annotated[FbrService, Depends(get_fbr_service)],
) -> dict:
    rows = await service.list_errors(company_id=company_id)
    return {"result": jsonable_encoder(rows)}


@router.post("/sales-invoices/{invoice_id}/fbr/retry")
async def retry_fbr_invoice(
    company_id: str,
    invoice_id: str,
    service: Annotated[FbrService, Depends(get_fbr_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("fbr"))],
) -> dict:
    from fastapi import HTTPException

    try:
        out = await service.retry_invoice(
            company_id=company_id, sales_invoice_id=invoice_id
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(out)}


@router.post("/fbr/retry-pending")
async def enqueue_fbr_retries(
    company_id: str,
    service: Annotated[FbrService, Depends(get_fbr_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("fbr"))],
) -> dict:
    count = await service.enqueue_due_retries(company_id=company_id)
    return {"result": {"queued": count}}


# =================== P5 — PayPro online payments (stub) ===================


@router.get("/payments/paypro/transactions")
async def list_paypro_transactions(
    company_id: str,
    service: Annotated[PayproService, Depends(get_paypro_service)],
) -> dict:
    rows = await service.list_transactions(company_id=company_id)
    return {"result": jsonable_encoder(rows)}


@router.post("/payments/paypro/initiate")
async def initiate_paypro_payment(
    company_id: str,
    body: PayproInitiateRequest,
    service: Annotated[PayproService, Depends(get_paypro_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("payments"))],
) -> dict:
    from fastapi import HTTPException

    try:
        out = await service.initiate_payment(
            company_id=company_id,
            customer_id=body.customer_id,
            amount=body.amount,
            bank_account_id=body.bank_account_id,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(out)}


@router.post("/payments/paypro/webhook")
async def paypro_webhook(
    company_id: str,
    request: Request,
    body: PayproWebhookRequest,
    service: Annotated[PayproService, Depends(get_paypro_service)],
    security_audit: Annotated[SecurityAuditService, Depends(get_security_audit_service)],
    x_paypro_signature: Annotated[str | None, Header(alias="X-Paypro-Signature")] = None,
) -> dict:
    from fastapi import HTTPException

    from app.core.rate_limit import check_rate_limit
    from app.core.webhook_guard import assert_webhook_ip_allowed
    from app.services.allocation_service import AllocationLine

    try:
        check_rate_limit(request, group="webhook")
        assert_webhook_ip_allowed(request=request, provider="paypro")
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    raw = await request.body()
    if not service.verify_webhook_signature(
        body=raw,
        signature=x_paypro_signature,
    ):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    explicit = None
    if body.allocations:
        explicit = [
            AllocationLine(document_id=line.invoice_id, amount=line.amount)
            for line in body.allocations
        ]
    try:
        row = await service.settle_webhook(
            company_id=company_id,
            merchant_ref=body.merchant_ref,
            payload=body.model_dump(by_alias=True),
            auto_fifo=body.auto_fifo,
            explicit_allocations=explicit,
        )
        await security_audit.record(
            company_id=company_id,
            event_type="paypro.webhook",
            resource_id=body.merchant_ref,
            status="settled",
            details=f"receipt={row.salesReceiptId}",
        )
    except ValidationAppError as exc:
        await security_audit.record(
            company_id=company_id,
            event_type="paypro.webhook",
            resource_id=body.merchant_ref,
            status="error",
            details=str(exc),
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(row)}


# =================== P7 — Kuickpay online payments ===================


@router.get("/payments/kuickpay/transactions")
async def list_kuickpay_transactions(
    company_id: str,
    service: Annotated[KuickpayService, Depends(get_kuickpay_service)],
) -> dict:
    rows = await service.list_transactions(company_id=company_id)
    return {"result": jsonable_encoder(rows)}


@router.post("/payments/kuickpay/initiate")
async def initiate_kuickpay_payment(
    company_id: str,
    body: PayproInitiateRequest,
    service: Annotated[KuickpayService, Depends(get_kuickpay_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("payments"))],
) -> dict:
    from fastapi import HTTPException

    try:
        out = await service.initiate_payment(
            company_id=company_id,
            customer_id=body.customer_id,
            amount=body.amount,
            bank_account_id=body.bank_account_id,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(out)}


@router.post("/payments/kuickpay/webhook")
async def kuickpay_webhook(
    company_id: str,
    request: Request,
    body: PayproWebhookRequest,
    service: Annotated[KuickpayService, Depends(get_kuickpay_service)],
    security_audit: Annotated[SecurityAuditService, Depends(get_security_audit_service)],
    x_kuickpay_signature: Annotated[str | None, Header(alias="X-Kuickpay-Signature")] = None,
) -> dict:
    from fastapi import HTTPException

    from app.core.rate_limit import check_rate_limit
    from app.core.webhook_guard import assert_webhook_ip_allowed
    from app.services.allocation_service import AllocationLine

    try:
        check_rate_limit(request, group="webhook")
        assert_webhook_ip_allowed(request=request, provider="kuickpay")
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    raw = await request.body()
    if not service.verify_webhook_signature(body=raw, signature=x_kuickpay_signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    explicit = None
    if body.allocations:
        explicit = [
            AllocationLine(document_id=line.invoice_id, amount=line.amount)
            for line in body.allocations
        ]
    try:
        row = await service.settle_webhook(
            company_id=company_id,
            merchant_ref=body.merchant_ref,
            payload=body.model_dump(by_alias=True),
            auto_fifo=body.auto_fifo,
            explicit_allocations=explicit,
        )
        await security_audit.record(
            company_id=company_id,
            event_type="kuickpay.webhook",
            resource_id=body.merchant_ref,
            status="settled",
        )
    except ValidationAppError as exc:
        await security_audit.record(
            company_id=company_id,
            event_type="kuickpay.webhook",
            resource_id=body.merchant_ref,
            status="error",
            details=str(exc),
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(row)}


@router.post("/platform/clickhouse/ensure-schema")
async def ensure_clickhouse_schema(
    company_id: str,
    schema_service: Annotated[ClickHouseSchemaService, Depends(get_clickhouse_schema_service)],
    _claims: Annotated[Any, Depends(require_permission("settings.platform.process"))],
) -> dict:
    result = await schema_service.ensure_schema()
    return {"result": result}


@router.post("/platform/clickhouse/sync-recent-runs")
async def sync_recent_runs_to_clickhouse(
    company_id: str,
    report_service: Annotated[ReportService, Depends(get_report_service)],
    prisma: Annotated[Prisma, Depends(get_prisma)],
    _claims: Annotated[Any, Depends(require_permission("settings.platform.process"))],
) -> dict:
    """Re-export completed report runs from the last 7 days (P7)."""

    from datetime import datetime, timedelta, timezone

    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    runs = await prisma.reportrun.find_many(
        where={
            "companyId": company_id,
            "status": "completed",
            "completedAt": {"gte": cutoff},
        },
        take=100,
    )
    synced = 0
    for run in runs:
        await report_service.export_run_to_clickhouse(
            company_id=company_id, run_id=run.id
        )
        synced += 1
    return {"result": {"synced": synced}}


@router.post("/users/bulk-assign-role")
async def bulk_assign_user_role(
    company_id: str,
    body: BulkAssignRoleRequest,
    membership_repo: Annotated[MembershipRepository, Depends(get_membership_repository)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    claims: Annotated[JwtClaims, Depends(require_permission("settings.roles.manage"))],
) -> dict:
    """Assign one role to multiple users — P35."""

    out = await membership_repo.bulk_assign_role(
        company_id=company_id,
        user_ids=body.user_ids,
        role_id=body.role_id,
        acting_user_id=claims.user_id,
    )
    await audit_service.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type="USER_BULK_ASSIGN_ROLE",
        transaction_id=body.role_id,
        status="ok",
        details=f"ok={len(out['succeeded'])} fail={len(out['failed'])}",
    )
    return {"result": out}


@router.post("/users/bulk-revoke")
async def bulk_revoke_users(
    company_id: str,
    body: BulkUserIdsRequest,
    membership_repo: Annotated[MembershipRepository, Depends(get_membership_repository)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    claims: Annotated[JwtClaims, Depends(require_permission("settings.users.invite"))],
) -> dict:
    """Remove multiple users from the company — P35."""

    out = await membership_repo.bulk_revoke_membership(
        company_id=company_id,
        user_ids=body.user_ids,
        acting_user_id=claims.user_id,
    )
    await audit_service.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type="USER_BULK_REVOKE",
        transaction_id=None,
        status="ok",
        details=f"ok={len(out['succeeded'])} fail={len(out['failed'])}",
    )
    return {"result": out}


@router.get("/users")
async def list_users(
    company_id: str,
    repo: Annotated[MembershipRepository, Depends(get_membership_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100, alias="pageSize"),
    q: str | None = Query(None, description="Search email or name"),
    is_active: bool | None = Query(None, alias="isActive"),
    role_id: str | None = Query(None, alias="roleId"),
    user_id: str | None = Query(None, alias="userId"),
) -> dict:
    """Company members with role names (paginated, filterable) — P33/P34/P39."""

    return {
        "result": await repo.list_members(
            company_id=company_id,
            page=page,
            page_size=page_size,
            search=q,
            is_active=is_active,
            role_id=role_id,
            user_id=user_id,
        )
    }


@router.get("/users/lookup")
async def lookup_user_by_email(
    company_id: str,
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
    email: str = Query(..., min_length=3),
) -> dict:
    """Resolve a global user id by email for reinvite UI — P41."""

    from fastapi import HTTPException

    normalized = email.strip().lower()
    user = await user_repo.find_by_email(email=normalized)
    if user is None:
        raise HTTPException(status_code=404, detail="No user with this email")
    return {
        "result": {
            "userId": user.id,
            "email": user.email,
            "firstName": user.firstName,
            "lastName": user.lastName,
            "isActive": user.isActive,
        }
    }


@router.post("/users/reinvite", status_code=201)
async def reinvite_user_by_email(
    company_id: str,
    body: ReinviteByEmailRequest,
    membership_repo: Annotated[MembershipRepository, Depends(get_membership_repository)],
    invite_service: Annotated[UserInviteService, Depends(get_user_invite_service)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    billing: Annotated[SubscriptionBillingService, Depends(get_subscription_billing_service)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    claims: Annotated[JwtClaims, Depends(require_permission("settings.users.invite"))],
) -> dict:
    """Re-add a revoked user by email (server resolves user id) — P42."""

    from fastapi import HTTPException

    try:
        await billing.assert_can_add_member(company_id=company_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    user = await user_repo.find_by_email(email=body.email.strip().lower())
    if user is None:
        raise HTTPException(status_code=404, detail="No user with this email")
    try:
        row = await membership_repo.reinvite_member(
            company_id=company_id,
            user_id=user.id,
            role_id=body.role_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    invite_email_sent = await invite_service.send_setup_email_if_needed(
        company_id=company_id,
        user_id=row["userId"],
        email=row["email"],
        user_created=False,
    )
    await audit_service.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type="USER_REINVITE",
        transaction_id=user.id,
        status="ok",
        details=f"email={row['email']} roleId={body.role_id} emailSent={invite_email_sent}",
    )
    return {"result": {**row, "inviteEmailSent": invite_email_sent}}


@router.get("/roles")
async def list_roles(
    company_id: str,
    repo: Annotated[MembershipRepository, Depends(get_membership_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    """Roles with permission codes — Sprint 9."""

    rows = await repo.list_roles(company_id=company_id)
    return {"result": rows}


@router.get("/roles/export")
async def export_roles(
    company_id: str,
    repo: Annotated[RoleRepository, Depends(get_role_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
    strip_ids: bool = Query(False, alias="stripIds"),
) -> dict:
    """Export all roles and permissions for backup — P29."""

    rows = await repo.list_roles_for_export(company_id=company_id)
    if strip_ids:
        rows = [{"name": r["name"], "permissions": r["permissions"]} for r in rows]
    return {
        "result": {
            "exportedAt": datetime.now(tz=UTC).isoformat(),
            "roles": rows,
            "namesOnly": strip_ids,
        }
    }


@router.post("/roles/clone-batch", status_code=201)
async def clone_roles_batch(
    company_id: str,
    body: RoleCloneBatchRequest,
    repo: Annotated[RoleRepository, Depends(get_role_repository)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    claims: Annotated[JwtClaims, Depends(require_permission("settings.roles.manage"))],
    strict: bool = Query(False, description="Reject batch when any source has unknown permission codes"),
) -> dict:
    from fastapi import HTTPException

    all_unknown: list[str] = []
    for role_id in body.role_ids:
        source = await repo.get_role(company_id=company_id, role_id=role_id)
        if source is None:
            raise HTTPException(status_code=404, detail=f"Role not found: {role_id}")
        perms = source.permissions if isinstance(source.permissions, list) else []
        validation = validate_role_permissions([str(p) for p in perms])
        all_unknown.extend(validation["unknownPermissions"])
    if strict and all_unknown:
        unique = sorted(set(all_unknown))
        raise HTTPException(
            status_code=400,
            detail=f"Unknown permission codes: {', '.join(unique)}",
        )
    try:
        rows = await repo.clone_roles_batch(
            company_id=company_id,
            role_ids=body.role_ids,
            name_suffix=body.name_suffix,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    result = [
        {
            "id": r.id,
            "name": r.name,
            "permissions": r.permissions if isinstance(r.permissions, list) else [],
        }
        for r in rows
    ]
    await audit_service.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type="ROLE_CLONE_BATCH",
        transaction_id=None,
        status="ok",
        details=f"count={len(result)} sourceIds={','.join(body.role_ids)}",
    )
    return {"result": result}


@router.post("/roles/import/jobs", status_code=202)
async def enqueue_role_import_job(
    company_id: str,
    import_service: Annotated[ImportJobService, Depends(get_import_job_service)],
    _claims: Annotated[JwtClaims, Depends(require_permission("settings.roles.manage"))],
    file: UploadFile = File(...),
    skip_existing: bool = Query(True, alias="skipExisting"),
) -> dict:
    """Queue background role import for large files — P33."""

    from fastapi import HTTPException

    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename required")
    content = await file.read()
    try:
        job = await import_service.enqueue_role_import_file(
            company_id=company_id,
            filename=file.filename,
            content=content,
            skip_existing=skip_existing,
            requested_by_user_id=claims.user_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(job)}


@router.get("/roles/import/jobs/{job_id}")
async def get_role_import_job(
    company_id: str,
    job_id: str,
    import_service: Annotated[ImportJobService, Depends(get_import_job_service)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    from fastapi import HTTPException

    job = await import_service.get_job(company_id=company_id, job_id=job_id)
    if job is None or job.jobType != "roles":
        raise HTTPException(status_code=404, detail="Role import job not found")
    return {"result": jsonable_encoder(job)}


@router.post("/roles/import/upload")
async def upload_import_roles(
    company_id: str,
    repo: Annotated[RoleRepository, Depends(get_role_repository)],
    import_service: Annotated[ImportJobService, Depends(get_import_job_service)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    claims: Annotated[JwtClaims, Depends(require_permission("settings.roles.manage"))],
    file: UploadFile = File(...),
    skip_existing: bool = Query(True, alias="skipExisting"),
    dry_run: bool = Query(False, alias="dryRun"),
    strict: bool = Query(False),
    force_sync: bool = Query(False, alias="forceSync"),
) -> dict:
    """Import roles from JSON or CSV upload — P32/P34."""

    from fastapi import HTTPException

    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename required")
    content = await file.read()
    try:
        entries = parse_role_import_file(filename=file.filename, content=content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not entries:
        raise HTTPException(status_code=400, detail="No roles found in file")
    for entry in entries:
        validation = validate_role_permissions(entry["permissions"])
        if strict and (msg := strict_validation_error(validation)):
            raise HTTPException(status_code=400, detail=msg)
    if (
        not dry_run
        and not force_sync
        and len(entries) >= ROLE_IMPORT_ASYNC_THRESHOLD
    ):
        job = await import_service.enqueue_role_import_file(
            company_id=company_id,
            filename=file.filename,
            content=content,
            skip_existing=skip_existing,
            requested_by_user_id=claims.user_id,
        )
        return JSONResponse(
            status_code=202,
            content={
                "result": {
                    "mode": "async",
                    "rowCount": len(entries),
                    "threshold": ROLE_IMPORT_ASYNC_THRESHOLD,
                    "job": jsonable_encoder(job),
                    "sourceFile": file.filename,
                }
            },
        )
    if dry_run:
        out = await repo.preview_import_roles(
            company_id=company_id,
            roles=entries,
            skip_existing=skip_existing,
        )
        warnings = [
            {
                "name": e["name"],
                "unknownPermissions": validate_role_permissions(e["permissions"])[
                    "unknownPermissions"
                ],
            }
            for e in entries
            if validate_role_permissions(e["permissions"])["unknownPermissions"]
        ]
        shape = describe_role_import_file(filename=file.filename, content=content)
        return {
            "result": {
                **out,
                "permissionWarnings": warnings,
                "sourceFile": file.filename,
                **shape,
            }
        }
    try:
        out = await repo.import_roles(
            company_id=company_id,
            roles=entries,
            skip_existing=skip_existing,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    await audit_service.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type="ROLE_IMPORT",
        transaction_id=None,
        status="ok",
        details=f"file={file.filename} created={len(out['created'])} skipped={len(out['skipped'])}",
    )
    return {
        "result": {
            **out,
            "mode": "sync",
            "sourceFile": file.filename,
        }
    }


@router.post("/roles/import/preview")
async def preview_import_roles(
    company_id: str,
    body: RoleImportRequest,
    repo: Annotated[RoleRepository, Depends(get_role_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
    strict: bool = Query(False, description="Flag roles with unknown permission codes"),
) -> dict:
    """Dry-run role import — P31."""

    from fastapi import HTTPException

    entries = [{"name": r.name, "permissions": r.permissions} for r in body.roles]
    warnings: list[dict[str, object]] = []
    for entry in entries:
        validation = validate_role_permissions(entry["permissions"])
        if validation["unknownPermissions"]:
            warnings.append(
                {
                    "name": entry["name"],
                    "unknownPermissions": validation["unknownPermissions"],
                }
            )
        if strict and validation["unknownPermissions"]:
            raise HTTPException(
                status_code=400,
                detail=strict_validation_error(validation),
            )
    out = await repo.preview_import_roles(
        company_id=company_id,
        roles=entries,
        skip_existing=body.skip_existing,
    )
    return {"result": {**out, "permissionWarnings": warnings}}


@router.post("/roles/import", status_code=201)
async def import_roles(
    company_id: str,
    body: RoleImportRequest,
    repo: Annotated[RoleRepository, Depends(get_role_repository)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    claims: Annotated[JwtClaims, Depends(require_permission("settings.roles.manage"))],
    strict: bool = Query(False, description="Reject import when any role has unknown permission codes"),
) -> dict:
    from fastapi import HTTPException

    entries = [{"name": r.name, "permissions": r.permissions} for r in body.roles]
    for entry in entries:
        validation = validate_role_permissions(entry["permissions"])
        if strict and (msg := strict_validation_error(validation)):
            raise HTTPException(status_code=400, detail=msg)
    try:
        out = await repo.import_roles(
            company_id=company_id,
            roles=entries,
            skip_existing=body.skip_existing,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    await audit_service.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type="ROLE_IMPORT",
        transaction_id=None,
        status="ok",
        details=f"created={len(out['created'])} skipped={len(out['skipped'])}",
    )
    return {"result": out}


@router.get("/permissions/catalog")
async def get_permissions_catalog(
    _claims: Annotated[JwtClaims, Depends(resolve_tenant)],
) -> dict:
    """Permission tree for role editor UI — P25."""

    return {"result": PERMISSION_TREE}


@router.get("/permissions/known-codes")
async def get_permissions_known_codes(
    _claims: Annotated[JwtClaims, Depends(resolve_tenant)],
) -> dict:
    """Flat sorted permission codes for autocomplete — P27."""

    return {"result": known_codes_sorted()}


@router.get("/permissions/mine")
async def get_my_permissions(
    company_id: str,
    claims: Annotated[JwtClaims, Depends(resolve_tenant)],
    permission_service: Annotated[
        PermissionService, Depends(get_permission_service)
    ],
    membership_repo: Annotated[MembershipRepository, Depends(get_membership_repository)],
    module_access: Annotated[ModuleAccessService, Depends(get_module_access_service)],
) -> dict:
    """Current user's effective permission codes for UI gating — P36 / RBAC v2."""

    perms = await permission_service.permissions_for(
        company_id=company_id, user_id=claims.user_id
    )
    membership = await membership_repo.get_membership(
        company_id=company_id, user_id=claims.user_id
    )
    modules = await module_access.matrix_for_user(
        company_id=company_id, user_id=claims.user_id
    )
    return {
        "result": {
            "permissions": perms,
            "roleIds": (membership or {}).get("roleIds", []),
            "roles": (membership or {}).get("roles", []),
            "modules": modules,
        }
    }


@router.get("/me/onboarding")
async def get_my_onboarding(
    company_id: str,
    claims: Annotated[JwtClaims, Depends(resolve_tenant)],
    onboarding_repo: Annotated[OnboardingRepository, Depends(get_onboarding_repository)],
    release_repo: Annotated[
        OnboardingReleaseRepository, Depends(get_onboarding_release_repository)
    ],
    platform_release_repo: Annotated[
        PlatformOnboardingReleaseRepository,
        Depends(get_platform_onboarding_release_repository),
    ],
    membership_repo: Annotated[MembershipRepository, Depends(get_membership_repository)],
    permission_service: Annotated[
        PermissionService, Depends(get_permission_service)
    ],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    company_repo: Annotated[CompanyRepository, Depends(get_company_repository)],
    email_service: Annotated[EmailService, Depends(get_email_service)],
    attempt_digest: bool = Query(True),
) -> dict:
    """Tour progress + role context for guided onboarding — P48."""

    from app.core.config import get_settings
    from app.services.onboarding_digest_service import digest_is_due, send_whats_new_digest

    payload = await onboarding_repo.get_payload(
        company_id=company_id, user_id=claims.user_id
    )
    membership = await membership_repo.get_membership(
        company_id=company_id, user_id=claims.user_id
    )
    perms = await permission_service.permissions_for(
        company_id=company_id, user_id=claims.user_id
    )
    from app.services.onboarding_release_service import releases_for_user

    tenant_releases = await release_repo.list_for_company(
        company_id=company_id, active_only=True
    )
    platform_releases = await platform_release_repo.list_all(active_only=True)
    releases = releases_for_user(perms, tenant_releases, platform_releases)

    digest_attempt: dict[str, Any] | None = None
    if attempt_digest and digest_is_due(payload, releases):
        user = await user_repo.find_by_id(user_id=claims.user_id)
        if user and user.email:
            settings = get_settings()
            app_base = (settings.cors_origins.split(",")[0] or "http://localhost:3000").strip()
            company_name = await company_repo.get_company_name(company_id=company_id)
            name = f"{user.firstName or ''} {user.lastName or ''}".strip() or user.email
            ok, message = await send_whats_new_digest(
                email_service=email_service,
                to_email=user.email,
                user_name=name,
                company_name=company_name,
                user_perms=perms,
                progress=payload,
                tenant_releases=tenant_releases,
                platform_releases=platform_releases,
                app_base_url=app_base,
            )
            if ok:
                now = datetime.now(UTC).isoformat()
                prefs = payload.get("preferences")
                if not isinstance(prefs, dict):
                    prefs = {}
                prefs["lastDigestSentAt"] = now
                payload["preferences"] = prefs
                payload = await onboarding_repo.upsert_payload(
                    company_id=company_id, user_id=claims.user_id, payload=payload
                )
            digest_attempt = {"sent": ok, "message": message}

    return {
        "result": {
            "progress": _onboarding_progress_view(payload),
            "roleName": membership.get("roleName") if membership else None,
            "permissions": perms,
            "releases": releases,
            "digestAttempt": digest_attempt,
        }
    }


def _onboarding_progress_view(payload: dict[str, Any]) -> dict[str, Any]:
    prefs = payload.get("preferences")
    if not isinstance(prefs, dict):
        prefs = {"emailDigestEnabled": False, "lastDigestSentAt": None}
    return {
        "tours": payload.get("tours", {}),
        "maturityScore": payload.get("maturityScore", 0),
        "dismissedHints": payload.get("dismissedHints", []),
        "lastActiveTourId": payload.get("lastActiveTourId"),
        "preferences": prefs,
    }


@router.get("/me/onboarding/suggestions")
async def get_my_onboarding_suggestions(
    company_id: str,
    claims: Annotated[JwtClaims, Depends(resolve_tenant)],
    onboarding_repo: Annotated[OnboardingRepository, Depends(get_onboarding_repository)],
    release_repo: Annotated[
        OnboardingReleaseRepository, Depends(get_onboarding_release_repository)
    ],
    platform_release_repo: Annotated[
        PlatformOnboardingReleaseRepository,
        Depends(get_platform_onboarding_release_repository),
    ],
    membership_repo: Annotated[MembershipRepository, Depends(get_membership_repository)],
    permission_service: Annotated[
        PermissionService, Depends(get_permission_service)
    ],
    pathname: str = Query("/dashboard", max_length=256),
) -> dict:
    """Contextual ranked suggestions for AI assistant panel — P51/P52."""

    from app.services.onboarding_llm_service import learning_suggestions
    from app.services.onboarding_release_service import releases_for_user

    payload = await onboarding_repo.get_payload(
        company_id=company_id, user_id=claims.user_id
    )
    membership = await membership_repo.get_membership(
        company_id=company_id, user_id=claims.user_id
    )
    perms = await permission_service.permissions_for(
        company_id=company_id, user_id=claims.user_id
    )
    tenant_releases = await release_repo.list_for_company(
        company_id=company_id, active_only=True
    )
    platform_releases = await platform_release_repo.list_all(active_only=True)
    releases = releases_for_user(perms, tenant_releases, platform_releases)
    progress = {
        "tours": payload.get("tours", {}),
        "maturityScore": payload.get("maturityScore", 0),
        "dismissedHints": payload.get("dismissedHints", []),
    }
    persona = membership.get("roleName") if membership else None
    suggestions, engine = await learning_suggestions(
        pathname=pathname,
        user_perms=perms,
        progress=progress,
        persona=persona,
        releases=releases,
    )
    return {"result": {"suggestions": suggestions, "pathname": pathname, "engine": engine}}


@router.post("/me/onboarding/assistant")
async def post_my_onboarding_assistant(
    company_id: str,
    body: OnboardingAssistantRequest,
    claims: Annotated[JwtClaims, Depends(resolve_tenant)],
    onboarding_repo: Annotated[OnboardingRepository, Depends(get_onboarding_repository)],
    membership_repo: Annotated[MembershipRepository, Depends(get_membership_repository)],
    permission_service: Annotated[
        PermissionService, Depends(get_permission_service)
    ],
) -> dict:
    """Short natural-language answer for learning assistant chat — P52."""

    from app.services.onboarding_llm_service import assistant_reply

    payload = await onboarding_repo.get_payload(
        company_id=company_id, user_id=claims.user_id
    )
    membership = await membership_repo.get_membership(
        company_id=company_id, user_id=claims.user_id
    )
    perms = await permission_service.permissions_for(
        company_id=company_id, user_id=claims.user_id
    )
    progress = {
        "tours": payload.get("tours", {}),
        "maturityScore": payload.get("maturityScore", 0),
        "dismissedHints": payload.get("dismissedHints", []),
    }
    reply, engine = await assistant_reply(
        message=body.message,
        pathname=body.pathname,
        user_perms=perms,
        progress=progress,
        persona=membership.get("roleName") if membership else None,
    )
    return {"result": {"reply": reply, "engine": engine, "pathname": body.pathname}}


@router.get("/onboarding/releases")
async def list_onboarding_releases(
    company_id: str,
    release_repo: Annotated[
        OnboardingReleaseRepository, Depends(get_onboarding_release_repository)
    ],
    _claims: Annotated[JwtClaims, Depends(require_permission("settings.users.invite"))],
) -> dict:
    """List tenant CMS release rows (admin) — P51."""

    rows = await release_repo.list_for_company(company_id=company_id, active_only=False)
    return {"result": rows}


@router.post("/onboarding/releases", status_code=201)
async def create_onboarding_release(
    company_id: str,
    body: OnboardingReleaseCreateRequest,
    release_repo: Annotated[
        OnboardingReleaseRepository, Depends(get_onboarding_release_repository)
    ],
    _claims: Annotated[JwtClaims, Depends(require_permission("settings.users.invite"))],
) -> dict:
    from fastapi import HTTPException

    try:
        row = await release_repo.create(
            company_id=company_id,
            release_key=body.releaseKey.strip(),
            version=body.version,
            title=body.title.strip(),
            summary=body.summary.strip(),
            published_at=body.publishedAt.strip(),
            tour_id=body.tourId,
            href=body.href,
            permissions=body.permissions,
            is_active=body.isActive,
            sort_order=body.sortOrder,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": row}


@router.put("/onboarding/releases/{item_id}")
async def update_onboarding_release(
    company_id: str,
    item_id: str,
    body: OnboardingReleaseUpdateRequest,
    release_repo: Annotated[
        OnboardingReleaseRepository, Depends(get_onboarding_release_repository)
    ],
    _claims: Annotated[JwtClaims, Depends(require_permission("settings.users.invite"))],
) -> dict:
    from fastapi import HTTPException

    patch: dict[str, Any] = {}
    if body.version is not None:
        patch["version"] = body.version
    if body.title is not None:
        patch["title"] = body.title.strip()
    if body.summary is not None:
        patch["summary"] = body.summary.strip()
    if body.publishedAt is not None:
        patch["publishedAt"] = body.publishedAt.strip()
    if body.tourId is not None:
        patch["tourId"] = body.tourId
    if body.href is not None:
        patch["href"] = body.href
    if body.permissions is not None:
        patch["permissions"] = body.permissions
    if body.isActive is not None:
        patch["isActive"] = body.isActive
    if body.sortOrder is not None:
        patch["sortOrder"] = body.sortOrder
    row = await release_repo.update(company_id=company_id, item_id=item_id, data=patch)
    if row is None:
        raise HTTPException(status_code=404, detail="Release not found")
    return {"result": row}


@router.delete("/onboarding/releases/{item_id}", status_code=204)
async def delete_onboarding_release(
    company_id: str,
    item_id: str,
    release_repo: Annotated[
        OnboardingReleaseRepository, Depends(get_onboarding_release_repository)
    ],
    _claims: Annotated[JwtClaims, Depends(require_permission("settings.users.invite"))],
) -> Response:
    from fastapi import HTTPException

    ok = await release_repo.delete(company_id=company_id, item_id=item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Release not found")
    return Response(status_code=204)


@router.get("/platform/onboarding/releases")
async def list_platform_onboarding_releases(
    company_id: str,
    platform_release_repo: Annotated[
        PlatformOnboardingReleaseRepository,
        Depends(get_platform_onboarding_release_repository),
    ],
    _claims: Annotated[JwtClaims, Depends(require_permission("settings.platform.process"))],
) -> dict:
    """List platform-wide What's New rows (operator) — P52."""

    rows = await platform_release_repo.list_all(active_only=False)
    return {"result": rows}


@router.post("/platform/onboarding/releases", status_code=201)
async def create_platform_onboarding_release(
    company_id: str,
    body: OnboardingReleaseCreateRequest,
    platform_release_repo: Annotated[
        PlatformOnboardingReleaseRepository,
        Depends(get_platform_onboarding_release_repository),
    ],
    _claims: Annotated[JwtClaims, Depends(require_permission("settings.platform.process"))],
) -> dict:
    from fastapi import HTTPException

    try:
        row = await platform_release_repo.create(
            release_key=body.releaseKey.strip(),
            version=body.version,
            title=body.title.strip(),
            summary=body.summary.strip(),
            published_at=body.publishedAt.strip(),
            tour_id=body.tourId,
            href=body.href,
            permissions=body.permissions,
            is_active=body.isActive,
            sort_order=body.sortOrder,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": row}


@router.put("/platform/onboarding/releases/{item_id}")
async def update_platform_onboarding_release(
    company_id: str,
    item_id: str,
    body: OnboardingReleaseUpdateRequest,
    platform_release_repo: Annotated[
        PlatformOnboardingReleaseRepository,
        Depends(get_platform_onboarding_release_repository),
    ],
    _claims: Annotated[JwtClaims, Depends(require_permission("settings.platform.process"))],
) -> dict:
    from fastapi import HTTPException

    patch: dict[str, Any] = {}
    if body.version is not None:
        patch["version"] = body.version
    if body.title is not None:
        patch["title"] = body.title.strip()
    if body.summary is not None:
        patch["summary"] = body.summary.strip()
    if body.publishedAt is not None:
        patch["publishedAt"] = body.publishedAt.strip()
    if body.tourId is not None:
        patch["tourId"] = body.tourId
    if body.href is not None:
        patch["href"] = body.href
    if body.permissions is not None:
        patch["permissions"] = body.permissions
    if body.isActive is not None:
        patch["isActive"] = body.isActive
    if body.sortOrder is not None:
        patch["sortOrder"] = body.sortOrder
    row = await platform_release_repo.update(item_id=item_id, data=patch)
    if row is None:
        raise HTTPException(status_code=404, detail="Release not found")
    return {"result": row}


@router.delete("/platform/onboarding/releases/{item_id}", status_code=204)
async def delete_platform_onboarding_release(
    company_id: str,
    item_id: str,
    platform_release_repo: Annotated[
        PlatformOnboardingReleaseRepository,
        Depends(get_platform_onboarding_release_repository),
    ],
    _claims: Annotated[JwtClaims, Depends(require_permission("settings.platform.process"))],
) -> Response:
    from fastapi import HTTPException

    ok = await platform_release_repo.delete(item_id=item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Release not found")
    return Response(status_code=204)


@router.get("/onboarding/insights")
async def get_onboarding_insights(
    company_id: str,
    onboarding_repo: Annotated[OnboardingRepository, Depends(get_onboarding_repository)],
    _claims: Annotated[JwtClaims, Depends(require_permission("settings.users.invite"))],
) -> dict:
    """Company-wide tour analytics from stored event logs — P50."""

    from app.services.onboarding_release_service import insights_from_payloads

    payloads = await onboarding_repo.list_company_payloads(company_id=company_id)
    return {"result": insights_from_payloads(payloads)}


@router.get("/onboarding/insights/export")
async def export_onboarding_insights(
    company_id: str,
    onboarding_repo: Annotated[OnboardingRepository, Depends(get_onboarding_repository)],
    _claims: Annotated[JwtClaims, Depends(require_permission("settings.users.invite"))],
) -> Response:
    """CSV export of tour analytics — P53."""

    from app.services.onboarding_insights_csv import insights_to_csv
    from app.services.onboarding_release_service import insights_from_payloads

    payloads = await onboarding_repo.list_company_payloads(company_id=company_id)
    csv_text = insights_to_csv(insights_from_payloads(payloads))
    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="learning-insights.csv"'},
    )


@router.put("/me/onboarding")
async def put_my_onboarding(
    company_id: str,
    body: OnboardingProgressBody,
    claims: Annotated[JwtClaims, Depends(resolve_tenant)],
    onboarding_repo: Annotated[OnboardingRepository, Depends(get_onboarding_repository)],
) -> dict:
    """Replace tour progress (preserves server event log) — P48."""

    existing = await onboarding_repo.get_payload(
        company_id=company_id, user_id=claims.user_id
    )
    payload = body.to_payload()
    payload["eventLog"] = existing.get("eventLog", [])
    if body.preferences is None:
        payload["preferences"] = existing.get(
            "preferences", {"emailDigestEnabled": False}
        )
    saved = await onboarding_repo.upsert_payload(
        company_id=company_id, user_id=claims.user_id, payload=payload
    )
    return {"result": {"progress": _onboarding_progress_view(saved)}}


@router.post("/me/onboarding/digest-email")
async def post_my_onboarding_digest_email(
    company_id: str,
    claims: Annotated[JwtClaims, Depends(resolve_tenant)],
    onboarding_repo: Annotated[OnboardingRepository, Depends(get_onboarding_repository)],
    release_repo: Annotated[
        OnboardingReleaseRepository, Depends(get_onboarding_release_repository)
    ],
    platform_release_repo: Annotated[
        PlatformOnboardingReleaseRepository,
        Depends(get_platform_onboarding_release_repository),
    ],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    company_repo: Annotated[CompanyRepository, Depends(get_company_repository)],
    permission_service: Annotated[
        PermissionService, Depends(get_permission_service)
    ],
    email_service: Annotated[EmailService, Depends(get_email_service)],
) -> dict:
    """Email current user a digest of unread What's New items — P55."""

    from fastapi import HTTPException

    from app.core.config import get_settings
    from app.services.onboarding_digest_service import send_whats_new_digest

    user = await user_repo.find_by_id(user_id=claims.user_id)
    if user is None or not user.email:
        raise HTTPException(status_code=400, detail="User email not found")

    payload = await onboarding_repo.get_payload(
        company_id=company_id, user_id=claims.user_id
    )
    perms = await permission_service.permissions_for(
        company_id=company_id, user_id=claims.user_id
    )
    tenant_releases = await release_repo.list_for_company(
        company_id=company_id, active_only=True
    )
    platform_releases = await platform_release_repo.list_all(active_only=True)
    settings = get_settings()
    app_base = (settings.cors_origins.split(",")[0] or "http://localhost:3000").strip()
    company_name = await company_repo.get_company_name(company_id=company_id)
    name = f"{user.firstName or ''} {user.lastName or ''}".strip() or user.email

    ok, message = await send_whats_new_digest(
        email_service=email_service,
        to_email=user.email,
        user_name=name,
        company_name=company_name,
        user_perms=perms,
        progress=payload,
        tenant_releases=tenant_releases,
        platform_releases=platform_releases,
        app_base_url=app_base,
    )
    if not ok:
        raise HTTPException(status_code=400, detail=message)

    now = datetime.now(UTC).isoformat()
    prefs = payload.get("preferences")
    if not isinstance(prefs, dict):
        prefs = {}
    prefs["lastDigestSentAt"] = now
    payload["preferences"] = prefs
    await onboarding_repo.upsert_payload(
        company_id=company_id, user_id=claims.user_id, payload=payload
    )
    return {"result": {"sent": True, "message": message, "lastDigestSentAt": now}}


@router.post("/me/onboarding/events", status_code=204)
async def post_my_onboarding_events(
    company_id: str,
    body: OnboardingEventsBody,
    claims: Annotated[JwtClaims, Depends(resolve_tenant)],
    onboarding_repo: Annotated[OnboardingRepository, Depends(get_onboarding_repository)],
) -> Response:
    """Append batched tour analytics events — P48."""

    if not body.events:
        return Response(status_code=204)
    now = datetime.now(UTC).isoformat()
    rows = [
        {
            **e.model_dump(exclude_none=True),
            "recordedAt": now,
            "userId": claims.user_id,
            "companyId": company_id,
        }
        for e in body.events
    ]
    await onboarding_repo.append_events(
        company_id=company_id, user_id=claims.user_id, events=rows
    )
    return Response(status_code=204)


@router.get("/roles/{role_id}")
async def get_role(
    company_id: str,
    role_id: str,
    repo: Annotated[RoleRepository, Depends(get_role_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("financial"))],
) -> dict:
    payload = await repo.get_role_payload(company_id=company_id, role_id=role_id)
    if payload is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Role not found")
    return {"result": payload}


@router.post("/roles", status_code=201)
async def create_role(
    company_id: str,
    body: RoleCreateRequest,
    repo: Annotated[RoleRepository, Depends(get_role_repository)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    claims: Annotated[JwtClaims, Depends(require_permission("settings.roles.manage"))],
    strict: bool = Query(False, description="Reject save when unknown permission codes are present"),
) -> dict:
    from fastapi import HTTPException

    validation = validate_role_permissions(body.permissions)
    if strict and (msg := strict_validation_error(validation)):
        raise HTTPException(status_code=400, detail=msg)
    try:
        row = await repo.create_role(
            company_id=company_id,
            name=body.name,
            permissions=body.permissions,
            description=body.description,
            parent_role_id=body.parent_role_id,
            code=body.code,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    payload = await repo.get_role_payload(company_id=company_id, role_id=row.id)
    await audit_service.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type="ROLE_CREATE",
        transaction_id=row.id,
        status="ok",
        details=f"name={row.name}",
    )
    return {
        "result": payload,
        **validation,
    }


@router.put("/roles/{role_id}")
async def update_role(
    company_id: str,
    role_id: str,
    body: RoleUpdateRequest,
    repo: Annotated[RoleRepository, Depends(get_role_repository)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    claims: Annotated[JwtClaims, Depends(require_permission("settings.roles.manage"))],
    strict: bool = Query(False, description="Reject save when unknown permission codes are present"),
) -> dict:
    from fastapi import HTTPException

    before = await repo.get_role_payload(company_id=company_id, role_id=role_id)
    validation = (
        validate_role_permissions(body.permissions)
        if body.permissions is not None
        else {"unknownPermissions": [], "permissionWarnings": []}
    )
    if strict and (msg := strict_validation_error(validation)):
        raise HTTPException(status_code=400, detail=msg)
    try:
        await repo.update_role(
            company_id=company_id,
            role_id=role_id,
            name=body.name,
            permissions=body.permissions,
            description=body.description,
            parent_role_id=body.parent_role_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    payload = await repo.get_role_payload(company_id=company_id, role_id=role_id)
    import json

    await audit_service.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type="ROLE_UPDATE",
        transaction_id=role_id,
        status="ok",
        details=json.dumps({"before": before, "after": payload}),
    )
    if body.permissions is not None:
        await audit_service.record(
            company_id=company_id,
            user_id=claims.user_id,
            transaction_type="ROLE_PERMISSION_CHANGE",
            transaction_id=role_id,
            status="ok",
            details=json.dumps(
                {
                    "before": (before or {}).get("permissions", []),
                    "after": payload.get("permissions", []),
                }
            ),
        )
    return {
        "result": payload,
        **validation,
    }


@router.post("/roles/{role_id}/clone", status_code=201)
async def clone_role(
    company_id: str,
    role_id: str,
    body: RoleCloneRequest,
    repo: Annotated[RoleRepository, Depends(get_role_repository)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    claims: Annotated[JwtClaims, Depends(require_permission("settings.roles.manage"))],
    strict: bool = Query(False, description="Reject save when unknown permission codes are present"),
) -> dict:
    from fastapi import HTTPException

    source = await repo.get_role(company_id=company_id, role_id=role_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Role not found")
    perms = source.permissions if isinstance(source.permissions, list) else []
    perm_list = [str(p) for p in perms]
    validation = validate_role_permissions(perm_list)
    if strict and (msg := strict_validation_error(validation)):
        raise HTTPException(status_code=400, detail=msg)
    try:
        row = await repo.clone_role(
            company_id=company_id,
            role_id=role_id,
            name=body.name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    out_perms = row.permissions if isinstance(row.permissions, list) else []
    await audit_service.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type="ROLE_CLONE",
        transaction_id=row.id,
        status="ok",
        details=f"sourceRoleId={role_id} name={row.name}",
    )
    return {
        "result": {"id": row.id, "name": row.name, "permissions": out_perms},
        **validation,
    }


@router.delete("/roles/{role_id}")
async def delete_role(
    company_id: str,
    role_id: str,
    repo: Annotated[RoleRepository, Depends(get_role_repository)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    claims: Annotated[JwtClaims, Depends(require_permission("settings.roles.manage"))],
) -> dict:
    from fastapi import HTTPException

    before = await repo.get_role_payload(company_id=company_id, role_id=role_id)
    if before is None:
        raise HTTPException(status_code=404, detail="Role not found")
    try:
        await repo.delete_role(company_id=company_id, role_id=role_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    import json

    await audit_service.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type="ROLE_DELETE",
        transaction_id=role_id,
        status="ok",
        details=json.dumps(before),
    )
    return {"result": {"deleted": True, "roleId": role_id}}


@router.patch("/users/{user_id}/role")
async def assign_user_role(
    company_id: str,
    user_id: str,
    body: AssignUserRoleRequest,
    membership_repo: Annotated[MembershipRepository, Depends(get_membership_repository)],
    _claims: Annotated[JwtClaims, Depends(require_permission("settings.roles.manage"))],
) -> dict:
    from fastapi import HTTPException

    try:
        row = await membership_repo.assign_role(
            company_id=company_id,
            user_id=user_id,
            role_id=body.role_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": row}


@router.post("/users/invite", status_code=201)
async def invite_user(
    company_id: str,
    body: InviteUserRequest,
    membership_repo: Annotated[MembershipRepository, Depends(get_membership_repository)],
    invite_service: Annotated[UserInviteService, Depends(get_user_invite_service)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    billing: Annotated[SubscriptionBillingService, Depends(get_subscription_billing_service)],
    claims: Annotated[JwtClaims, Depends(require_permission("settings.users.invite"))],
) -> dict:
    """Add a user to the company with a role (create account if email is new) — P27/P28."""

    import secrets

    from fastapi import HTTPException

    try:
        await billing.assert_can_add_member(company_id=company_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    temp_password = secrets.token_urlsafe(32)
    try:
        row = await membership_repo.invite_member(
            company_id=company_id,
            email=body.email,
            first_name=body.first_name,
            last_name=body.last_name,
            role_id=body.role_id,
            password_hash=hash_password(temp_password),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    invite_email_sent = await invite_service.send_setup_email_if_needed(
        company_id=company_id,
        user_id=row["userId"],
        email=row["email"],
        user_created=bool(row.get("userCreated")),
    )
    await audit_service.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type="USER_INVITE",
        transaction_id=row["userId"],
        status="ok",
        details=f"email={row['email']} roleId={body.role_id} emailSent={invite_email_sent}",
    )
    return {"result": {**row, "inviteEmailSent": invite_email_sent}}


@router.patch("/users/{user_id}/ip-allowlist")
async def update_user_ip_allowlist(
    company_id: str,
    user_id: str,
    body: UpdateIpAllowlistRequest,
    membership_repo: Annotated[MembershipRepository, Depends(get_membership_repository)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    claims: Annotated[JwtClaims, Depends(require_permission("settings.users.invite"))],
) -> dict:
    """Set comma-separated IP allowlist for a company member — P9."""

    from fastapi import HTTPException

    try:
        row = await membership_repo.update_ip_allowlist(
            company_id=company_id,
            user_id=user_id,
            ip_allowlist=body.ip_allowlist,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    await audit_service.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type="USER_IP_ALLOWLIST",
        transaction_id=user_id,
        status="ok",
        details=f"ipAllowlist={body.ip_allowlist or ''}",
    )
    return {"result": row}


@router.post("/users/{user_id}/resend-invite")
async def resend_user_invite(
    company_id: str,
    user_id: str,
    invite_service: Annotated[UserInviteService, Depends(get_user_invite_service)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    app_settings: Annotated[AppSettingsService, Depends(get_app_settings_service)],
    claims: Annotated[JwtClaims, Depends(require_permission("settings.users.invite"))],
) -> dict:
    """Resend set-password or welcome email for a member — P29."""

    from fastapi import HTTPException

    try:
        payload = await invite_service.resend_invite_email(
            company_id=company_id,
            user_id=user_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    await audit_service.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type="USER_INVITE_RESEND",
        transaction_id=user_id,
        status="ok",
        details=f"emailType={payload['emailType']} emailSent={payload['emailSent']}",
    )
    if payload.get("emailSent"):
        await app_settings.append_sent_email(
            company_id=company_id,
            entry={
                "to": payload.get("email", ""),
                "subject": payload.get("emailType", "invite"),
                "status": "sent",
            },
        )
    return {"result": payload}


@router.delete("/users/{user_id}/membership")
async def revoke_user_membership(
    company_id: str,
    user_id: str,
    membership_repo: Annotated[MembershipRepository, Depends(get_membership_repository)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    claims: Annotated[JwtClaims, Depends(require_permission("settings.users.invite"))],
) -> dict:
    """Remove a user from this company — P32."""

    from fastapi import HTTPException

    try:
        row = await membership_repo.revoke_membership(
            company_id=company_id,
            user_id=user_id,
            acting_user_id=claims.user_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    await audit_service.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type="USER_MEMBERSHIP_REVOKE",
        transaction_id=user_id,
        status="ok",
        details=f"email={row['email']}",
    )
    return {"result": row}


@router.post("/users/{user_id}/deactivate")
async def deactivate_user(
    company_id: str,
    user_id: str,
    membership_repo: Annotated[MembershipRepository, Depends(get_membership_repository)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    claims: Annotated[JwtClaims, Depends(require_permission("settings.users.invite"))],
) -> dict:
    """Deactivate user account (blocks sign-in globally) — P32."""

    from fastapi import HTTPException

    try:
        row = await membership_repo.deactivate_user(
            company_id=company_id,
            user_id=user_id,
            acting_user_id=claims.user_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    await audit_service.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type="USER_DEACTIVATE",
        transaction_id=user_id,
        status="ok",
        details=f"email={row['email']}",
    )
    return {"result": row}


@router.post("/users/{user_id}/reinvite", status_code=201)
async def reinvite_user(
    company_id: str,
    user_id: str,
    body: ReinviteUserRequest,
    membership_repo: Annotated[MembershipRepository, Depends(get_membership_repository)],
    invite_service: Annotated[UserInviteService, Depends(get_user_invite_service)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    billing: Annotated[SubscriptionBillingService, Depends(get_subscription_billing_service)],
    claims: Annotated[JwtClaims, Depends(require_permission("settings.users.invite"))],
) -> dict:
    """Re-add a revoked user to the company with a role — P34."""

    from fastapi import HTTPException

    try:
        await billing.assert_can_add_member(company_id=company_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        row = await membership_repo.reinvite_member(
            company_id=company_id,
            user_id=user_id,
            role_id=body.role_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    invite_email_sent = await invite_service.send_setup_email_if_needed(
        company_id=company_id,
        user_id=row["userId"],
        email=row["email"],
        user_created=False,
    )
    await audit_service.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type="USER_REINVITE",
        transaction_id=user_id,
        status="ok",
        details=f"email={row['email']} roleId={body.role_id} emailSent={invite_email_sent}",
    )
    return {"result": {**row, "inviteEmailSent": invite_email_sent}}


@router.post("/users/{user_id}/reactivate")
async def reactivate_user(
    company_id: str,
    user_id: str,
    membership_repo: Annotated[MembershipRepository, Depends(get_membership_repository)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    claims: Annotated[JwtClaims, Depends(require_permission("settings.users.invite"))],
) -> dict:
    """Re-enable a deactivated user account — P33."""

    from fastapi import HTTPException

    try:
        row = await membership_repo.reactivate_user(
            company_id=company_id,
            user_id=user_id,
            acting_user_id=claims.user_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    await audit_service.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type="USER_REACTIVATE",
        transaction_id=user_id,
        status="ok",
        details=f"email={row['email']}",
    )
    return {"result": row}


@router.get("/customers/{customer_id}/open-invoices")
async def list_customer_open_invoices(
    company_id: str,
    customer_id: str,
    allocation_service: Annotated[AllocationService, Depends(get_allocation_service)],
) -> dict:
    """Open sales invoices for explicit receipt allocation — Sprint 13."""

    rows = await allocation_service.list_open_sales_invoices(
        company_id=company_id, customer_id=customer_id
    )
    return {"result": rows}


@router.get("/suppliers/{supplier_id}/open-bills")
async def list_supplier_open_bills(
    company_id: str,
    supplier_id: str,
    allocation_service: Annotated[AllocationService, Depends(get_allocation_service)],
) -> dict:
    """Open supplier bills for explicit payment allocation — Sprint 13."""

    rows = await allocation_service.list_open_supplier_bills(
        company_id=company_id, supplier_id=supplier_id
    )
    return {"result": rows}


# ---------------- Sprint 4 — Quotations, Orders, Credits ----------------


@router.get("/quotations")
async def list_quotations(
    company_id: str,
    repo: Annotated[QuotationRepository, Depends(get_quotation_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("sales"))],
) -> dict:
    """Quotations (§5.2)."""

    rows = await repo.list_quotations(company_id=company_id)
    return {"result": _dump_rows(rows)}


@router.get("/quotations/{quotation_id}")
async def get_quotation(
    company_id: str,
    quotation_id: str,
    repo: Annotated[QuotationRepository, Depends(get_quotation_repository)],
) -> dict:
    row = await repo.get_quotation(company_id=company_id, quotation_id=quotation_id)
    if row is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Quotation not found")
    return {"result": jsonable_encoder(row)}


@router.post("/quotations", status_code=201)
async def create_quotation(
    company_id: str,
    body: QuotationCreateRequest,
    repo: Annotated[QuotationRepository, Depends(get_quotation_repository)],
    document_number_service: Annotated[
        DocumentNumberService, Depends(get_document_number_service)
    ],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    tax_service: Annotated[TaxCalculationService, Depends(get_tax_calculation_service)],
    _claims: Annotated[Any, Depends(require_permission("sales.quotations.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("sales"))],
) -> dict:
    await lock_date_service.assert_not_locked(
        company_id=company_id,
        document_date=body.quotation_date,
        document_label="quotation",
    )
    number = str(
        await document_number_service.reserve_next(company_id=company_id, sequence_key="SQ")
    )
    repo_lines = await _taxed_planning_lines(
        company_id=company_id,
        raw_lines=body.to_raw_lines(),
        tax_service=tax_service,
    )
    row = await repo.create_quotation(
        company_id=company_id,
        quotation_number=number,
        quotation_date=body.quotation_date,
        customer_id=body.customer_id,
        lines=repo_lines,
    )
    return {"result": jsonable_encoder(row)}


@router.put("/quotations/{quotation_id}/status")
async def set_quotation_status(
    company_id: str,
    quotation_id: str,
    body: StatusTransitionRequest,
    repo: Annotated[QuotationRepository, Depends(get_quotation_repository)],
    _claims: Annotated[Any, Depends(require_permission("sales.quotations.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("sales"))],
) -> dict:
    try:
        row = await repo.update_status(
            company_id=company_id, quotation_id=quotation_id, status=body.status
        )
    except ValueError as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(row)}


@router.get("/sales-orders")
async def list_sales_orders(
    company_id: str,
    repo: Annotated[SalesOrderRepository, Depends(get_sales_order_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("sales"))],
) -> dict:
    """Sales orders (§5.3)."""

    rows = await repo.list_orders(company_id=company_id)
    return {"result": _dump_rows(rows)}


@router.get("/sales-orders/{order_id}")
async def get_sales_order(
    company_id: str,
    order_id: str,
    repo: Annotated[SalesOrderRepository, Depends(get_sales_order_repository)],
) -> dict:
    row = await repo.get_order(company_id=company_id, order_id=order_id)
    if row is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Sales order not found")
    return {"result": jsonable_encoder(row)}


@router.post("/sales-orders", status_code=201)
async def create_sales_order(
    company_id: str,
    body: SalesOrderCreateRequest,
    repo: Annotated[SalesOrderRepository, Depends(get_sales_order_repository)],
    document_number_service: Annotated[
        DocumentNumberService, Depends(get_document_number_service)
    ],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    tax_service: Annotated[TaxCalculationService, Depends(get_tax_calculation_service)],
    smart_runtime: Annotated[SmartSettingsRuntime, Depends(get_smart_settings_runtime)],
    _claims: Annotated[Any, Depends(require_permission("sales.orders.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("sales"))],
) -> dict:
    from fastapi import HTTPException

    await lock_date_service.assert_not_locked(
        company_id=company_id,
        document_date=body.order_date,
        document_label="sales order",
    )
    number = str(
        await document_number_service.reserve_next(company_id=company_id, sequence_key="SO")
    )
    repo_lines = await _taxed_planning_lines(
        company_id=company_id,
        raw_lines=body.to_raw_lines(),
        tax_service=tax_service,
    )
    order_total = sum(Decimal(str(line.get("lineTotal", 0))) for line in repo_lines)
    try:
        await smart_runtime.assert_credit_limit(
            company_id=company_id,
            customer_id=body.customer_id,
            additional_amount=order_total,
            for_sales_order=True,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    row = await repo.create_order(
        company_id=company_id,
        order_number=number,
        order_date=body.order_date,
        customer_id=body.customer_id,
        lines=repo_lines,
    )
    return {"result": jsonable_encoder(row)}


@router.put("/sales-orders/{order_id}/status")
async def set_sales_order_status(
    company_id: str,
    order_id: str,
    body: StatusTransitionRequest,
    repo: Annotated[SalesOrderRepository, Depends(get_sales_order_repository)],
    reversal_service: Annotated[
        DocumentReversalService, Depends(get_document_reversal_service)
    ],
    _claims: Annotated[Any, Depends(require_permission("sales.orders.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("sales"))],
) -> dict:
    from fastapi import HTTPException

    try:
        row = await repo.update_status(
            company_id=company_id, order_id=order_id, status=body.status
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if body.status != "cancelled":
        return {"result": jsonable_encoder(row)}
    dgn_side = await reversal_service.void_delivery_notes_for_sales_order(
        company_id=company_id, order_id=order_id
    )
    return {
        "result": {
            "order": jsonable_encoder(row),
            "deliveryNotesVoided": dgn_side["deliveryNotesVoided"],
            "deliveryStockRestored": dgn_side["deliveryStockRestored"],
        }
    }


@router.get("/purchase-orders")
async def list_purchase_orders(
    company_id: str,
    repo: Annotated[PurchaseOrderRepository, Depends(get_purchase_order_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("purchases"))],
) -> dict:
    """Purchase orders (§6.2)."""

    rows = await repo.list_orders(company_id=company_id)
    return {"result": _dump_rows(rows)}


@router.get("/purchase-orders/{order_id}")
async def get_purchase_order(
    company_id: str,
    order_id: str,
    repo: Annotated[PurchaseOrderRepository, Depends(get_purchase_order_repository)],
) -> dict:
    row = await repo.get_order(company_id=company_id, order_id=order_id)
    if row is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Purchase order not found")
    return {"result": jsonable_encoder(row)}


@router.post("/purchase-orders", status_code=201)
async def create_purchase_order(
    company_id: str,
    body: PurchaseOrderCreateRequest,
    repo: Annotated[PurchaseOrderRepository, Depends(get_purchase_order_repository)],
    document_number_service: Annotated[
        DocumentNumberService, Depends(get_document_number_service)
    ],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    tax_service: Annotated[TaxCalculationService, Depends(get_tax_calculation_service)],
    _claims: Annotated[Any, Depends(require_permission("purchases.orders.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("purchases"))],
) -> dict:
    await lock_date_service.assert_not_locked(
        company_id=company_id,
        document_date=body.order_date,
        document_label="purchase order",
    )
    number = str(
        await document_number_service.reserve_next(company_id=company_id, sequence_key="PO")
    )
    repo_lines = await _taxed_planning_lines(
        company_id=company_id,
        raw_lines=body.to_raw_lines(),
        tax_service=tax_service,
    )
    row = await repo.create_order(
        company_id=company_id,
        order_number=number,
        order_date=body.order_date,
        supplier_id=body.supplier_id,
        lines=repo_lines,
    )
    return {"result": jsonable_encoder(row)}


@router.put("/purchase-orders/{order_id}/status")
async def set_purchase_order_status(
    company_id: str,
    order_id: str,
    body: StatusTransitionRequest,
    repo: Annotated[PurchaseOrderRepository, Depends(get_purchase_order_repository)],
    reversal_service: Annotated[
        DocumentReversalService, Depends(get_document_reversal_service)
    ],
    _claims: Annotated[Any, Depends(require_permission("purchases.orders.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("purchases"))],
) -> dict:
    from fastapi import HTTPException

    try:
        row = await repo.update_status(
            company_id=company_id, order_id=order_id, status=body.status
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if body.status != "cancelled":
        return {"result": jsonable_encoder(row)}
    grn_side = await reversal_service.void_grns_for_purchase_order(
        company_id=company_id, order_id=order_id
    )
    return {
        "result": {
            "order": jsonable_encoder(row),
            "grnVoided": grn_side["grnVoided"],
            "grnStockRollback": grn_side["grnStockRollback"],
        }
    }


@router.get("/sales-credits")
async def list_sales_credits(
    company_id: str,
    repo: Annotated[SalesCreditRepository, Depends(get_sales_credit_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("sales"))],
) -> dict:
    """Sales credits (§5.5)."""

    rows = await repo.list_credits(company_id=company_id)
    return {"result": _dump_rows(rows)}


@router.get("/sales-credits/{credit_id}")
async def get_sales_credit(
    company_id: str,
    credit_id: str,
    repo: Annotated[SalesCreditRepository, Depends(get_sales_credit_repository)],
) -> dict:
    row = await repo.get_credit(company_id=company_id, credit_id=credit_id)
    if row is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Sales credit not found")
    return {"result": jsonable_encoder(row)}


@router.post("/sales-credits", status_code=201)
async def create_sales_credit(
    company_id: str,
    body: SalesCreditCreateRequest,
    repo: Annotated[SalesCreditRepository, Depends(get_sales_credit_repository)],
    document_number_service: Annotated[
        DocumentNumberService, Depends(get_document_number_service)
    ],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    posting_service: Annotated[PostingService, Depends(get_posting_service)],
    tax_service: Annotated[TaxCalculationService, Depends(get_tax_calculation_service)],
    approval_engine: Annotated[ApprovalEngineService, Depends(get_approval_engine_service)],
    _claims: Annotated[Any, Depends(require_permission("sales.credits.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("sales"))],
) -> dict:
    """Create a sales credit (§5.5). Auto-posts DR sales / CR receivables."""

    from decimal import Decimal
    from fastapi import HTTPException

    await lock_date_service.assert_not_locked(
        company_id=company_id,
        document_date=body.credit_date,
        document_label="sales credit",
    )
    number = str(
        await document_number_service.reserve_next(company_id=company_id, sequence_key="SC")
    )
    repo_lines = await _taxed_planning_lines(
        company_id=company_id,
        raw_lines=body.to_raw_lines(),
        tax_service=tax_service,
    )
    total = sum((Decimal(str(l["lineTotal"])) for l in repo_lines), Decimal(0))
    credit_id = str(uuid4())
    try:
        await approval_engine.assert_can_post(
            company_id=company_id,
            entity_type="sales_credit",
            entity_id=credit_id,
            amount=total,
        )
        journal = await posting_service.post_sales_credit(
            company_id=company_id,
            credit_date=body.credit_date,
            credit_number=number,
            total_amount=total,
        )
        row = await repo.create_credit(
            company_id=company_id,
            credit_number=number,
            credit_date=body.credit_date,
            customer_id=body.customer_id,
            lines=repo_lines,
            journal_id=journal.id if journal else None,
            credit_id=credit_id,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "result": jsonable_encoder(row),
        "posted": journal is not None,
        "postingWarning": None
        if journal
        else "Set the receivables and sales nominal codes in Smart Settings → Defaults to enable GL posting.",
    }


@router.post("/sales-credits/{credit_id}/void")
async def void_sales_credit(
    company_id: str,
    credit_id: str,
    body: DocumentVoidRequest,
    reversal_service: Annotated[
        DocumentReversalService, Depends(get_document_reversal_service)
    ],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    _claims: Annotated[Any, Depends(require_permission("sales.credits.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("sales"))],
) -> dict:
    from fastapi import HTTPException

    if body.reversal_date:
        await lock_date_service.assert_not_locked(
            company_id=company_id,
            document_date=body.reversal_date,
            document_label="sales credit void",
        )
    try:
        out = await reversal_service.void_sales_credit(
            company_id=company_id,
            credit_id=credit_id,
            reversal_date=body.reversal_date,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(out)}


@router.get("/supplier-credits")
async def list_supplier_credits(
    company_id: str,
    repo: Annotated[SupplierCreditRepository, Depends(get_supplier_credit_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("purchases"))],
) -> dict:
    """Supplier credits (§6.3 — VC)."""

    rows = await repo.list_credits(company_id=company_id)
    return {"result": _dump_rows(rows)}


@router.get("/supplier-credits/{credit_id}")
async def get_supplier_credit(
    company_id: str,
    credit_id: str,
    repo: Annotated[SupplierCreditRepository, Depends(get_supplier_credit_repository)],
) -> dict:
    row = await repo.get_credit(company_id=company_id, credit_id=credit_id)
    if row is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Supplier credit not found")
    return {"result": jsonable_encoder(row)}


@router.post("/supplier-credits", status_code=201)
async def create_supplier_credit(
    company_id: str,
    body: SupplierCreditCreateRequest,
    repo: Annotated[SupplierCreditRepository, Depends(get_supplier_credit_repository)],
    document_number_service: Annotated[
        DocumentNumberService, Depends(get_document_number_service)
    ],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    posting_service: Annotated[PostingService, Depends(get_posting_service)],
    tax_service: Annotated[TaxCalculationService, Depends(get_tax_calculation_service)],
    approval_engine: Annotated[ApprovalEngineService, Depends(get_approval_engine_service)],
    _claims: Annotated[Any, Depends(require_permission("purchases.credits.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("purchases"))],
) -> dict:
    """Create a supplier credit (§6.3). Auto-posts DR payables / CR purchases."""

    from decimal import Decimal
    from fastapi import HTTPException

    await lock_date_service.assert_not_locked(
        company_id=company_id,
        document_date=body.credit_date,
        document_label="supplier credit",
    )
    number = str(
        await document_number_service.reserve_next(company_id=company_id, sequence_key="VC")
    )
    repo_lines = await _taxed_planning_lines(
        company_id=company_id,
        raw_lines=body.to_raw_lines(),
        tax_service=tax_service,
    )
    total = sum((Decimal(str(l["lineTotal"])) for l in repo_lines), Decimal(0))
    credit_id = str(uuid4())
    try:
        await approval_engine.assert_can_post(
            company_id=company_id,
            entity_type="supplier_credit",
            entity_id=credit_id,
            amount=total,
        )
        journal = await posting_service.post_supplier_credit(
            company_id=company_id,
            credit_date=body.credit_date,
            credit_number=number,
            total_amount=total,
        )
        row = await repo.create_credit(
            company_id=company_id,
            credit_number=number,
            credit_date=body.credit_date,
            supplier_id=body.supplier_id,
            lines=repo_lines,
            journal_id=journal.id if journal else None,
            credit_id=credit_id,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "result": jsonable_encoder(row),
        "posted": journal is not None,
        "postingWarning": None
        if journal
        else "Set the payables and purchases nominal codes in Smart Settings → Defaults to enable GL posting.",
    }


@router.post("/supplier-credits/{credit_id}/void")
async def void_supplier_credit(
    company_id: str,
    credit_id: str,
    body: DocumentVoidRequest,
    reversal_service: Annotated[
        DocumentReversalService, Depends(get_document_reversal_service)
    ],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    _claims: Annotated[Any, Depends(require_permission("purchases.credits.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("purchases"))],
) -> dict:
    from fastapi import HTTPException

    if body.reversal_date:
        await lock_date_service.assert_not_locked(
            company_id=company_id,
            document_date=body.reversal_date,
            document_label="supplier credit void",
        )
    try:
        out = await reversal_service.void_supplier_credit(
            company_id=company_id,
            credit_id=credit_id,
            reversal_date=body.reversal_date,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(out)}


# ---------------- Sprint 5 — Document conversions ----------------


@router.post("/quotations/{quotation_id}/convert-to-order", status_code=201)
async def convert_quotation_to_order(
    company_id: str,
    quotation_id: str,
    conversion_service: Annotated[ConversionService, Depends(get_conversion_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("sales"))],
) -> dict:
    """Copy quotation lines into a new sales order; quote becomes ``converted``."""

    try:
        result = await conversion_service.quotation_to_sales_order(
            company_id=company_id,
            quotation_id=quotation_id,
        )
    except Exception as exc:  # ValidationAppError is mapped to 400 by global handlers
        from app.core.exceptions import ValidationAppError
        from fastapi import HTTPException

        if isinstance(exc, ValidationAppError):
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        raise
    return {"result": jsonable_encoder(result["salesOrder"]), "quotationId": result["quotationId"]}


@router.post("/sales-orders/{order_id}/convert-to-invoice", status_code=201)
async def convert_sales_order_to_invoice(
    company_id: str,
    order_id: str,
    conversion_service: Annotated[ConversionService, Depends(get_conversion_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("sales"))],
) -> dict:
    """Copy SO lines into a new sales invoice and post the AR journal."""

    try:
        result = await conversion_service.sales_order_to_invoice(
            company_id=company_id,
            order_id=order_id,
        )
    except Exception as exc:
        from app.core.exceptions import ValidationAppError
        from fastapi import HTTPException

        if isinstance(exc, ValidationAppError):
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        raise
    return {
        "result": jsonable_encoder(result["salesInvoice"]),
        "orderId": result["orderId"],
        "posted": result["posted"],
    }


@router.post("/purchase-orders/{order_id}/convert-to-bill", status_code=201)
async def convert_purchase_order_to_bill(
    company_id: str,
    order_id: str,
    conversion_service: Annotated[ConversionService, Depends(get_conversion_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("purchases"))],
) -> dict:
    """Copy PO lines into a new supplier bill and post the AP journal."""

    try:
        result = await conversion_service.purchase_order_to_bill(
            company_id=company_id,
            order_id=order_id,
        )
    except Exception as exc:
        from app.core.exceptions import ValidationAppError
        from fastapi import HTTPException

        if isinstance(exc, ValidationAppError):
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        raise
    return {
        "result": jsonable_encoder(result["supplierBill"]),
        "orderId": result["orderId"],
        "posted": result["posted"],
    }


# =================== Sprint 8 — Inventory writes ===================


@router.get("/stock-adjustments")
async def list_stock_adjustments(
    company_id: str,
    repo: Annotated[StockAdjustmentRepository, Depends(get_stock_adjustment_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("inventory"))],
) -> dict:
    """Stock adjustment vouchers (§7.3)."""

    rows = await repo.list_adjustments(company_id=company_id)
    return {"result": _dump_rows(rows)}


@router.get("/stock-adjustments/{adjustment_id}")
async def get_stock_adjustment(
    company_id: str,
    adjustment_id: str,
    repo: Annotated[StockAdjustmentRepository, Depends(get_stock_adjustment_repository)],
) -> dict:
    row = await repo.get_adjustment(company_id=company_id, adjustment_id=adjustment_id)
    if row is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Stock adjustment not found")
    return {"result": jsonable_encoder(row)}


@router.post("/stock-adjustments", status_code=201)
async def create_stock_adjustment(
    company_id: str,
    body: StockAdjustmentCreateRequest,
    repo: Annotated[StockAdjustmentRepository, Depends(get_stock_adjustment_repository)],
    document_number_service: Annotated[
        DocumentNumberService, Depends(get_document_number_service)
    ],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    posting_engine: Annotated[PostingEngine, Depends(get_posting_engine)],
    _claims: Annotated[Any, Depends(require_permission("inventory.adjustments.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("inventory"))],
) -> dict:
    """Create and post a stock adjustment to inventory + GL (§7.3)."""

    from fastapi import HTTPException

    await lock_date_service.assert_not_locked(
        company_id=company_id,
        document_date=body.adjustment_date,
        document_label="stock adjustment",
    )
    voucher_number = str(
        await document_number_service.reserve_next(company_id=company_id, sequence_key="SA")
    )
    row = await repo.create_adjustment(
        company_id=company_id,
        voucher_number=voucher_number,
        adjustment_date=body.adjustment_date,
        reason=body.reason,
        notes=body.notes,
        lines=body.to_repo_lines(),
    )
    try:
        journal = await posting_engine.post_stock_adjustment(
            company_id=company_id, adjustment_id=row.id
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    refreshed = await repo.get_adjustment(
        company_id=company_id, adjustment_id=row.id
    )
    return {
        "result": jsonable_encoder(refreshed),
        "posted": True,
        "journalId": journal.id,
    }


@router.post("/stock-adjustments/{adjustment_id}/reverse")
async def reverse_stock_adjustment(
    company_id: str,
    adjustment_id: str,
    body: DocumentVoidRequest,
    reversal_service: Annotated[
        DocumentReversalService, Depends(get_document_reversal_service)
    ],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("inventory"))],
) -> dict:
    from fastapi import HTTPException

    if body.reversal_date:
        await lock_date_service.assert_not_locked(
            company_id=company_id,
            document_date=body.reversal_date,
            document_label="stock adjustment reversal",
        )
    try:
        out = await reversal_service.reverse_stock_adjustment(
            company_id=company_id,
            adjustment_id=adjustment_id,
            reversal_date=body.reversal_date,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(out)}


@router.get("/stock-transfers")
async def list_stock_transfers(
    company_id: str,
    repo: Annotated[StockTransferRepository, Depends(get_stock_transfer_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("inventory"))],
) -> dict:
    """Stock transfers (§7.2)."""

    rows = await repo.list_transfers(company_id=company_id)
    return {"result": _dump_rows(rows)}


@router.get("/stock-transfers/{transfer_id}")
async def get_stock_transfer(
    company_id: str,
    transfer_id: str,
    repo: Annotated[StockTransferRepository, Depends(get_stock_transfer_repository)],
) -> dict:
    row = await repo.get_transfer(company_id=company_id, transfer_id=transfer_id)
    if row is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Stock transfer not found")
    return {"result": jsonable_encoder(row)}


@router.post("/stock-transfers", status_code=201)
async def create_stock_transfer(
    company_id: str,
    body: StockTransferCreateRequest,
    repo: Annotated[StockTransferRepository, Depends(get_stock_transfer_repository)],
    document_number_service: Annotated[
        DocumentNumberService, Depends(get_document_number_service)
    ],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    _access: Annotated[JwtClaims, Depends(require_module_access("inventory"))],
) -> dict:
    """Create a stock transfer (§7.2)."""

    await lock_date_service.assert_not_locked(
        company_id=company_id,
        document_date=body.transfer_date,
        document_label="stock transfer",
    )
    voucher_number = str(
        await document_number_service.reserve_next(company_id=company_id, sequence_key="ST")
    )
    try:
        row = await repo.create_transfer(
            company_id=company_id,
            voucher_number=voucher_number,
            transfer_date=body.transfer_date,
            from_location_code=body.from_location_code,
            to_location_code=body.to_location_code,
            notes=body.notes,
            lines=body.to_repo_lines(),
        )
    except ValueError as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(row)}


@router.get("/product-batches")
async def list_product_batches(
    company_id: str,
    repo: Annotated[ProductBatchRepository, Depends(get_product_batch_repository)],
    product_code: str | None = Query(default=None, alias="productCode"),
) -> dict:
    """Product batches with optional product filter (§7.8)."""

    rows = await repo.list_batches(company_id=company_id, product_code=product_code)
    return {"result": _dump_rows(rows)}


@router.post("/product-batches", status_code=201)
async def create_product_batch(
    company_id: str,
    body: ProductBatchCreateRequest,
    repo: Annotated[ProductBatchRepository, Depends(get_product_batch_repository)],
) -> dict:
    row = await repo.create_batch(
        company_id=company_id,
        product_code=body.product_code,
        batch_number=body.batch_number,
        expiry_date=body.expiry_date,
        quantity_on_hand=body.quantity_on_hand,
        notes=body.notes,
    )
    return {"result": jsonable_encoder(row)}


# =================== Sprint 12 — Delivery / GRN ===================


@router.get("/delivery-notes")
async def list_delivery_notes(
    company_id: str,
    repo: Annotated[DeliveryNoteRepository, Depends(get_delivery_note_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("sales"))],
) -> dict:
    """Delivery notes (§5.6)."""

    rows = await repo.list_notes(company_id=company_id)
    return {"result": _dump_rows(rows)}


@router.get("/delivery-notes/{note_id}")
async def get_delivery_note(
    company_id: str,
    note_id: str,
    repo: Annotated[DeliveryNoteRepository, Depends(get_delivery_note_repository)],
) -> dict:
    row = await repo.get_note(company_id=company_id, note_id=note_id)
    if row is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Delivery note not found")
    return {"result": jsonable_encoder(row)}


@router.post("/delivery-notes", status_code=201)
async def create_delivery_note(
    company_id: str,
    body: DeliveryNoteCreateRequest,
    repo: Annotated[DeliveryNoteRepository, Depends(get_delivery_note_repository)],
    document_number_service: Annotated[
        DocumentNumberService, Depends(get_document_number_service)
    ],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    inventory_service: Annotated[
        InventoryQuantityService, Depends(get_inventory_quantity_service)
    ],
    stock_guard: Annotated[
        InventoryStockGuardService, Depends(get_inventory_stock_guard_service)
    ],
    _claims: Annotated[Any, Depends(require_permission("sales.orders.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("sales"))],
) -> dict:
    """Create a delivery note (§5.6)."""

    from fastapi import HTTPException

    try:
        await stock_guard.assert_delivery_stock_allowed(
            company_id=company_id,
            source_kind=body.source_kind,
            source_id=body.source_id,
            skip_stock_movement=body.skip_stock_movement,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    await lock_date_service.assert_not_locked(
        company_id=company_id,
        document_date=body.delivery_date,
        document_label="delivery note",
    )
    seq_key = body.source_kind if body.source_kind in {"GDNSI", "GDNSO"} else "GDN"
    voucher_number = str(
        await document_number_service.reserve_next(company_id=company_id, sequence_key=seq_key)
    )
    try:
        row = await repo.create_note(
            company_id=company_id,
            voucher_number=voucher_number,
            delivery_date=body.delivery_date,
            customer_id=body.customer_id,
            source_kind=body.source_kind,
            source_id=body.source_id,
            notes=body.notes,
            lines=body.to_repo_lines(),
        )
    except ValueError as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=str(exc)) from exc
    stock_issued: list[dict[str, str]] = []
    if not body.skip_stock_movement:
        stock_issued = await inventory_service.apply_delivery_note_lines(
            company_id=company_id,
            lines=row.lines or [],
        )
    return {
        "result": jsonable_encoder(row),
        "stockIssued": stock_issued,
        "stockSkipped": body.skip_stock_movement,
    }


@router.post("/delivery-notes/{note_id}/void")
async def void_delivery_note(
    company_id: str,
    note_id: str,
    reversal_service: Annotated[
        DocumentReversalService, Depends(get_document_reversal_service)
    ],
    _claims: Annotated[Any, Depends(require_permission("sales.orders.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("sales"))],
) -> dict:
    from fastapi import HTTPException

    try:
        out = await reversal_service.void_delivery_note(
            company_id=company_id, note_id=note_id
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(out)}


@router.get("/goods-receipt-notes")
async def list_goods_receipt_notes(
    company_id: str,
    repo: Annotated[GoodsReceiptNoteRepository, Depends(get_goods_receipt_note_repository)],
    _read: Annotated[JwtClaims, Depends(require_module_list_read("purchases"))],
) -> dict:
    """Goods receipt notes (§6 GRN)."""

    rows = await repo.list_notes(company_id=company_id)
    return {"result": _dump_rows(rows)}


@router.get("/goods-receipt-notes/{note_id}")
async def get_goods_receipt_note(
    company_id: str,
    note_id: str,
    repo: Annotated[GoodsReceiptNoteRepository, Depends(get_goods_receipt_note_repository)],
) -> dict:
    row = await repo.get_note(company_id=company_id, note_id=note_id)
    if row is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Goods receipt note not found")
    return {"result": jsonable_encoder(row)}


@router.post("/goods-receipt-notes", status_code=201)
async def create_goods_receipt_note(
    company_id: str,
    body: GoodsReceiptNoteCreateRequest,
    repo: Annotated[GoodsReceiptNoteRepository, Depends(get_goods_receipt_note_repository)],
    document_number_service: Annotated[
        DocumentNumberService, Depends(get_document_number_service)
    ],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    inventory_service: Annotated[
        InventoryQuantityService, Depends(get_inventory_quantity_service)
    ],
    stock_guard: Annotated[
        InventoryStockGuardService, Depends(get_inventory_stock_guard_service)
    ],
    _claims: Annotated[Any, Depends(require_permission("purchases.grn.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("purchases"))],
) -> dict:
    """Create a goods receipt note (§6)."""

    from fastapi import HTTPException

    try:
        await stock_guard.assert_grn_receipt_allowed(
            company_id=company_id,
            source_kind=body.source_kind,
            source_id=body.source_id,
            skip_stock_movement=body.skip_stock_movement,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    await lock_date_service.assert_not_locked(
        company_id=company_id,
        document_date=body.receipt_date,
        document_label="goods receipt note",
    )
    seq_key = body.source_kind if body.source_kind in {"GRNPO", "GRNVI"} else "GRN"
    voucher_number = str(
        await document_number_service.reserve_next(company_id=company_id, sequence_key=seq_key)
    )
    try:
        row = await repo.create_note(
            company_id=company_id,
            voucher_number=voucher_number,
            receipt_date=body.receipt_date,
            supplier_id=body.supplier_id,
            source_kind=body.source_kind,
            source_id=body.source_id,
            notes=body.notes,
            lines=body.to_repo_lines(),
        )
    except ValueError as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=str(exc)) from exc
    stock_applied: list[dict[str, str]] = []
    if not body.skip_stock_movement:
        stock_applied = await inventory_service.apply_grn_receipt_lines(
            company_id=company_id,
            lines=row.lines or [],
        )
    return {
        "result": jsonable_encoder(row),
        "stockApplied": stock_applied,
        "stockSkipped": body.skip_stock_movement,
    }


@router.post("/goods-receipt-notes/{note_id}/void")
async def void_goods_receipt_note(
    company_id: str,
    note_id: str,
    reversal_service: Annotated[
        DocumentReversalService, Depends(get_document_reversal_service)
    ],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    _claims: Annotated[Any, Depends(require_permission("purchases.grn.create"))],
    claims: Annotated[JwtClaims, Depends(require_module_access("purchases"))],
) -> dict:
    from fastapi import HTTPException

    try:
        out = await reversal_service.void_goods_receipt_note(
            company_id=company_id, note_id=note_id
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    grn = out.get("goodsReceiptNote")
    voucher = getattr(grn, "voucherNumber", None) if grn is not None else note_id
    await audit_service.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type="GRN_VOID",
        transaction_id=note_id,
        status="voided",
        details=f"voucher={voucher}",
    )
    return {"result": jsonable_encoder(out)}


# =================== Sprint 14 — Post-Dated Cheques ===================


@router.get("/pdc-received/{cheque_id}")
async def get_pdc_received(
    company_id: str,
    cheque_id: str,
    repo: Annotated[PdcReceivedRepository, Depends(get_pdc_received_repository)],
) -> dict:
    from fastapi import HTTPException

    row = await repo.get_cheque(company_id=company_id, cheque_id=cheque_id)
    if row is None:
        raise HTTPException(status_code=404, detail="PDC not found")
    return {"result": jsonable_encoder(row)}


@router.get("/pdc-received")
async def list_pdc_received(
    company_id: str,
    repo: Annotated[PdcReceivedRepository, Depends(get_pdc_received_repository)],
    status: str | None = Query(default=None),
) -> dict:
    """Post-dated cheques received (§5.7)."""

    rows = await repo.list_cheques(company_id=company_id, status=status)
    return {"result": _dump_rows(rows)}


@router.post("/pdc-received", status_code=201)
async def create_pdc_received(
    company_id: str,
    body: PdcReceivedCreateRequest,
    repo: Annotated[PdcReceivedRepository, Depends(get_pdc_received_repository)],
    document_number_service: Annotated[
        DocumentNumberService, Depends(get_document_number_service)
    ],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    _claims: Annotated[Any, Depends(require_permission("bank.payments.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("bank"))],
) -> dict:
    await lock_date_service.assert_not_locked(
        company_id=company_id,
        document_date=body.received_date,
        document_label="PDC received",
    )
    voucher_number = str(
        await document_number_service.reserve_next(company_id=company_id, sequence_key="PDCR")
    )
    row = await repo.create_cheque(
        company_id=company_id,
        voucher_number=voucher_number,
        cheque_number=body.cheque_number,
        bank_name=body.bank_name,
        customer_id=body.customer_id,
        received_date=body.received_date,
        cheque_date=body.cheque_date,
        amount=body.amount,
        notes=body.notes,
    )
    return {"result": jsonable_encoder(row)}


@router.put("/pdc-received/{cheque_id}/status")
async def update_pdc_received_status(
    company_id: str,
    cheque_id: str,
    body: PdcStatusUpdateRequest,
    repo: Annotated[PdcReceivedRepository, Depends(get_pdc_received_repository)],
    _claims: Annotated[Any, Depends(require_permission("bank.payments.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("bank"))],
) -> dict:
    try:
        row = await repo.update_status(
            company_id=company_id, cheque_id=cheque_id, status=body.status
        )
    except ValueError as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(row)}


@router.post("/pdc-received/{cheque_id}/present")
async def present_pdc_received(
    company_id: str,
    cheque_id: str,
    service: Annotated[PdcService, Depends(get_pdc_service)],
    _claims: Annotated[Any, Depends(require_permission("bank.payments.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("bank"))],
) -> dict:
    from fastapi import HTTPException

    try:
        row = await service.present_received(company_id=company_id, cheque_id=cheque_id)
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(row)}


@router.post("/pdc-received/{cheque_id}/clear")
async def clear_pdc_received(
    company_id: str,
    cheque_id: str,
    body: PdcClearReceivedRequest,
    service: Annotated[PdcService, Depends(get_pdc_service)],
    _claims: Annotated[Any, Depends(require_permission("bank.payments.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("bank"))],
) -> dict:
    from fastapi import HTTPException

    try:
        out = await service.clear_received(
            company_id=company_id,
            cheque_id=cheque_id,
            bank_account_id=body.bank_account_id,
            clear_date=body.clear_date,
            auto_fifo=body.auto_fifo,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(out)}


@router.post("/pdc-received/{cheque_id}/bounce")
async def bounce_pdc_received(
    company_id: str,
    cheque_id: str,
    service: Annotated[PdcService, Depends(get_pdc_service)],
    _claims: Annotated[Any, Depends(require_permission("bank.payments.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("bank"))],
) -> dict:
    from fastapi import HTTPException

    try:
        row = await service.bounce_received(company_id=company_id, cheque_id=cheque_id)
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(row)}


@router.get("/pdc-issued/{cheque_id}")
async def get_pdc_issued(
    company_id: str,
    cheque_id: str,
    repo: Annotated[PdcIssuedRepository, Depends(get_pdc_issued_repository)],
) -> dict:
    from fastapi import HTTPException

    row = await repo.get_cheque(company_id=company_id, cheque_id=cheque_id)
    if row is None:
        raise HTTPException(status_code=404, detail="PDC not found")
    return {"result": jsonable_encoder(row)}


@router.get("/pdc-issued")
async def list_pdc_issued(
    company_id: str,
    repo: Annotated[PdcIssuedRepository, Depends(get_pdc_issued_repository)],
    status: str | None = Query(default=None),
) -> dict:
    """Post-dated cheques issued (§6.1)."""

    rows = await repo.list_cheques(company_id=company_id, status=status)
    return {"result": _dump_rows(rows)}


@router.post("/pdc-issued", status_code=201)
async def create_pdc_issued(
    company_id: str,
    body: PdcIssuedCreateRequest,
    repo: Annotated[PdcIssuedRepository, Depends(get_pdc_issued_repository)],
    document_number_service: Annotated[
        DocumentNumberService, Depends(get_document_number_service)
    ],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    _claims: Annotated[Any, Depends(require_permission("bank.payments.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("bank"))],
) -> dict:
    await lock_date_service.assert_not_locked(
        company_id=company_id,
        document_date=body.issued_date,
        document_label="PDC issued",
    )
    voucher_number = str(
        await document_number_service.reserve_next(company_id=company_id, sequence_key="PDCI")
    )
    row = await repo.create_cheque(
        company_id=company_id,
        voucher_number=voucher_number,
        cheque_number=body.cheque_number,
        bank_account_id=body.bank_account_id,
        supplier_id=body.supplier_id,
        issued_date=body.issued_date,
        cheque_date=body.cheque_date,
        amount=body.amount,
        notes=body.notes,
    )
    return {"result": jsonable_encoder(row)}


@router.put("/pdc-issued/{cheque_id}/status")
async def update_pdc_issued_status(
    company_id: str,
    cheque_id: str,
    body: PdcStatusUpdateRequest,
    repo: Annotated[PdcIssuedRepository, Depends(get_pdc_issued_repository)],
    _claims: Annotated[Any, Depends(require_permission("bank.payments.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("bank"))],
) -> dict:
    try:
        row = await repo.update_status(
            company_id=company_id, cheque_id=cheque_id, status=body.status
        )
    except ValueError as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(row)}


@router.post("/pdc-issued/{cheque_id}/present")
async def present_pdc_issued(
    company_id: str,
    cheque_id: str,
    service: Annotated[PdcService, Depends(get_pdc_service)],
    _claims: Annotated[Any, Depends(require_permission("bank.payments.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("bank"))],
) -> dict:
    from fastapi import HTTPException

    try:
        row = await service.present_issued(company_id=company_id, cheque_id=cheque_id)
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(row)}


@router.post("/pdc-issued/{cheque_id}/clear")
async def clear_pdc_issued(
    company_id: str,
    cheque_id: str,
    body: PdcClearIssuedRequest,
    service: Annotated[PdcService, Depends(get_pdc_service)],
    _claims: Annotated[Any, Depends(require_permission("bank.payments.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("bank"))],
) -> dict:
    from fastapi import HTTPException

    try:
        out = await service.clear_issued(
            company_id=company_id,
            cheque_id=cheque_id,
            clear_date=body.clear_date,
            auto_fifo=body.auto_fifo,
        )
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(out)}


@router.post("/pdc-issued/{cheque_id}/bounce")
async def bounce_pdc_issued(
    company_id: str,
    cheque_id: str,
    service: Annotated[PdcService, Depends(get_pdc_service)],
    _claims: Annotated[Any, Depends(require_permission("bank.payments.create"))],
    _access: Annotated[JwtClaims, Depends(require_module_access("bank"))],
) -> dict:
    from fastapi import HTTPException

    try:
        row = await service.bounce_issued(company_id=company_id, cheque_id=cheque_id)
    except ValidationAppError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": jsonable_encoder(row)}


# =================== Sprint 11 — Reports breadth ===================


def _date_query(
    date_from: datetime | None, date_to: datetime | None
) -> tuple[datetime | None, datetime | None]:
    return date_from, date_to


@router.get("/reports/sale-invoices-by-date")
async def report_sale_invoices_by_date(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    svc: Annotated[ExtendedReportsService, Depends(get_extended_reports_service)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    return {"result": await svc.sale_invoices_by_date(
        company_id=company_id, date_from=date_from, date_to=date_to
    )}


@router.get("/reports/sale-invoices-by-customer")
async def report_sale_invoices_by_customer(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    svc: Annotated[ExtendedReportsService, Depends(get_extended_reports_service)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    return {"result": await svc.sale_invoices_by_customer(
        company_id=company_id, date_from=date_from, date_to=date_to
    )}


@router.get("/reports/sale-summary-by-date")
async def report_sale_summary_by_date(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    svc: Annotated[ExtendedReportsService, Depends(get_extended_reports_service)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    return {"result": await svc.sale_summary_by_date(
        company_id=company_id, date_from=date_from, date_to=date_to
    )}


@router.get("/reports/customer-performance")
async def report_customer_performance(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    svc: Annotated[ExtendedReportsService, Depends(get_extended_reports_service)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    return {"result": await svc.customer_performance(
        company_id=company_id, date_from=date_from, date_to=date_to
    )}


@router.get("/reports/customer-balances")
async def report_customer_balances(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    svc: Annotated[ExtendedReportsService, Depends(get_extended_reports_service)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    return {"result": await svc.customer_balances(
        company_id=company_id, date_from=date_from, date_to=date_to
    )}


@router.get("/reports/purchase-bills-by-date")
async def report_purchase_bills_by_date(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    svc: Annotated[ExtendedReportsService, Depends(get_extended_reports_service)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    return {"result": await svc.purchase_bills_by_date(
        company_id=company_id, date_from=date_from, date_to=date_to
    )}


@router.get("/reports/purchase-bills-by-supplier")
async def report_purchase_bills_by_supplier(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    svc: Annotated[ExtendedReportsService, Depends(get_extended_reports_service)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    return {"result": await svc.purchase_bills_by_supplier(
        company_id=company_id, date_from=date_from, date_to=date_to
    )}


@router.get("/reports/product-sale-detail")
async def report_product_sale_detail(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    svc: Annotated[ExtendedReportsService, Depends(get_extended_reports_service)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    return {"result": await svc.product_sale_detail(
        company_id=company_id, date_from=date_from, date_to=date_to
    )}


@router.get("/reports/product-purchase-detail")
async def report_product_purchase_detail(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    svc: Annotated[ExtendedReportsService, Depends(get_extended_reports_service)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    return {"result": await svc.product_purchase_detail(
        company_id=company_id, date_from=date_from, date_to=date_to
    )}


@router.get("/reports/stock-quantity")
async def report_stock_quantity(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    svc: Annotated[ExtendedReportsService, Depends(get_extended_reports_service)],
) -> dict:
    return {"result": await svc.stock_quantity(company_id=company_id)}


@router.get("/reports/out-of-stock")
async def report_out_of_stock(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    svc: Annotated[ExtendedReportsService, Depends(get_extended_reports_service)],
) -> dict:
    return {"result": await svc.out_of_stock(company_id=company_id)}


@router.get("/reports/bank-payments-list")
async def report_bank_payments(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    svc: Annotated[ExtendedReportsService, Depends(get_extended_reports_service)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    return {"result": await svc.bank_payments_report(
        company_id=company_id, date_from=date_from, date_to=date_to
    )}


@router.get("/reports/advanced-stock-quantity")
async def report_advanced_stock_quantity(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    svc: Annotated[ExtendedReportsService, Depends(get_extended_reports_service)],
) -> dict:
    data = await svc.advanced_stock_quantity(company_id=company_id)
    return {"result": data["rows"]}


@router.get("/reports/multi-unit-price-list")
async def report_multi_unit_price_list(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    svc: Annotated[ExtendedReportsService, Depends(get_extended_reports_service)],
) -> dict:
    data = await svc.multi_unit_price_list(company_id=company_id)
    return {"result": data["rows"]}


@router.get("/reports/sale-summary-by-field")
async def report_sale_summary_by_field(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    svc: Annotated[ExtendedReportsService, Depends(get_extended_reports_service)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
    group_by_field: str = Query(default="productCode", alias="groupByField"),
) -> dict:
    data = await svc.sale_summary_by_field(
        company_id=company_id,
        date_from=date_from,
        date_to=date_to,
        group_by_field=group_by_field,
    )
    return {"result": data["rows"]}


@router.get("/reports/customer-field-activity")
async def report_customer_field_activity(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    svc: Annotated[ExtendedReportsService, Depends(get_extended_reports_service)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    data = await svc.customer_field_activity_summary(
        company_id=company_id, date_from=date_from, date_to=date_to
    )
    return {"result": data["rows"]}


@router.get("/reports/bank-account-balances")
async def report_bank_account_balances(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
    as_of_date: datetime | None = Query(default=None, alias="asOfDate"),
) -> dict:
    from app.services.report_query_service import ReportQueryService

    criteria = {"dateTo": as_of_date.isoformat()} if as_of_date else {}
    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="BANK_BAL", criteria=criteria
    )
    return {"result": rows}


@router.get("/reports/bank-cash-flow-monthly")
async def report_bank_cash_flow_monthly(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    from app.services.report_query_service import ReportQueryService

    criteria: dict = {}
    if date_from:
        criteria["dateFrom"] = date_from.isoformat()
    if date_to:
        criteria["dateTo"] = date_to.isoformat()
    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="BANK_CF", criteria=criteria
    )
    return {"result": rows}


@router.get("/reports/assembly-job-cost-summary")
async def report_assembly_job_cost(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
) -> dict:
    from app.services.report_query_service import ReportQueryService

    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="ASM_JOB", criteria={}
    )
    return {"result": rows}


@router.get("/reports/project-payments")
async def report_project_payments(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    from app.services.report_query_service import ReportQueryService

    criteria: dict = {}
    if date_from:
        criteria["dateFrom"] = date_from.isoformat()
    if date_to:
        criteria["dateTo"] = date_to.isoformat()
    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="PRJ_PAY", criteria=criteria
    )
    return {"result": rows}


@router.get("/reports/bank-receipts")
async def report_bank_receipts(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    from app.services.report_query_service import ReportQueryService

    criteria: dict = {}
    if date_from:
        criteria["dateFrom"] = date_from.isoformat()
    if date_to:
        criteria["dateTo"] = date_to.isoformat()
    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="BANK_REC", criteria=criteria
    )
    return {"result": rows}


@router.get("/reports/bank-transfers")
async def report_bank_transfers(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    from app.services.report_query_service import ReportQueryService

    criteria: dict = {}
    if date_from:
        criteria["dateFrom"] = date_from.isoformat()
    if date_to:
        criteria["dateTo"] = date_to.isoformat()
    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="BANK_XFR", criteria=criteria
    )
    return {"result": rows}


@router.get("/reports/bank-activity-summary")
async def report_bank_activity_summary(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    from app.services.report_query_service import ReportQueryService

    criteria: dict = {}
    if date_from:
        criteria["dateFrom"] = date_from.isoformat()
    if date_to:
        criteria["dateTo"] = date_to.isoformat()
    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="BANK_ACT", criteria=criteria
    )
    return {"result": rows}


@router.get("/reports/assembly-templates")
async def report_assembly_templates(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
) -> dict:
    from app.services.report_query_service import ReportQueryService

    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="ASM_TPL", criteria={}
    )
    return {"result": rows}


@router.get("/reports/supplier-balances")
async def report_supplier_balances(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    from app.services.report_query_service import ReportQueryService

    criteria: dict = {}
    if date_from:
        criteria["dateFrom"] = date_from.isoformat()
    if date_to:
        criteria["dateTo"] = date_to.isoformat()
    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="067", criteria=criteria
    )
    return {"result": rows}


@router.get("/reports/assembly-wip")
async def report_assembly_wip(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
) -> dict:
    from app.services.report_query_service import ReportQueryService

    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="ASM_WIP", criteria={}
    )
    return {"result": rows}


@router.get("/reports/assembly-component-cost")
async def report_assembly_component_cost(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
) -> dict:
    from app.services.report_query_service import ReportQueryService

    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="ASM_COMP", criteria={}
    )
    return {"result": rows}


@router.get("/reports/low-stock")
async def report_low_stock(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
) -> dict:
    from app.services.report_query_service import ReportQueryService

    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="083", criteria={}
    )
    return {"result": rows}


@router.get("/reports/stock-valuation")
async def report_stock_valuation(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
) -> dict:
    from app.services.report_query_service import ReportQueryService

    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="148", criteria={}
    )
    return {"result": rows}


@router.get("/reports/stock-movement")
async def report_stock_movement(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    from app.services.report_query_service import ReportQueryService

    criteria: dict = {}
    if date_from:
        criteria["dateFrom"] = date_from.isoformat()
    if date_to:
        criteria["dateTo"] = date_to.isoformat()
    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="174", criteria=criteria
    )
    return {"result": rows}


@router.get("/reports/price-list")
async def report_price_list(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
) -> dict:
    from app.services.report_query_service import ReportQueryService

    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="079", criteria={}
    )
    return {"result": rows}


@router.get("/reports/sale-summary-by-customer")
async def report_sale_summary_by_customer(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    from app.services.report_query_service import ReportQueryService

    criteria: dict = {}
    if date_from:
        criteria["dateFrom"] = date_from.isoformat()
    if date_to:
        criteria["dateTo"] = date_to.isoformat()
    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="033", criteria=criteria
    )
    return {"result": rows}


@router.get("/reports/invoice-line-detail")
async def report_invoice_line_detail(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    from app.services.report_query_service import ReportQueryService

    criteria: dict = {}
    if date_from:
        criteria["dateFrom"] = date_from.isoformat()
    if date_to:
        criteria["dateTo"] = date_to.isoformat()
    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="030", criteria=criteria
    )
    return {"result": rows}


@router.get("/reports/invoice-line-by-customer")
async def report_invoice_line_by_customer(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
    customer_id: str | None = Query(default=None, alias="customerId"),
) -> dict:
    from app.services.report_query_service import ReportQueryService

    criteria: dict = {}
    if date_from:
        criteria["dateFrom"] = date_from.isoformat()
    if date_to:
        criteria["dateTo"] = date_to.isoformat()
    if customer_id:
        criteria["customerId"] = customer_id
    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="031", criteria=criteria
    )
    return {"result": rows}


@router.get("/reports/customer-list")
async def report_customer_list(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
) -> dict:
    from app.services.report_query_service import ReportQueryService

    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="035", criteria={}
    )
    return {"result": rows}


@router.get("/reports/customer-outstanding")
async def report_customer_outstanding(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
    customer_id: str | None = Query(default=None, alias="customerId"),
) -> dict:
    from app.services.report_query_service import ReportQueryService

    criteria: dict = {}
    if date_from:
        criteria["dateFrom"] = date_from.isoformat()
    if date_to:
        criteria["dateTo"] = date_to.isoformat()
    if customer_id:
        criteria["customerId"] = customer_id
    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="143", criteria=criteria
    )
    return {"result": rows}


@router.get("/reports/customer-products")
async def report_customer_products(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
    customer_id: str | None = Query(default=None, alias="customerId"),
) -> dict:
    from app.services.report_query_service import ReportQueryService

    criteria: dict = {}
    if date_from:
        criteria["dateFrom"] = date_from.isoformat()
    if date_to:
        criteria["dateTo"] = date_to.isoformat()
    if customer_id:
        criteria["customerId"] = customer_id
    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="145", criteria=criteria
    )
    return {"result": rows}


@router.get("/reports/financial-monthly-balances")
async def report_financial_monthly_balances(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    from app.services.report_query_service import ReportQueryService

    criteria: dict = {}
    if date_from:
        criteria["dateFrom"] = date_from.isoformat()
    if date_to:
        criteria["dateTo"] = date_to.isoformat()
    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="FIN_MTB", criteria=criteria
    )
    return {"result": rows}


@router.get("/reports/financial-trial-balance-by-month")
async def report_financial_trial_balance_by_month(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
    date_to: datetime | None = Query(default=None, alias="dateTo"),
    period_count: int | None = Query(default=None, alias="periodCount"),
) -> dict:
    from app.services.report_query_service import ReportQueryService

    criteria: dict = {}
    if date_to:
        criteria["dateTo"] = date_to.isoformat()
    if period_count is not None:
        criteria["periodCount"] = period_count
    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="FIN_TB12", criteria=criteria
    )
    return {"result": rows}


@router.get("/reports/products-list")
async def report_products_list(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
) -> dict:
    from app.services.report_query_service import ReportQueryService

    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="078", criteria={}
    )
    return {"result": rows}


@router.get("/reports/product-performance")
async def report_product_performance(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    from app.services.report_query_service import ReportQueryService

    criteria: dict = {}
    if date_from:
        criteria["dateFrom"] = date_from.isoformat()
    if date_to:
        criteria["dateTo"] = date_to.isoformat()
    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="162", criteria=criteria
    )
    return {"result": rows}


@router.get("/reports/product-sale-summary")
async def report_product_sale_summary(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    from app.services.report_query_service import ReportQueryService

    criteria: dict = {}
    if date_from:
        criteria["dateFrom"] = date_from.isoformat()
    if date_to:
        criteria["dateTo"] = date_to.isoformat()
    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="088", criteria=criteria
    )
    return {"result": rows}


@router.get("/reports/product-purchase-summary")
async def report_product_purchase_summary(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    from app.services.report_query_service import ReportQueryService

    criteria: dict = {}
    if date_from:
        criteria["dateFrom"] = date_from.isoformat()
    if date_to:
        criteria["dateTo"] = date_to.isoformat()
    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="089", criteria=criteria
    )
    return {"result": rows}


@router.get("/reports/bank-payment-receipt-data")
async def report_bank_payment_receipt_data(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    from app.services.report_query_service import ReportQueryService

    criteria: dict = {}
    if date_from:
        criteria["dateFrom"] = date_from.isoformat()
    if date_to:
        criteria["dateTo"] = date_to.isoformat()
    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="300", criteria=criteria
    )
    return {"result": rows}


@router.get("/reports/stock-transfer-detail")
async def report_stock_transfer_detail(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    from app.services.report_query_service import ReportQueryService

    criteria: dict = {}
    if date_from:
        criteria["dateFrom"] = date_from.isoformat()
    if date_to:
        criteria["dateTo"] = date_to.isoformat()
    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="STOCK_XFR", criteria=criteria
    )
    return {"result": rows}


@router.get("/reports/product-activity-summary")
async def report_product_activity_summary(
    company_id: str,
    _reports: Annotated[JwtClaims, Depends(require_module_reports("financial"))],
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
) -> dict:
    from app.services.report_query_service import ReportQueryService

    criteria: dict = {}
    if date_from:
        criteria["dateFrom"] = date_from.isoformat()
    if date_to:
        criteria["dateTo"] = date_to.isoformat()
    rows = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id, report_id="PROD_ACT", criteria=criteria
    )
    return {"result": rows}


from app.api.routes.assistant import router as assistant_router
from app.api.routes.access_control_routes import router as access_control_router

router.include_router(access_control_router)
router.include_router(assistant_router)
