"""FastAPI dependency wiring for Prisma, services, and auth claims."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, Any, AsyncIterator

from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.database import get_prisma_client, get_read_prisma_client
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_token
from app.repositories.auth_otp_repository import AuthOtpRepository
from app.repositories.approval_policy_repository import ApprovalPolicyRepository
from app.repositories.approval_request_repository import ApprovalRequestRepository
from app.repositories.attachment_repository import AttachmentRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.bank_repository import BankRepository
from app.repositories.coa_repository import CoaRepository
from app.repositories.company_bootstrap_repository import CompanyBootstrapRepository
from app.repositories.company_repository import CompanyRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.location_repository import LocationRepository
from app.repositories.budget_repository import BudgetRepository
from app.repositories.document_number_repository import DocumentNumberRepository
from app.repositories.assembly_repository import AssemblyRepository
from app.repositories.fx_revaluation_repository import FxRevaluationRepository
from app.repositories.fbr_repository import FbrRepository
from app.repositories.payment_gateway_repository import PaymentGatewayRepository
from app.repositories.goods_issue_repository import GoodsIssueRepository
from app.repositories.import_job_repository import ImportJobRepository
from app.repositories.outbox_repository import OutboxRepository
from app.repositories.report_run_repository import ReportRunRepository
from app.repositories.bank_reconciliation_repository import BankReconciliationRepository
from app.repositories.dashboard_repository import DashboardRepository
from app.repositories.journal_repository import JournalRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.business_information_repository import BusinessInformationRepository
from app.repositories.bank_receipt_repository import BankReceiptRepository
from app.repositories.bank_transfer_repository import BankTransferRepository
from app.repositories.lock_date_repository import LockDateRepository
from app.repositories.purchase_order_repository import PurchaseOrderRepository
from app.repositories.quotation_repository import QuotationRepository
from app.repositories.sales_credit_repository import SalesCreditRepository
from app.repositories.sales_invoice_repository import SalesInvoiceRepository
from app.repositories.sales_order_repository import SalesOrderRepository
from app.repositories.sales_receipt_repository import SalesReceiptRepository
from app.repositories.smart_settings_repository import SmartSettingsRepository
from app.repositories.supplier_bill_repository import SupplierBillRepository
from app.repositories.delivery_repository import (
    DeliveryNoteRepository,
    GoodsReceiptNoteRepository,
)
from app.repositories.inventory_repository import (
    ProductBatchRepository,
    StockAdjustmentRepository,
    StockTransferRepository,
)
from app.repositories.pdc_repository import (
    PdcIssuedRepository,
    PdcReceivedRepository,
)
from app.repositories.supplier_credit_repository import SupplierCreditRepository
from app.repositories.supplier_payment_repository import SupplierPaymentRepository
from app.repositories.supplier_repository import SupplierRepository
from app.repositories.taxes_config_repository import TaxesConfigRepository
from app.repositories.transaction_template_repository import TransactionTemplateRepository
from app.repositories.recurring_schedule_repository import RecurringScheduleRepository
from app.services.batch_document_service import BatchDocumentService
from app.services.advance_return_service import AdvanceReturnService
from app.services.recurring_schedule_service import RecurringScheduleService
from app.repositories.membership_repository import MembershipRepository
from app.repositories.membership_role_repository import MembershipRoleRepository
from app.repositories.role_permission_repository import RolePermissionRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.services.approval_engine_service import ApprovalEngineService
from app.services.approval_policy_service import ApprovalPolicyService
from app.services.budget_service import BudgetService
from app.services.assembly_service import AssemblyService
from app.services.fx_revaluation_service import FxRevaluationService
from app.services.fbr_service import FbrService
from app.services.kuickpay_service import KuickpayService
from app.services.paypro_service import PayproService
from app.services.clickhouse_schema_service import ClickHouseSchemaService
from app.services.grni_service import GrniService
from app.services.bank_payment_service import BankPaymentService
from app.services.attachment_service import AttachmentService
from app.services.audit_log_service import AuditLogService
from app.services.auth_service import AuthService
from app.services.user_invite_service import UserInviteService
from app.services.invite_email_template_service import InviteEmailTemplateService
from app.services.email_service import EmailService
from app.services.document_number_service import DocumentNumberService
from app.services.activity_service import ActivityService
from app.services.my_tasks_service import MyTasksService
from app.services.app_settings_service import AppSettingsService
from app.services.aging_service import AgingService
from app.services.smart_settings_runtime import SmartSettingsRuntime
from app.services.allocation_service import AllocationService
from app.services.conversion_service import ConversionService
from app.services.extended_reports_service import ExtendedReportsService
from app.services.import_job_service import ImportJobService
from app.services.pdc_service import PdcService
from app.services.journal_service import JournalService
from app.services.lock_date_service import LockDateService
from app.services.posting_engine import PostingEngine
from app.services.posting_prerequisites_service import PostingPrerequisitesService
from app.services.posting_service import PostingService
from app.services.permission_service import PermissionService
from app.services.effective_permission_service import EffectivePermissionService
from app.services.access_control_service import AccessControlService
from app.services.field_masking_service import FieldMaskingService
from app.services.module_entitlement_service import ModuleEntitlementService
from app.services.module_access_service import ModuleAccessService
from app.services.custom_field_service import CustomFieldService
from app.services.product_service import ProductService
from app.services.product_uom_service import ProductUomService
from app.services.document_reversal_service import DocumentReversalService
from app.services.inventory_quantity_service import InventoryQuantityService
from app.services.inventory_stock_guard_service import InventoryStockGuardService
from app.services.subscription_billing_service import SubscriptionBillingService
from app.services.advance_users_service import AdvanceUsersService
from app.services.sales_invoice_email_service import SalesInvoiceEmailService
from app.services.bank_reconciliation_service import BankReconciliationService
from app.services.outbox_worker_service import OutboxWorkerService
from app.services.clickhouse_export_service import ClickHouseExportService
from app.services.report_service import ReportService
from app.services.security_audit_service import SecurityAuditService
from app.services.subledger_tieout_service import SubledgerTieoutService
from app.services.tax_calculation_service import TaxCalculationService
from app.services.auto_code_service import AutoCodeService
from app.services.last_rate_service import LastRateService
from prisma_generated import Prisma

_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True, slots=True)
class JwtClaims:
    """Resolved subject and tenant from access token."""

    user_id: str
    company_id: str


async def get_prisma() -> AsyncIterator[Prisma]:
    """Yield connected Prisma client (singleton)."""

    yield get_prisma_client()


async def get_read_prisma() -> AsyncIterator[Prisma]:
    """Yield read-replica Prisma when configured, else primary."""

    yield get_read_prisma_client()


def get_outbox_repository(prisma: Annotated[Prisma, Depends(get_prisma)]) -> OutboxRepository:
    return OutboxRepository(prisma)


def get_report_run_repository(prisma: Annotated[Prisma, Depends(get_prisma)]) -> ReportRunRepository:
    return ReportRunRepository(prisma)


def get_clickhouse_export_service() -> ClickHouseExportService:
    return ClickHouseExportService()


def get_report_service(
    report_run_repository: Annotated[ReportRunRepository, Depends(get_report_run_repository)],
    outbox_repository: Annotated[OutboxRepository, Depends(get_outbox_repository)],
    clickhouse_export_service: Annotated[
        ClickHouseExportService, Depends(get_clickhouse_export_service)
    ],
) -> ReportService:
    return ReportService(
        report_run_repository=report_run_repository,
        outbox_repository=outbox_repository,
        clickhouse_export_service=clickhouse_export_service,
    )


def get_outbox_worker_service(
    outbox_repository: Annotated[OutboxRepository, Depends(get_outbox_repository)],
    import_job_repository: Annotated[ImportJobRepository, Depends(get_import_job_repository)],
    report_run_repository: Annotated[ReportRunRepository, Depends(get_report_run_repository)],
    audit_log_repository: Annotated[AuditLogRepository, Depends(get_audit_log_repository)],
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> OutboxWorkerService:
    return OutboxWorkerService(
        outbox_repository=outbox_repository,
        import_job_repository=import_job_repository,
        report_run_repository=report_run_repository,
        audit_log_repository=audit_log_repository,
        prisma=prisma,
    )


def get_bank_reconciliation_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> BankReconciliationRepository:
    return BankReconciliationRepository(prisma)


def get_bank_reconciliation_service(
    prisma: Annotated[Prisma, Depends(get_prisma)],
    reconciliation_repository: Annotated[
        BankReconciliationRepository, Depends(get_bank_reconciliation_repository)
    ],
    bank_repository: Annotated[BankRepository, Depends(get_bank_repository)],
) -> BankReconciliationService:
    return BankReconciliationService(
        prisma=prisma,
        reconciliation_repository=reconciliation_repository,
        bank_repository=bank_repository,
    )


def get_subledger_tieout_service(
    prisma: Annotated[Prisma, Depends(get_prisma)],
    smart_settings_repository: Annotated[
        SmartSettingsRepository, Depends(get_smart_settings_repository)
    ],
) -> SubledgerTieoutService:
    return SubledgerTieoutService(
        prisma=prisma,
        smart_settings_repository=smart_settings_repository,
    )


def get_user_repository(prisma: Annotated[Prisma, Depends(get_prisma)]) -> UserRepository:
    """User table repository."""

    return UserRepository(prisma)


def get_company_repository(prisma: Annotated[Prisma, Depends(get_prisma)]) -> CompanyRepository:
    """Company and membership repository."""

    return CompanyRepository(prisma)


def get_company_bootstrap_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> CompanyBootstrapRepository:
    """Default tenant configuration rows."""

    return CompanyBootstrapRepository(prisma)


def get_auth_otp_repository(prisma: Annotated[Prisma, Depends(get_prisma)]) -> AuthOtpRepository:
    """Email OTP challenge persistence."""

    return AuthOtpRepository(prisma)


def get_email_service() -> EmailService:
    """Transactional email (SMTP)."""

    return EmailService()


def get_auth_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    company_repository: Annotated[CompanyRepository, Depends(get_company_repository)],
    bootstrap_repository: Annotated[CompanyBootstrapRepository, Depends(get_company_bootstrap_repository)],
    otp_repository: Annotated[AuthOtpRepository, Depends(get_auth_otp_repository)],
    email_service: Annotated[EmailService, Depends(get_email_service)],
) -> AuthService:
    """Sign-up and login orchestrator."""

    return AuthService(
        user_repository=user_repository,
        company_repository=company_repository,
        bootstrap_repository=bootstrap_repository,
        otp_repository=otp_repository,
        email_service=email_service,
    )


def get_invite_email_template_service(
    smart_settings_repository: Annotated[
        SmartSettingsRepository, Depends(get_smart_settings_repository)
    ],
) -> InviteEmailTemplateService:
    return InviteEmailTemplateService(smart_settings_repository=smart_settings_repository)


def get_user_invite_service(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    company_repository: Annotated[CompanyRepository, Depends(get_company_repository)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    membership_repository: Annotated[
        MembershipRepository, Depends(get_membership_repository)
    ],
    email_service: Annotated[EmailService, Depends(get_email_service)],
    template_service: Annotated[
        InviteEmailTemplateService, Depends(get_invite_email_template_service)
    ],
) -> UserInviteService:
    """Invite follow-up email after membership create."""

    return UserInviteService(
        auth_service=auth_service,
        company_repository=company_repository,
        user_repository=user_repository,
        membership_repository=membership_repository,
        email_service=email_service,
        template_service=template_service,
    )


def get_attachment_repository(prisma: Annotated[Prisma, Depends(get_prisma)]) -> AttachmentRepository:
    """Attachment persistence."""

    return AttachmentRepository(prisma)


def get_attachment_service(
    repo: Annotated[AttachmentRepository, Depends(get_attachment_repository)],
) -> AttachmentService:
    """Attachment orchestration."""

    return AttachmentService(attachment_repository=repo)


def get_document_number_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> DocumentNumberRepository:
    """Atomic counters."""

    return DocumentNumberRepository(prisma)


def get_document_number_service(
    repo: Annotated[DocumentNumberRepository, Depends(get_document_number_repository)],
) -> DocumentNumberService:
    """Numbering facade."""

    return DocumentNumberService(document_number_repository=repo)


def get_import_job_repository(prisma: Annotated[Prisma, Depends(get_prisma)]) -> ImportJobRepository:
    """Import job persistence."""

    return ImportJobRepository(prisma)


def get_import_job_service(
    repo: Annotated[ImportJobRepository, Depends(get_import_job_repository)],
    outbox_repository: Annotated[OutboxRepository, Depends(get_outbox_repository)],
) -> ImportJobService:
    """Import job orchestration."""

    return ImportJobService(
        import_job_repository=repo,
        outbox_repository=outbox_repository,
    )


def get_audit_log_repository(prisma: Annotated[Prisma, Depends(get_prisma)]) -> AuditLogRepository:
    """Audit trail persistence."""

    return AuditLogRepository(prisma)


def get_audit_log_service(
    repo: Annotated[AuditLogRepository, Depends(get_audit_log_repository)],
) -> AuditLogService:
    """Audit log orchestration."""

    return AuditLogService(audit_log_repository=repo)


def get_security_audit_service(
    repo: Annotated[AuditLogRepository, Depends(get_audit_log_repository)],
) -> SecurityAuditService:
    return SecurityAuditService(audit_log_repository=repo)


def get_approval_policy_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> ApprovalPolicyRepository:
    """Approval policy persistence."""

    return ApprovalPolicyRepository(prisma)


def get_approval_policy_service(
    repo: Annotated[ApprovalPolicyRepository, Depends(get_approval_policy_repository)],
) -> ApprovalPolicyService:
    """Approval policy orchestration."""

    return ApprovalPolicyService(approval_policy_repository=repo)


def get_journal_repository(prisma: Annotated[Prisma, Depends(get_prisma)]) -> JournalRepository:
    """Journal persistence."""

    return JournalRepository(prisma)


def get_read_journal_repository(
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
) -> JournalRepository:
    """Journal reads routed to read replica when available."""

    return JournalRepository(prisma)


def get_dashboard_repository(
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
) -> DashboardRepository:
    return DashboardRepository(prisma)


def get_read_aging_service(
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
) -> AgingService:
    return AgingService(prisma)


def get_journal_service(
    journal_repository: Annotated[JournalRepository, Depends(get_journal_repository)],
    document_number_service: Annotated[DocumentNumberService, Depends(get_document_number_service)],
    coa_repository: Annotated[CoaRepository, Depends(get_coa_repository)],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
) -> JournalService:
    """Journal orchestration."""

    return JournalService(
        journal_repository=journal_repository,
        document_number_service=document_number_service,
        coa_repository=coa_repository,
        lock_date_service=lock_date_service,
    )


def get_inventory_quantity_service(
    batch_repository: Annotated[
        ProductBatchRepository, Depends(get_product_batch_repository)
    ],
) -> InventoryQuantityService:
    return InventoryQuantityService(batches=batch_repository)


def get_inventory_stock_guard_service(
    delivery_note_repository: Annotated[
        DeliveryNoteRepository, Depends(get_delivery_note_repository)
    ],
    goods_issue_repository: Annotated[
        GoodsIssueRepository, Depends(get_goods_issue_repository)
    ],
    grn_repository: Annotated[
        GoodsReceiptNoteRepository, Depends(get_goods_receipt_note_repository)
    ],
) -> InventoryStockGuardService:
    return InventoryStockGuardService(
        delivery_notes=delivery_note_repository,
        goods_issues=goods_issue_repository,
        grn_repository=grn_repository,
    )


def get_document_reversal_service(
    sales_credit_repository: Annotated[
        SalesCreditRepository, Depends(get_sales_credit_repository)
    ],
    supplier_credit_repository: Annotated[
        SupplierCreditRepository, Depends(get_supplier_credit_repository)
    ],
    sales_invoice_repository: Annotated[
        SalesInvoiceRepository, Depends(get_sales_invoice_repository)
    ],
    supplier_bill_repository: Annotated[
        SupplierBillRepository, Depends(get_supplier_bill_repository)
    ],
    stock_adjustment_repository: Annotated[
        StockAdjustmentRepository, Depends(get_stock_adjustment_repository)
    ],
    goods_issue_repository: Annotated[
        GoodsIssueRepository, Depends(get_goods_issue_repository)
    ],
    grn_repository: Annotated[
        GoodsReceiptNoteRepository, Depends(get_goods_receipt_note_repository)
    ],
    delivery_note_repository: Annotated[
        DeliveryNoteRepository, Depends(get_delivery_note_repository)
    ],
    journal_service: Annotated[JournalService, Depends(get_journal_service)],
    inventory_quantity_service: Annotated[
        InventoryQuantityService, Depends(get_inventory_quantity_service)
    ],
    posting_prerequisites: Annotated[
        PostingPrerequisitesService, Depends(get_posting_prerequisites_service)
    ],
) -> DocumentReversalService:
    return DocumentReversalService(
        sales_credits=sales_credit_repository,
        supplier_credits=supplier_credit_repository,
        sales_invoices=sales_invoice_repository,
        supplier_bills=supplier_bill_repository,
        stock_adjustments=stock_adjustment_repository,
        goods_issues=goods_issue_repository,
        grn_repository=grn_repository,
        delivery_notes=delivery_note_repository,
        journal_service=journal_service,
        inventory_quantities=inventory_quantity_service,
        posting_prerequisites=posting_prerequisites,
    )


def get_approval_request_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> ApprovalRequestRepository:
    return ApprovalRequestRepository(prisma)


def get_approval_engine_service(
    prisma: Annotated[Prisma, Depends(get_prisma)],
    policy_repository: Annotated[
        ApprovalPolicyRepository, Depends(get_approval_policy_repository)
    ],
    request_repository: Annotated[
        ApprovalRequestRepository, Depends(get_approval_request_repository)
    ],
    membership_roles: Annotated[
        MembershipRoleRepository, Depends(get_membership_role_repository)
    ],
) -> ApprovalEngineService:
    return ApprovalEngineService(
        policy_repository=policy_repository,
        request_repository=request_repository,
        prisma_client=prisma,
        membership_roles=membership_roles,
    )


def get_grni_service(prisma: Annotated[Prisma, Depends(get_prisma)]) -> GrniService:
    return GrniService(prisma=prisma)


def get_assembly_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> AssemblyRepository:
    return AssemblyRepository(prisma)


def get_assembly_service(
    assembly_repository: Annotated[AssemblyRepository, Depends(get_assembly_repository)],
    product_repository: Annotated[ProductRepository, Depends(get_product_repository)],
    document_number_service: Annotated[
        DocumentNumberService, Depends(get_document_number_service)
    ],
    posting_service: Annotated[PostingService, Depends(get_posting_service)],
    prerequisites: Annotated[
        PostingPrerequisitesService, Depends(get_posting_prerequisites_service)
    ],
) -> AssemblyService:
    return AssemblyService(
        assembly_repository=assembly_repository,
        product_repository=product_repository,
        document_number_service=document_number_service,
        posting_service=posting_service,
        prerequisites=prerequisites,
    )


def get_fx_revaluation_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> FxRevaluationRepository:
    return FxRevaluationRepository(prisma)


def get_fx_revaluation_service(
    fx_repository: Annotated[FxRevaluationRepository, Depends(get_fx_revaluation_repository)],
    bank_repository: Annotated[BankRepository, Depends(get_bank_repository)],
    posting_service: Annotated[PostingService, Depends(get_posting_service)],
    prerequisites: Annotated[
        PostingPrerequisitesService, Depends(get_posting_prerequisites_service)
    ],
) -> FxRevaluationService:
    return FxRevaluationService(
        fx_repository=fx_repository,
        bank_repository=bank_repository,
        posting_service=posting_service,
        prerequisites=prerequisites,
    )


def get_fbr_repository(prisma: Annotated[Prisma, Depends(get_prisma)]) -> FbrRepository:
    return FbrRepository(prisma)


def get_fbr_service(
    fbr_repository: Annotated[FbrRepository, Depends(get_fbr_repository)],
    sales_invoice_repository: Annotated[
        SalesInvoiceRepository, Depends(get_sales_invoice_repository)
    ],
    outbox_repository: Annotated[OutboxRepository, Depends(get_outbox_repository)],
) -> FbrService:
    return FbrService(
        fbr_repository=fbr_repository,
        sales_invoice_repository=sales_invoice_repository,
        outbox_repository=outbox_repository,
    )


def get_payment_gateway_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> PaymentGatewayRepository:
    return PaymentGatewayRepository(prisma)


def get_clickhouse_schema_service() -> ClickHouseSchemaService:
    return ClickHouseSchemaService()


def get_coa_repository(prisma: Annotated[Prisma, Depends(get_prisma)]) -> CoaRepository:
    """COA read repository."""

    return CoaRepository(prisma)


def get_bank_repository(prisma: Annotated[Prisma, Depends(get_prisma)]) -> BankRepository:
    """Bank repository."""

    return BankRepository(prisma)


def get_bank_payment_service(
    bank_repository: Annotated[BankRepository, Depends(get_bank_repository)],
    document_number_service: Annotated[DocumentNumberService, Depends(get_document_number_service)],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    posting_service: Annotated[PostingService, Depends(get_posting_service)],
) -> BankPaymentService:
    """Bank payment voucher orchestration with lock-date guard and GL posting."""

    return BankPaymentService(
        bank_repository=bank_repository,
        document_number_service=document_number_service,
        lock_date_service=lock_date_service,
        posting_service=posting_service,
    )


def get_customer_repository(prisma: Annotated[Prisma, Depends(get_prisma)]) -> CustomerRepository:
    """Customer repository."""

    return CustomerRepository(prisma)


def get_project_repository(prisma: Annotated[Prisma, Depends(get_prisma)]) -> ProjectRepository:
    return ProjectRepository(prisma)


def get_location_repository(prisma: Annotated[Prisma, Depends(get_prisma)]) -> LocationRepository:
    return LocationRepository(prisma)


def get_budget_repository(prisma: Annotated[Prisma, Depends(get_prisma)]) -> BudgetRepository:
    return BudgetRepository(prisma)


def get_budget_service(
    budget_repository: Annotated[BudgetRepository, Depends(get_budget_repository)],
) -> BudgetService:
    return BudgetService(budget_repository=budget_repository)


def get_supplier_repository(prisma: Annotated[Prisma, Depends(get_prisma)]) -> SupplierRepository:
    """Supplier repository."""

    return SupplierRepository(prisma)


def get_product_repository(prisma: Annotated[Prisma, Depends(get_prisma)]) -> ProductRepository:
    """Product repository."""

    return ProductRepository(prisma)


def get_sales_invoice_repository(prisma: Annotated[Prisma, Depends(get_prisma)]) -> SalesInvoiceRepository:
    """Sales invoice repository."""

    return SalesInvoiceRepository(prisma)


def get_supplier_bill_repository(prisma: Annotated[Prisma, Depends(get_prisma)]) -> SupplierBillRepository:
    """Supplier bill repository."""

    return SupplierBillRepository(prisma)


def get_smart_settings_repository(prisma: Annotated[Prisma, Depends(get_prisma)]) -> SmartSettingsRepository:
    """Smart Settings persistence."""

    return SmartSettingsRepository(prisma)


def get_app_settings_service(
    smart_settings_repository: Annotated[
        SmartSettingsRepository, Depends(get_smart_settings_repository)
    ],
) -> AppSettingsService:
    """Print templates, content settings, filters, email, and related slices."""

    return AppSettingsService(smart_settings_repository=smart_settings_repository)


def get_onboarding_repository(prisma: Annotated[Prisma, Depends(get_prisma)]) -> "OnboardingRepository":
    """Per-user tour progress — P48."""

    from app.repositories.onboarding_repository import OnboardingRepository

    return OnboardingRepository(prisma)


def get_assistant_conversation_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> "AssistantConversationRepository":
    from app.repositories.assistant_conversation_repository import (
        AssistantConversationRepository,
    )

    return AssistantConversationRepository(prisma)


def get_groq_client() -> "GroqClient":
    from app.integrations.groq_client import GroqClient

    return GroqClient()


def get_llm_provider():
    """Task-tier provider router (Claude primary, Groq/OpenAI fallback lanes).

    Satisfies the same streaming event-dict contract as GroqClient, so it drops
    into the assistant orchestrator unchanged. Falls back to whichever provider is
    configured — a Groq-only deploy behaves exactly as before.
    """

    from app.services.ai.providers.router import ProviderRouter

    return ProviderRouter()


def get_assistant_tool_handlers(
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    sales_invoice_repository: Annotated[
        "SalesInvoiceRepository", Depends(get_sales_invoice_repository)
    ],
    product_repository: Annotated["ProductRepository", Depends(get_product_repository)],
    audit_log_repository: Annotated[AuditLogRepository, Depends(get_audit_log_repository)],
    auto_code_service: Annotated[AutoCodeService, Depends(get_auto_code_service)],
) -> "AssistantToolHandlers":
    from app.services.assistant.tool_handlers import AssistantToolHandlers

    return AssistantToolHandlers(
        permission_service=permission_service,
        sales_invoice_repository=sales_invoice_repository,
        product_repository=product_repository,
        audit_log_repository=audit_log_repository,
        auto_code_service=auto_code_service,
    )


def get_assistant_orchestrator(
    llm_provider: Annotated[Any, Depends(get_llm_provider)],
    conversation_repository: Annotated[
        "AssistantConversationRepository", Depends(get_assistant_conversation_repository)
    ],
    tool_handlers: Annotated["AssistantToolHandlers", Depends(get_assistant_tool_handlers)],
    audit_log_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
) -> "AssistantOrchestrator":
    from app.services.assistant.orchestrator import AssistantOrchestrator

    # llm_provider is the task-tier ProviderRouter; it satisfies the same
    # streaming contract the orchestrator expects from a single provider.
    return AssistantOrchestrator(
        groq_client=llm_provider,
        conversation_repository=conversation_repository,
        tool_handlers=tool_handlers,
        audit_log_service=audit_log_service,
    )


def get_onboarding_release_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> "OnboardingReleaseRepository":
    """Tenant What's New CMS — P51."""

    from app.repositories.onboarding_release_repository import OnboardingReleaseRepository

    return OnboardingReleaseRepository(prisma)


