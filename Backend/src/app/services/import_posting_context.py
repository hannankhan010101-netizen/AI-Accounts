"""Construct posting stack for background import jobs (no FastAPI DI)."""

from __future__ import annotations

from prisma_generated import Prisma

from app.repositories.bank_repository import BankRepository
from app.repositories.coa_repository import CoaRepository
from app.repositories.document_number_repository import DocumentNumberRepository
from app.repositories.goods_issue_repository import GoodsIssueRepository
from app.repositories.inventory_repository import StockAdjustmentRepository
from app.repositories.journal_repository import JournalRepository
from app.repositories.lock_date_repository import LockDateRepository
from app.repositories.inventory_repository import ProductBatchRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.sales_invoice_repository import SalesInvoiceRepository
from app.repositories.smart_settings_repository import SmartSettingsRepository
from app.repositories.supplier_bill_repository import SupplierBillRepository
from app.repositories.taxes_config_repository import TaxesConfigRepository
from app.services.document_number_service import DocumentNumberService
from app.services.inventory_quantity_service import InventoryQuantityService
from app.services.journal_service import JournalService
from app.services.lock_date_service import LockDateService
from app.services.posting_engine import PostingEngine
from app.services.posting_prerequisites_service import PostingPrerequisitesService
from app.services.posting_service import PostingService
from app.services.smart_settings_runtime import SmartSettingsRuntime
from app.services.tax_calculation_service import TaxCalculationService


def build_import_posting_stack(
    db: Prisma,
) -> tuple[PostingEngine, PostingService]:
    """Wire the same services as HTTP approve/post routes for import GL."""

    coa_repo = CoaRepository(db)
    smart_repo = SmartSettingsRepository(db)
    bank_repo = BankRepository(db)
    doc_num_repo = DocumentNumberRepository(db)
    journal_repo = JournalRepository(db)
    lock_repo = LockDateRepository(db)
    lock_service = LockDateService(lock_repo)
    doc_nums = DocumentNumberService(document_number_repository=doc_num_repo)
    journal_service = JournalService(
        journal_repository=journal_repo,
        document_number_service=doc_nums,
        coa_repository=coa_repo,
        lock_date_service=lock_service,
    )
    posting_service = PostingService(
        journal_service=journal_service,
        smart_settings_repository=smart_repo,
        bank_repository=bank_repo,
    )
    smart_runtime = SmartSettingsRuntime(
        smart_settings_repository=smart_repo,
        prisma=db,
    )
    tax_service = TaxCalculationService(
        taxes_repository=TaxesConfigRepository(db),
        smart_runtime=smart_runtime,
    )
    batches = ProductBatchRepository(db)
    engine = PostingEngine(
        posting_service=posting_service,
        prerequisites=PostingPrerequisitesService(
            smart_settings_repository=smart_repo,
            coa_repository=coa_repo,
        ),
        sales_invoice_repository=SalesInvoiceRepository(db),
        supplier_bill_repository=SupplierBillRepository(db),
        stock_adjustment_repository=StockAdjustmentRepository(db),
        tax_calculation_service=tax_service,
        product_repository=ProductRepository(db),
        goods_issue_repository=GoodsIssueRepository(db),
        document_number_service=doc_nums,
        inventory_quantity_service=InventoryQuantityService(batches=batches),
    )
    return engine, posting_service
