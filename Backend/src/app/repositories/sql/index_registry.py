"""Step 2 composite index registry — documents index → query purpose."""

from __future__ import annotations

STEP2_INDEX_REGISTRY: dict[str, str] = {
    # P0 — keyset / report lists
    "idx_step2_si_keyset": "sales_invoices: company+status+date+id DESC keyset pagination",
    "idx_step2_sb_keyset": "supplier_bills: company+status+date+id DESC keyset pagination",
    "idx_step2_bank_payments_keyset": "bank_payments: company+date+id keyset",
    "idx_step2_bank_receipts_keyset": "bank_receipts: company+date+id keyset",
    "idx_step2_bank_transfers_keyset": "bank_transfers: company+date+id keyset",
    "idx_step2_stock_adjustments_keyset": "stock_adjustments: company+date+id keyset",
    "idx_step2_stock_transfers_keyset": "stock_transfers: company+date+id keyset",
    "idx_step2_assembly_jobs_keyset": "assembly_jobs: company+date+id keyset",
    "idx_step2_products_active_code": "products: active-only code+id ascending (partial)",
    "idx_step2_customers_code": "customers: company+code+id ascending keyset",
    "idx_step2_suppliers_code": "suppliers: company+code+id ascending keyset",
    # P1 — subledger / activity
    "idx_step2_sr_customer_date": "sales_receipts: company+customer+date",
    "idx_step2_sp_supplier_date": "supplier_payments: company+supplier+date",
    "idx_step2_si_customer_status_date": "sales_invoices: activity feed party+status+date",
    "idx_step2_sb_supplier_status_date": "supplier_bills: activity feed party+status+date",
    "idx_step2_sales_credits_customer_date": "sales_credits: activity party+date",
    "idx_step2_supplier_credits_supplier_date": "supplier_credits: activity party+date",
    "idx_step2_quotations_customer_date": "quotations: activity party+date",
    "idx_step2_sales_orders_customer_date": "sales_orders: activity party+date",
    "idx_step2_purchase_orders_supplier_date": "purchase_orders: activity party+date",
    "idx_step2_delivery_notes_customer_date": "delivery_notes: activity party+date",
    "idx_step2_grn_supplier_date": "goods_receipt_notes: activity party+date",
    "idx_step2_pdc_received_customer_date": "pdc_received: activity party+date",
    "idx_step2_pdc_issued_supplier_date": "pdc_issued: activity party+date",
    # P1 — My Tasks partial draft
    "idx_step2_sales_credits_draft": "my_tasks: draft sales credits",
    "idx_step2_supplier_credits_draft": "my_tasks: draft supplier credits",
    "idx_step2_quotations_draft": "my_tasks: draft quotations",
    "idx_step2_sales_orders_draft": "my_tasks: draft sales orders",
    "idx_step2_purchase_orders_draft": "my_tasks: draft purchase orders",
    "idx_step2_journals_draft": "my_tasks: draft journals",
    # P1 — audit / membership search
    "idx_step2_audit_company_user_created": "audit_log: company+user+created_at",
    "idx_step2_audit_company_transaction_id": "audit_log: company+transaction_id",
    "idx_step2_audit_company_type_created": "audit_log: company+type+created_at",
    "idx_step2_audit_transaction_type_trgm": "audit_log: typeContains pg_trgm GIN",
    "idx_step2_users_email_trgm": "membership search: user email pg_trgm GIN",
    "idx_step2_users_first_name_trgm": "membership search: first name pg_trgm GIN",
    "idx_step2_users_last_name_trgm": "membership search: last name pg_trgm GIN",
    "idx_step2_memberships_company_role": "membership list: company+role filter",
    # P2 — workers
    "idx_step2_outbox_pending_claim": "outbox worker: pending claim queue (partial)",
    "idx_step2_report_runs_completed": "report runs: completed sync by completed_at",
    "idx_step2_approval_requests_queue": "approval queue: company+status+created_at",
    "idx_step2_journal_lines_project": "project payments report: project_code (partial)",
    "idx_step2_grn_lines_note_product": "GRNI: grn line + product_code join",
}

MIGRATION_ONLY_INDEXES: frozenset[str] = frozenset(
    {
        "idx_step2_products_active_code",
        "idx_step2_sales_credits_draft",
        "idx_step2_supplier_credits_draft",
        "idx_step2_quotations_draft",
        "idx_step2_sales_orders_draft",
        "idx_step2_purchase_orders_draft",
        "idx_step2_journals_draft",
        "idx_step2_audit_transaction_type_trgm",
        "idx_step2_users_email_trgm",
        "idx_step2_users_first_name_trgm",
        "idx_step2_users_last_name_trgm",
        "idx_step2_outbox_pending_claim",
        "idx_step2_journal_lines_project",
    }
)


def step2_index_names() -> list[str]:
    return sorted(STEP2_INDEX_REGISTRY)