def get_platform_onboarding_release_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> "PlatformOnboardingReleaseRepository":
    """Platform What's New CMS — P52."""

    from app.repositories.platform_onboarding_release_repository import (
        PlatformOnboardingReleaseRepository,
    )

    return PlatformOnboardingReleaseRepository(prisma)


def get_taxes_config_repository(prisma: Annotated[Prisma, Depends(get_prisma)]) -> TaxesConfigRepository:
    """Tax configuration persistence."""

    return TaxesConfigRepository(prisma)


def get_lock_date_repository(prisma: Annotated[Prisma, Depends(get_prisma)]) -> LockDateRepository:
    """Lock date persistence."""

    return LockDateRepository(prisma)


def get_lock_date_service(
    lock_date_repository: Annotated[LockDateRepository, Depends(get_lock_date_repository)],
) -> LockDateService:
    """Lock date enforcement service (catalog §3.14)."""

    return LockDateService(lock_date_repository)


def get_posting_service(
    journal_service: Annotated[JournalService, Depends(get_journal_service)],
    smart_settings_repository: Annotated[
        SmartSettingsRepository, Depends(get_smart_settings_repository)
    ],
    bank_repository: Annotated[BankRepository, Depends(get_bank_repository)],
) -> PostingService:
    """Posting service ties operational documents into the GL via JournalService."""

    return PostingService(
        journal_service=journal_service,
        smart_settings_repository=smart_settings_repository,
        bank_repository=bank_repository,
    )


def get_posting_prerequisites_service(
    smart_settings_repository: Annotated[
        SmartSettingsRepository, Depends(get_smart_settings_repository)
    ],
    coa_repository: Annotated[CoaRepository, Depends(get_coa_repository)],
) -> PostingPrerequisitesService:
    return PostingPrerequisitesService(
        smart_settings_repository=smart_settings_repository,
        coa_repository=coa_repository,
    )


def get_posting_engine(
    posting_service: Annotated[PostingService, Depends(get_posting_service)],
    prerequisites: Annotated[
        PostingPrerequisitesService, Depends(get_posting_prerequisites_service)
    ],
    sales_invoice_repository: Annotated[
        SalesInvoiceRepository, Depends(get_sales_invoice_repository)
    ],
    supplier_bill_repository: Annotated[
        SupplierBillRepository, Depends(get_supplier_bill_repository)
    ],
    stock_adjustment_repository: Annotated[
        StockAdjustmentRepository, Depends(get_stock_adjustment_repository)
    ],
    tax_calculation_service: Annotated[
        TaxCalculationService, Depends(get_tax_calculation_service)
    ],
    product_repository: Annotated[ProductRepository, Depends(get_product_repository)],
    goods_issue_repository: Annotated[
        GoodsIssueRepository, Depends(get_goods_issue_repository)
    ],
    document_number_service: Annotated[
        DocumentNumberService, Depends(get_document_number_service)
    ],
    inventory_quantity_service: Annotated[
        InventoryQuantityService, Depends(get_inventory_quantity_service)
    ],
) -> PostingEngine:
    return PostingEngine(
        posting_service=posting_service,
        prerequisites=prerequisites,
        sales_invoice_repository=sales_invoice_repository,
        supplier_bill_repository=supplier_bill_repository,
        stock_adjustment_repository=stock_adjustment_repository,
        tax_calculation_service=tax_calculation_service,
        product_repository=product_repository,
        goods_issue_repository=goods_issue_repository,
        document_number_service=document_number_service,
        inventory_quantity_service=inventory_quantity_service,
    )


def get_goods_issue_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> GoodsIssueRepository:
    return GoodsIssueRepository(prisma)


def get_business_information_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> BusinessInformationRepository:
    """Business information persistence."""

    return BusinessInformationRepository(prisma)


async def get_jwt_claims(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> JwtClaims:
    """Decode bearer token and return ``user_id`` + ``company_id`` claims."""

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("Missing bearer token")
    try:
        payload = decode_token(credentials.credentials)
    except Exception as exc:  # noqa: BLE001 — map jose errors to 401
        raise UnauthorizedError("Invalid token") from exc
    user_id = payload.get("sub")
    company_id = payload.get("companyId")
    if not isinstance(user_id, str) or not isinstance(company_id, str):
        raise UnauthorizedError("Token missing subject or companyId")
    return JwtClaims(user_id=user_id, company_id=company_id)


def assert_company_matches_token(company_id: str, claims: JwtClaims) -> None:
    """Raise if the path tenant does not match the JWT active company."""

    if claims.company_id != company_id:
        raise ForbiddenError("Token does not allow this company")


async def resolve_tenant(
    company_id: str,
    request: Request,
    claims: Annotated[JwtClaims, Depends(get_jwt_claims)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    membership_repo: Annotated[MembershipRepository, Depends(get_membership_repository)],
) -> JwtClaims:
    """Router-level guard: path ``company_id`` must match token and role is assigned."""

    from app.core.ip_allowlist import assert_membership_ip_allowed
    from app.core.tenant_context import set_current_user_id

    assert_company_matches_token(company_id, claims)
    await permission_service.assert_membership_has_role(
        company_id=company_id, user_id=claims.user_id
    )
    membership = await membership_repo.get_membership(
        company_id=company_id, user_id=claims.user_id
    )
    if membership is not None:
        assert_membership_ip_allowed(
            request=request,
            allowlist_raw=membership.get("ipAllowlist"),
        )
    set_current_user_id(claims.user_id)
    return claims


def get_sales_receipt_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> SalesReceiptRepository:
    """Customer receipt persistence."""

    return SalesReceiptRepository(prisma)


def get_supplier_payment_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> SupplierPaymentRepository:
    """Supplier payment persistence."""

    return SupplierPaymentRepository(prisma)


def get_bank_receipt_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> BankReceiptRepository:
    """Bank receipt persistence."""

    return BankReceiptRepository(prisma)


def get_bank_transfer_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> BankTransferRepository:
    """Bank transfer persistence."""

    return BankTransferRepository(prisma)


def get_activity_service(
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
) -> ActivityService:
    """Sales All / Purchases All unified activity feeds."""

    return ActivityService(prisma)


def get_my_tasks_service(
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
) -> MyTasksService:
    """Header My Tasks — draft documents needing attention."""

    return MyTasksService(prisma)


def get_aging_service(prisma: Annotated[Prisma, Depends(get_prisma)]) -> AgingService:
    """AR / AP aging + party statement aggregator."""

    return AgingService(prisma)


def get_smart_settings_runtime(
    prisma: Annotated[Prisma, Depends(get_prisma)],
    smart_settings_repository: Annotated[
        SmartSettingsRepository, Depends(get_smart_settings_repository)
    ],
) -> SmartSettingsRuntime:
    """FA §12.2 runtime flags (credit limit, round-off, template draft)."""

    return SmartSettingsRuntime(
        smart_settings_repository=smart_settings_repository,
        prisma=prisma,
    )


def get_allocation_service(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> AllocationService:
    """Receipt / payment allocation against open invoices / bills."""

    return AllocationService(prisma)


def get_paypro_service(
    payment_gateway_repository: Annotated[
        PaymentGatewayRepository, Depends(get_payment_gateway_repository)
    ],
    sales_receipt_repository: Annotated[
        SalesReceiptRepository, Depends(get_sales_receipt_repository)
    ],
    document_number_service: Annotated[
        DocumentNumberService, Depends(get_document_number_service)
    ],
    posting_service: Annotated[PostingService, Depends(get_posting_service)],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    smart_settings_repository: Annotated[
        SmartSettingsRepository, Depends(get_smart_settings_repository)
    ],
    allocation_service: Annotated[AllocationService, Depends(get_allocation_service)],
) -> PayproService:
    return PayproService(
        payment_gateway_repository=payment_gateway_repository,
        sales_receipt_repository=sales_receipt_repository,
        document_number_service=document_number_service,
        posting_service=posting_service,
        lock_date_service=lock_date_service,
        smart_settings_repository=smart_settings_repository,
        allocation_service=allocation_service,
    )


def get_kuickpay_service(
    payment_gateway_repository: Annotated[
        PaymentGatewayRepository, Depends(get_payment_gateway_repository)
    ],
    sales_receipt_repository: Annotated[
        SalesReceiptRepository, Depends(get_sales_receipt_repository)
    ],
    document_number_service: Annotated[
        DocumentNumberService, Depends(get_document_number_service)
    ],
    posting_service: Annotated[PostingService, Depends(get_posting_service)],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    smart_settings_repository: Annotated[
        SmartSettingsRepository, Depends(get_smart_settings_repository)
    ],
    allocation_service: Annotated[AllocationService, Depends(get_allocation_service)],
) -> KuickpayService:
    return KuickpayService(
        payment_gateway_repository=payment_gateway_repository,
        sales_receipt_repository=sales_receipt_repository,
        document_number_service=document_number_service,
        posting_service=posting_service,
        lock_date_service=lock_date_service,
        smart_settings_repository=smart_settings_repository,
        allocation_service=allocation_service,
    )


def get_quotation_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> QuotationRepository:
    """Quotation persistence."""

    return QuotationRepository(prisma)


def get_sales_order_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> SalesOrderRepository:
    """Sales order persistence."""

    return SalesOrderRepository(prisma)


def get_purchase_order_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> PurchaseOrderRepository:
    """Purchase order persistence."""

    return PurchaseOrderRepository(prisma)


def get_sales_credit_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> SalesCreditRepository:
    """Sales credit persistence."""

    return SalesCreditRepository(prisma)


def get_supplier_credit_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> SupplierCreditRepository:
    """Supplier credit persistence."""

    return SupplierCreditRepository(prisma)


def get_stock_adjustment_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> StockAdjustmentRepository:
    """Stock adjustment persistence (§7.3)."""

    return StockAdjustmentRepository(prisma)


def get_stock_transfer_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> StockTransferRepository:
    """Stock transfer persistence (§7.2)."""

    return StockTransferRepository(prisma)


def get_product_batch_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> ProductBatchRepository:
    """Product batch + expiry persistence (§7.8)."""

    return ProductBatchRepository(prisma)


def get_product_service(
    product_repository: Annotated[ProductRepository, Depends(get_product_repository)],
    batch_repository: Annotated[ProductBatchRepository, Depends(get_product_batch_repository)],
    attachment_repository: Annotated[AttachmentRepository, Depends(get_attachment_repository)],
    uom_service: Annotated[ProductUomService, Depends(get_product_uom_service)],
    auto_code_service: Annotated[AutoCodeService, Depends(get_auto_code_service)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    field_masking: Annotated[FieldMaskingService, Depends(get_field_masking_service)],
) -> ProductService:
    return ProductService(
        product_repository=product_repository,
        batch_repository=batch_repository,
        attachment_repository=attachment_repository,
        uom_service=uom_service,
        auto_code_service=auto_code_service,
        audit_service=audit_service,
        field_masking=field_masking,
    )


def get_delivery_note_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> DeliveryNoteRepository:
    """Delivery note (GDNSI/GDNSO) persistence (§5.6)."""

    return DeliveryNoteRepository(prisma)


def get_goods_receipt_note_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> GoodsReceiptNoteRepository:
    """Goods receipt note (GRNPO/GRNVI) persistence (§6)."""

    return GoodsReceiptNoteRepository(prisma)


def get_pdc_received_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> PdcReceivedRepository:
    """Post-dated cheques received persistence (§5.7)."""

    return PdcReceivedRepository(prisma)


def get_pdc_issued_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> PdcIssuedRepository:
    """Post-dated cheques issued persistence (§6.1)."""

    return PdcIssuedRepository(prisma)


def get_pdc_service(
    pdc_received_repository: Annotated[
        PdcReceivedRepository, Depends(get_pdc_received_repository)
    ],
    pdc_issued_repository: Annotated[
        PdcIssuedRepository, Depends(get_pdc_issued_repository)
    ],
    sales_receipt_repository: Annotated[
        SalesReceiptRepository, Depends(get_sales_receipt_repository)
    ],
    supplier_payment_repository: Annotated[
        SupplierPaymentRepository, Depends(get_supplier_payment_repository)
    ],
    document_number_service: Annotated[
        DocumentNumberService, Depends(get_document_number_service)
    ],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    posting_service: Annotated[PostingService, Depends(get_posting_service)],
    allocation_service: Annotated[AllocationService, Depends(get_allocation_service)],
    journal_service: Annotated[JournalService, Depends(get_journal_service)],
) -> PdcService:
    return PdcService(
        pdc_received_repository=pdc_received_repository,
        pdc_issued_repository=pdc_issued_repository,
        sales_receipt_repository=sales_receipt_repository,
        supplier_payment_repository=supplier_payment_repository,
        document_number_service=document_number_service,
        lock_date_service=lock_date_service,
        posting_service=posting_service,
        allocation_service=allocation_service,
        journal_service=journal_service,
    )


def get_extended_reports_service(
    prisma: Annotated[Prisma, Depends(get_read_prisma)],
) -> ExtendedReportsService:
    """Sprint 11 — catalog-named operational reports."""

    return ExtendedReportsService(prisma)


def get_conversion_service(
    quotation_repository: Annotated[QuotationRepository, Depends(get_quotation_repository)],
    sales_order_repository: Annotated[
        SalesOrderRepository, Depends(get_sales_order_repository)
    ],
    sales_invoice_repository: Annotated[
        SalesInvoiceRepository, Depends(get_sales_invoice_repository)
    ],
    purchase_order_repository: Annotated[
        PurchaseOrderRepository, Depends(get_purchase_order_repository)
    ],
    supplier_bill_repository: Annotated[
        SupplierBillRepository, Depends(get_supplier_bill_repository)
    ],
    document_number_service: Annotated[
        DocumentNumberService, Depends(get_document_number_service)
    ],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    posting_engine: Annotated[PostingEngine, Depends(get_posting_engine)],
) -> ConversionService:
    """Document-conversion orchestration."""

    return ConversionService(
        quotation_repository=quotation_repository,
        sales_order_repository=sales_order_repository,
        sales_invoice_repository=sales_invoice_repository,
        purchase_order_repository=purchase_order_repository,
        supplier_bill_repository=supplier_bill_repository,
        document_number_service=document_number_service,
        lock_date_service=lock_date_service,
        posting_engine=posting_engine,
    )


def get_membership_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> MembershipRepository:
    """Membership + role persistence."""

    return MembershipRepository(prisma)


def get_role_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> RoleRepository:
    return RoleRepository(prisma)


def get_role_permission_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> RolePermissionRepository:
    return RolePermissionRepository(prisma)


def get_membership_role_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> MembershipRoleRepository:
    return MembershipRoleRepository(prisma)


def get_effective_permission_service(
    prisma: Annotated[Prisma, Depends(get_prisma)],
    role_permissions: Annotated[
        RolePermissionRepository, Depends(get_role_permission_repository)
    ],
    membership_roles: Annotated[
        MembershipRoleRepository, Depends(get_membership_role_repository)
    ],
) -> EffectivePermissionService:
    return EffectivePermissionService(
        prisma_client=prisma,
        role_permissions=role_permissions,
        membership_roles=membership_roles,
    )


def get_access_control_service(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> AccessControlService:
    return AccessControlService(prisma)


def get_field_masking_service(
    access_control: Annotated[AccessControlService, Depends(get_access_control_service)],
    membership_repo: Annotated[MembershipRepository, Depends(get_membership_repository)],
    effective_permissions: Annotated[
        EffectivePermissionService, Depends(get_effective_permission_service)
    ],
) -> FieldMaskingService:
    return FieldMaskingService(
        access_control=access_control,
        membership_repo=membership_repo,
        effective_permissions=effective_permissions,
    )


def get_permission_service(
    effective_permissions: Annotated[
        EffectivePermissionService, Depends(get_effective_permission_service)
    ],
    access_control: Annotated[AccessControlService, Depends(get_access_control_service)],
) -> PermissionService:
    """RBAC checks for tenant routes."""

    return PermissionService(
        effective_permissions=effective_permissions,
        access_control=access_control,
    )


def get_tax_calculation_service(
    taxes_config_repository: Annotated[
        TaxesConfigRepository, Depends(get_taxes_config_repository)
    ],
    smart_runtime: Annotated[SmartSettingsRuntime, Depends(get_smart_settings_runtime)],
) -> TaxCalculationService:
    """Line tax computation from Taxes & Year End config."""

    return TaxCalculationService(
        taxes_repository=taxes_config_repository,
        smart_runtime=smart_runtime,
    )


def get_auto_code_service(
    smart_settings_repository: Annotated[
        SmartSettingsRepository, Depends(get_smart_settings_repository)
    ],
    document_number_repository: Annotated[
        DocumentNumberRepository, Depends(get_document_number_repository)
    ],
) -> AutoCodeService:
    return AutoCodeService(
        smart_settings_repository=smart_settings_repository,
        document_number_repository=document_number_repository,
    )


def get_last_rate_service(
    prisma: Annotated[Prisma, Depends(get_prisma)],
    smart_settings_repository: Annotated[
        SmartSettingsRepository, Depends(get_smart_settings_repository)
    ],
) -> LastRateService:
    return LastRateService(prisma=prisma, smart_settings_repository=smart_settings_repository)


def get_transaction_template_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> TransactionTemplateRepository:
    return TransactionTemplateRepository(prisma)


def get_recurring_schedule_repository(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> RecurringScheduleRepository:
    return RecurringScheduleRepository(prisma)


def get_batch_document_service(
    sales_invoice_repository: Annotated[
        SalesInvoiceRepository, Depends(get_sales_invoice_repository)
    ],
    supplier_bill_repository: Annotated[
        SupplierBillRepository, Depends(get_supplier_bill_repository)
    ],
    document_number_service: Annotated[
        DocumentNumberService, Depends(get_document_number_service)
    ],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    tax_service: Annotated[TaxCalculationService, Depends(get_tax_calculation_service)],
) -> BatchDocumentService:
    return BatchDocumentService(
        sales_invoice_repository=sales_invoice_repository,
        supplier_bill_repository=supplier_bill_repository,
        document_number_service=document_number_service,
        lock_date_service=lock_date_service,
        tax_service=tax_service,
    )


def get_advance_return_service(
    prisma: Annotated[Prisma, Depends(get_prisma)],
    sales_receipt_repository: Annotated[
        SalesReceiptRepository, Depends(get_sales_receipt_repository)
    ],
    supplier_payment_repository: Annotated[
        SupplierPaymentRepository, Depends(get_supplier_payment_repository)
    ],
    bank_repository: Annotated[BankRepository, Depends(get_bank_repository)],
    bank_receipt_repository: Annotated[
        BankReceiptRepository, Depends(get_bank_receipt_repository)
    ],
    document_number_service: Annotated[
        DocumentNumberService, Depends(get_document_number_service)
    ],
    lock_date_service: Annotated[LockDateService, Depends(get_lock_date_service)],
    posting_service: Annotated[PostingService, Depends(get_posting_service)],
) -> AdvanceReturnService:
    return AdvanceReturnService(
        prisma=prisma,
        sales_receipts=sales_receipt_repository,
        supplier_payments=supplier_payment_repository,
        banks=bank_repository,
        bank_receipts=bank_receipt_repository,
        document_numbers=document_number_service,
        lock_date=lock_date_service,
        posting=posting_service,
    )


def get_recurring_schedule_service(
    repository: Annotated[
        RecurringScheduleRepository, Depends(get_recurring_schedule_repository)
    ],
    batch_document_service: Annotated[
        BatchDocumentService, Depends(get_batch_document_service)
    ],
) -> RecurringScheduleService:
    return RecurringScheduleService(
        repository=repository,
        batch_document_service=batch_document_service,
    )


def require_permission(permission: str):
    """FastAPI dependency factory — enforce a permission code on mutating routes."""

    async def _guard(
        company_id: str,
        claims: Annotated[JwtClaims, Depends(resolve_tenant)],
        permission_service: Annotated[
            PermissionService, Depends(get_permission_service)
        ],
    ) -> JwtClaims:
        await permission_service.assert_allowed(
            company_id=company_id,
            user_id=claims.user_id,
            permission=permission,
        )
        return claims

    return _guard


def get_module_entitlement_service(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> ModuleEntitlementService:
    return ModuleEntitlementService(prisma=prisma)


def get_custom_field_service(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> CustomFieldService:
    return CustomFieldService(prisma=prisma)


def get_product_uom_service(
    prisma: Annotated[Prisma, Depends(get_prisma)],
) -> ProductUomService:
    return ProductUomService(prisma=prisma)


def get_module_access_service(
    module_service: Annotated[
        ModuleEntitlementService, Depends(get_module_entitlement_service)
    ],
    permission_service: Annotated[
        PermissionService, Depends(get_permission_service)
    ],
    access_control: Annotated[AccessControlService, Depends(get_access_control_service)],
) -> ModuleAccessService:
    return ModuleAccessService(
        module_service=module_service,
        permission_service=permission_service,
        access_control=access_control,
    )


def get_subscription_billing_service(
    prisma: Annotated[Prisma, Depends(get_prisma)],
    module_service: Annotated[
        ModuleEntitlementService, Depends(get_module_entitlement_service)
    ],
) -> SubscriptionBillingService:
    return SubscriptionBillingService(prisma=prisma, module_service=module_service)


def get_advance_users_service(
    prisma: Annotated[Prisma, Depends(get_prisma)],
    app_settings: Annotated[AppSettingsService, Depends(get_app_settings_service)],
    access_control: Annotated[AccessControlService, Depends(get_access_control_service)],
) -> AdvanceUsersService:
    return AdvanceUsersService(
        app_settings=app_settings,
        prisma_client=prisma,
        access_control=access_control,
    )


def get_sales_invoice_email_service(
    invoice_repo: Annotated[SalesInvoiceRepository, Depends(get_sales_invoice_repository)],
    customer_repo: Annotated[CustomerRepository, Depends(get_customer_repository)],
    company_repo: Annotated[CompanyRepository, Depends(get_company_repository)],
    app_settings: Annotated[AppSettingsService, Depends(get_app_settings_service)],
    email_service: Annotated[EmailService, Depends(get_email_service)],
) -> SalesInvoiceEmailService:
    return SalesInvoiceEmailService(
        invoice_repo=invoice_repo,
        customer_repo=customer_repo,
        company_repo=company_repo,
        app_settings=app_settings,
        email_service=email_service,
    )


def require_module(module_code: str):
    """FastAPI dependency — block when company subscription omits a module."""

    async def _guard(
        company_id: str,
        _claims: Annotated[JwtClaims, Depends(resolve_tenant)],
        module_service: Annotated[
            ModuleEntitlementService, Depends(get_module_entitlement_service)
        ],
    ) -> None:
        await module_service.assert_enabled(
            company_id=company_id, module_code=module_code
        )

    return _guard


def require_module_access(module_code: str):
    """P12 — module entitlement plus RBAC matrix permission."""

    async def _guard(
        company_id: str,
        claims: Annotated[JwtClaims, Depends(resolve_tenant)],
        access: Annotated[ModuleAccessService, Depends(get_module_access_service)],
    ) -> JwtClaims:
        await access.assert_access(
            company_id=company_id,
            user_id=claims.user_id,
            module_code=module_code,
        )
        return claims

    return _guard


def require_module_list_read(module_code: str):
    """P25 — module entitlement plus list/read permission for GET grids."""

    async def _guard(
        company_id: str,
        claims: Annotated[JwtClaims, Depends(resolve_tenant)],
        access: Annotated[ModuleAccessService, Depends(get_module_access_service)],
    ) -> JwtClaims:
        await access.assert_list_read(
            company_id=company_id,
            user_id=claims.user_id,
            module_code=module_code,
        )
        return claims

    return _guard


def require_module_reports(module_code: str):
    """Module reportsEnabled flag plus list/read permission."""

    async def _guard(
        company_id: str,
        claims: Annotated[JwtClaims, Depends(resolve_tenant)],
        access: Annotated[ModuleAccessService, Depends(get_module_access_service)],
    ) -> JwtClaims:
        await access.assert_reports(
            company_id=company_id,
            user_id=claims.user_id,
            module_code=module_code,
        )
        return claims

    return _guard
