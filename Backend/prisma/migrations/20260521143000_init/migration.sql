-- CreateTable
CREATE TABLE "Company" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Company_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "User" (
    "id" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "password_hash" TEXT NOT NULL,
    "first_name" TEXT NOT NULL,
    "last_name" TEXT NOT NULL,
    "phone" TEXT,
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "email_verified" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "User_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "auth_otp_challenges" (
    "id" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "purpose" TEXT NOT NULL,
    "code_hash" TEXT NOT NULL,
    "expires_at" TIMESTAMP(3) NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "auth_otp_challenges_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "company_memberships" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "role_id" TEXT,
    "is_default" BOOLEAN NOT NULL DEFAULT false,
    "ip_allowlist" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "company_memberships_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "roles" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "permissions" JSONB NOT NULL DEFAULT '[]',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "roles_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "business_information" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "business_name" TEXT,
    "address_line_1" TEXT,
    "address_line_2" TEXT,
    "address_line_3" TEXT,
    "address_line_4" TEXT,
    "address_line_5" TEXT,
    "branch_name" TEXT,
    "phone_number" TEXT,
    "mobile_number" TEXT,
    "email_address" TEXT,
    "website_address" TEXT,
    "logo_url" TEXT,
    "cnic" TEXT,
    "stn" TEXT,
    "ntn" TEXT,
    "apply_on_all_prints" BOOLEAN NOT NULL DEFAULT false,

    CONSTRAINT "business_information_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "smart_settings" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "payload" JSONB NOT NULL DEFAULT '{}',
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "smart_settings_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "lock_date_settings" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "global_lock_date" TIMESTAMP(3),
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "lock_date_settings_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "lock_date_per_user" (
    "id" TEXT NOT NULL,
    "lock_date_settings_id" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "extended_lock_date" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "lock_date_per_user_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "taxes_year_end_config" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "year_end_date" TIMESTAMP(3),
    "tax_display" JSONB NOT NULL DEFAULT '{}',
    "gst_rates" JSONB NOT NULL DEFAULT '[]',
    "fed_rates" JSONB NOT NULL DEFAULT '[]',
    "adt_rates" JSONB NOT NULL DEFAULT '[]',
    "wht_rates" JSONB NOT NULL DEFAULT '[]',
    "tax_regions" JSONB NOT NULL DEFAULT '[]',
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "taxes_year_end_config_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "coa_categories" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "code" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "sort_order" INTEGER NOT NULL DEFAULT 0,
    "category_type" TEXT NOT NULL DEFAULT 'Other',

    CONSTRAINT "coa_categories_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "coa_sections" (
    "id" TEXT NOT NULL,
    "category_id" TEXT NOT NULL,
    "code" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "sort_order" INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT "coa_sections_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "nominal_accounts" (
    "id" TEXT NOT NULL,
    "section_id" TEXT NOT NULL,
    "code" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "is_charge_deduction" BOOLEAN NOT NULL DEFAULT false,

    CONSTRAINT "nominal_accounts_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "bank_accounts" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "nominal_code" TEXT,
    "currency" TEXT NOT NULL DEFAULT 'PKR',
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "bank_accounts_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "customers" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "code" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "email" TEXT,
    "phone" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "customers_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "suppliers" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "code" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "email" TEXT,
    "phone" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "suppliers_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "products" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "code" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "is_stock" BOOLEAN NOT NULL DEFAULT true,
    "is_archived" BOOLEAN NOT NULL DEFAULT false,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "products_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "projects" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "code" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "is_active" BOOLEAN NOT NULL DEFAULT true,

    CONSTRAINT "projects_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "locations" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "code" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "is_main" BOOLEAN NOT NULL DEFAULT false,

    CONSTRAINT "locations_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "journals" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "journal_number" TEXT NOT NULL,
    "journal_date" TIMESTAMP(3) NOT NULL,
    "ref_no" TEXT,
    "total_amount" DECIMAL(18,4) NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'posted',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "journals_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "journal_lines" (
    "id" TEXT NOT NULL,
    "journal_id" TEXT NOT NULL,
    "nominal_code" TEXT NOT NULL,
    "debit" DECIMAL(18,4) NOT NULL DEFAULT 0,
    "credit" DECIMAL(18,4) NOT NULL DEFAULT 0,
    "project_code" TEXT,

    CONSTRAINT "journal_lines_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "sales_invoices" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "invoice_number" TEXT NOT NULL,
    "invoice_date" TIMESTAMP(3) NOT NULL,
    "customer_id" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'draft',
    "total_amount" DECIMAL(18,4) NOT NULL,
    "journal_id" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "sales_invoices_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "sales_invoice_lines" (
    "id" TEXT NOT NULL,
    "sales_invoice_id" TEXT NOT NULL,
    "product_code" TEXT,
    "quantity" DECIMAL(18,4) NOT NULL,
    "rate" DECIMAL(18,4) NOT NULL,
    "line_subtotal" DECIMAL(18,4) NOT NULL DEFAULT 0,
    "gst_code" TEXT,
    "gst_rate" DECIMAL(8,4) NOT NULL DEFAULT 0,
    "tax_amount" DECIMAL(18,4) NOT NULL DEFAULT 0,
    "line_total" DECIMAL(18,4) NOT NULL,
    "project_code" TEXT,

    CONSTRAINT "sales_invoice_lines_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "supplier_bills" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "bill_number" TEXT NOT NULL,
    "bill_date" TIMESTAMP(3) NOT NULL,
    "supplier_id" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'draft',
    "total_amount" DECIMAL(18,4) NOT NULL,
    "journal_id" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "supplier_bills_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "supplier_bill_lines" (
    "id" TEXT NOT NULL,
    "supplier_bill_id" TEXT NOT NULL,
    "product_code" TEXT,
    "quantity" DECIMAL(18,4) NOT NULL,
    "rate" DECIMAL(18,4) NOT NULL,
    "line_subtotal" DECIMAL(18,4) NOT NULL DEFAULT 0,
    "gst_code" TEXT,
    "gst_rate" DECIMAL(8,4) NOT NULL DEFAULT 0,
    "tax_amount" DECIMAL(18,4) NOT NULL DEFAULT 0,
    "line_total" DECIMAL(18,4) NOT NULL,

    CONSTRAINT "supplier_bill_lines_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "bank_payments" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "voucher_number" TEXT NOT NULL,
    "payment_date" TIMESTAMP(3) NOT NULL,
    "bank_account_id" TEXT NOT NULL,
    "nominal_code" TEXT,
    "total_amount" DECIMAL(18,4) NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'posted',
    "journal_id" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "bank_payments_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "sales_receipts" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "receipt_number" TEXT NOT NULL,
    "receipt_date" TIMESTAMP(3) NOT NULL,
    "customer_id" TEXT NOT NULL,
    "bank_account_id" TEXT NOT NULL,
    "total_amount" DECIMAL(18,4) NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'posted',
    "journal_id" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "sales_receipts_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "supplier_payments" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "voucher_number" TEXT NOT NULL,
    "payment_date" TIMESTAMP(3) NOT NULL,
    "supplier_id" TEXT NOT NULL,
    "bank_account_id" TEXT NOT NULL,
    "total_amount" DECIMAL(18,4) NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'posted',
    "journal_id" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "supplier_payments_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "sales_receipt_allocations" (
    "id" TEXT NOT NULL,
    "sales_receipt_id" TEXT NOT NULL,
    "sales_invoice_id" TEXT NOT NULL,
    "amount" DECIMAL(18,4) NOT NULL,

    CONSTRAINT "sales_receipt_allocations_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "supplier_payment_allocations" (
    "id" TEXT NOT NULL,
    "supplier_payment_id" TEXT NOT NULL,
    "supplier_bill_id" TEXT NOT NULL,
    "amount" DECIMAL(18,4) NOT NULL,

    CONSTRAINT "supplier_payment_allocations_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "bank_receipts" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "voucher_number" TEXT NOT NULL,
    "receipt_date" TIMESTAMP(3) NOT NULL,
    "bank_account_id" TEXT NOT NULL,
    "nominal_code" TEXT,
    "total_amount" DECIMAL(18,4) NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'posted',
    "journal_id" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "bank_receipts_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "quotations" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "quotation_number" TEXT NOT NULL,
    "quotation_date" TIMESTAMP(3) NOT NULL,
    "customer_id" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'draft',
    "total_amount" DECIMAL(18,4) NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "quotations_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "quotation_lines" (
    "id" TEXT NOT NULL,
    "quotation_id" TEXT NOT NULL,
    "product_code" TEXT,
    "quantity" DECIMAL(18,4) NOT NULL,
    "rate" DECIMAL(18,4) NOT NULL,
    "line_total" DECIMAL(18,4) NOT NULL,

    CONSTRAINT "quotation_lines_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "sales_orders" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "order_number" TEXT NOT NULL,
    "order_date" TIMESTAMP(3) NOT NULL,
    "customer_id" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'in_progress',
    "total_amount" DECIMAL(18,4) NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "sales_orders_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "sales_order_lines" (
    "id" TEXT NOT NULL,
    "sales_order_id" TEXT NOT NULL,
    "product_code" TEXT,
    "quantity" DECIMAL(18,4) NOT NULL,
    "rate" DECIMAL(18,4) NOT NULL,
    "line_total" DECIMAL(18,4) NOT NULL,
    "project_code" TEXT,

    CONSTRAINT "sales_order_lines_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "purchase_orders" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "order_number" TEXT NOT NULL,
    "order_date" TIMESTAMP(3) NOT NULL,
    "supplier_id" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'in_progress',
    "total_amount" DECIMAL(18,4) NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "purchase_orders_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "purchase_order_lines" (
    "id" TEXT NOT NULL,
    "purchase_order_id" TEXT NOT NULL,
    "product_code" TEXT,
    "quantity" DECIMAL(18,4) NOT NULL,
    "rate" DECIMAL(18,4) NOT NULL,
    "line_total" DECIMAL(18,4) NOT NULL,

    CONSTRAINT "purchase_order_lines_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "sales_credits" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "credit_number" TEXT NOT NULL,
    "credit_date" TIMESTAMP(3) NOT NULL,
    "customer_id" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'posted',
    "total_amount" DECIMAL(18,4) NOT NULL,
    "journal_id" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "sales_credits_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "sales_credit_lines" (
    "id" TEXT NOT NULL,
    "sales_credit_id" TEXT NOT NULL,
    "product_code" TEXT,
    "quantity" DECIMAL(18,4) NOT NULL,
    "rate" DECIMAL(18,4) NOT NULL,
    "line_total" DECIMAL(18,4) NOT NULL,

    CONSTRAINT "sales_credit_lines_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "supplier_credits" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "credit_number" TEXT NOT NULL,
    "credit_date" TIMESTAMP(3) NOT NULL,
    "supplier_id" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'posted',
    "total_amount" DECIMAL(18,4) NOT NULL,
    "journal_id" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "supplier_credits_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "supplier_credit_lines" (
    "id" TEXT NOT NULL,
    "supplier_credit_id" TEXT NOT NULL,
    "product_code" TEXT,
    "quantity" DECIMAL(18,4) NOT NULL,
    "rate" DECIMAL(18,4) NOT NULL,
    "line_total" DECIMAL(18,4) NOT NULL,

    CONSTRAINT "supplier_credit_lines_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "bank_transfers" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "voucher_number" TEXT NOT NULL,
    "transfer_date" TIMESTAMP(3) NOT NULL,
    "from_bank_account_id" TEXT NOT NULL,
    "to_bank_account_id" TEXT NOT NULL,
    "total_amount" DECIMAL(18,4) NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'posted',
    "journal_id" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "bank_transfers_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "attachments" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "entity_type" TEXT NOT NULL,
    "entity_id" TEXT NOT NULL,
    "file_name" TEXT NOT NULL,
    "storage_key" TEXT NOT NULL,
    "mime_type" TEXT,
    "byte_size" INTEGER NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "attachments_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "document_number_sequences" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "key" TEXT NOT NULL,
    "next_value" INTEGER NOT NULL,

    CONSTRAINT "document_number_sequences_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "import_jobs" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "job_type" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'pending',
    "file_name" TEXT,
    "error_count" INTEGER NOT NULL DEFAULT 0,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "import_jobs_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "audit_log_entries" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "user_id" TEXT,
    "transaction_type" TEXT NOT NULL,
    "transaction_id" TEXT,
    "status" TEXT,
    "details" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "audit_log_entries_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "approval_policies" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "entity_type" TEXT NOT NULL,
    "rules" JSONB NOT NULL DEFAULT '{}',

    CONSTRAINT "approval_policies_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "stock_adjustments" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "voucher_number" TEXT NOT NULL,
    "adjustment_date" TIMESTAMP(3) NOT NULL,
    "reason" TEXT NOT NULL DEFAULT 'adjustment',
    "notes" TEXT,
    "status" TEXT NOT NULL DEFAULT 'posted',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "stock_adjustments_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "stock_adjustment_lines" (
    "id" TEXT NOT NULL,
    "stock_adjustment_id" TEXT NOT NULL,
    "product_code" TEXT NOT NULL,
    "location_code" TEXT,
    "quantity_delta" DECIMAL(18,4) NOT NULL,
    "unit_cost" DECIMAL(18,4) NOT NULL DEFAULT 0,

    CONSTRAINT "stock_adjustment_lines_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "stock_transfers" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "voucher_number" TEXT NOT NULL,
    "transfer_date" TIMESTAMP(3) NOT NULL,
    "from_location_code" TEXT NOT NULL,
    "to_location_code" TEXT NOT NULL,
    "notes" TEXT,
    "status" TEXT NOT NULL DEFAULT 'posted',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "stock_transfers_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "stock_transfer_lines" (
    "id" TEXT NOT NULL,
    "stock_transfer_id" TEXT NOT NULL,
    "product_code" TEXT NOT NULL,
    "quantity" DECIMAL(18,4) NOT NULL,
    "unit_cost" DECIMAL(18,4) NOT NULL DEFAULT 0,

    CONSTRAINT "stock_transfer_lines_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "product_batches" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "product_code" TEXT NOT NULL,
    "batch_number" TEXT NOT NULL,
    "expiry_date" TIMESTAMP(3),
    "quantity_on_hand" DECIMAL(18,4) NOT NULL DEFAULT 0,
    "notes" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "product_batches_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "delivery_notes" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "voucher_number" TEXT NOT NULL,
    "delivery_date" TIMESTAMP(3) NOT NULL,
    "customer_id" TEXT NOT NULL,
    "source_kind" TEXT NOT NULL,
    "source_id" TEXT,
    "status" TEXT NOT NULL DEFAULT 'delivered',
    "notes" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "delivery_notes_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "delivery_note_lines" (
    "id" TEXT NOT NULL,
    "delivery_note_id" TEXT NOT NULL,
    "product_code" TEXT,
    "quantity" DECIMAL(18,4) NOT NULL,
    "notes" TEXT,

    CONSTRAINT "delivery_note_lines_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "goods_receipt_notes" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "voucher_number" TEXT NOT NULL,
    "receipt_date" TIMESTAMP(3) NOT NULL,
    "supplier_id" TEXT NOT NULL,
    "source_kind" TEXT NOT NULL,
    "source_id" TEXT,
    "status" TEXT NOT NULL DEFAULT 'received',
    "notes" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "goods_receipt_notes_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "goods_receipt_note_lines" (
    "id" TEXT NOT NULL,
    "goods_receipt_note_id" TEXT NOT NULL,
    "product_code" TEXT,
    "quantity" DECIMAL(18,4) NOT NULL,
    "notes" TEXT,

    CONSTRAINT "goods_receipt_note_lines_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "pdc_received" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "voucher_number" TEXT NOT NULL,
    "cheque_number" TEXT NOT NULL,
    "bank_name" TEXT NOT NULL,
    "customer_id" TEXT NOT NULL,
    "received_date" TIMESTAMP(3) NOT NULL,
    "cheque_date" TIMESTAMP(3) NOT NULL,
    "amount" DECIMAL(18,4) NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'pending',
    "linked_receipt_id" TEXT,
    "notes" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "pdc_received_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "pdc_issued" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "voucher_number" TEXT NOT NULL,
    "cheque_number" TEXT NOT NULL,
    "bank_account_id" TEXT NOT NULL,
    "supplier_id" TEXT NOT NULL,
    "issued_date" TIMESTAMP(3) NOT NULL,
    "cheque_date" TIMESTAMP(3) NOT NULL,
    "amount" DECIMAL(18,4) NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'pending',
    "linked_payment_id" TEXT,
    "notes" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "pdc_issued_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "document_tax_summary" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "document_kind" TEXT NOT NULL,
    "document_id" TEXT NOT NULL,
    "tax_code" TEXT NOT NULL,
    "tax_rate" DECIMAL(8,4) NOT NULL DEFAULT 0,
    "tax_base" DECIMAL(18,4) NOT NULL DEFAULT 0,
    "tax_amount" DECIMAL(18,4) NOT NULL DEFAULT 0,
    "nominal_code" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "document_tax_summary_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "User_email_key" ON "User"("email");

-- CreateIndex
CREATE INDEX "auth_otp_challenges_user_id_purpose_idx" ON "auth_otp_challenges"("user_id", "purpose");

-- CreateIndex
CREATE INDEX "company_memberships_company_id_idx" ON "company_memberships"("company_id");

-- CreateIndex
CREATE INDEX "company_memberships_user_id_idx" ON "company_memberships"("user_id");

-- CreateIndex
CREATE UNIQUE INDEX "company_memberships_company_id_user_id_key" ON "company_memberships"("company_id", "user_id");

-- CreateIndex
CREATE INDEX "roles_company_id_idx" ON "roles"("company_id");

-- CreateIndex
CREATE UNIQUE INDEX "business_information_company_id_key" ON "business_information"("company_id");

-- CreateIndex
CREATE UNIQUE INDEX "smart_settings_company_id_key" ON "smart_settings"("company_id");

-- CreateIndex
CREATE UNIQUE INDEX "lock_date_settings_company_id_key" ON "lock_date_settings"("company_id");

-- CreateIndex
CREATE UNIQUE INDEX "lock_date_per_user_lock_date_settings_id_user_id_key" ON "lock_date_per_user"("lock_date_settings_id", "user_id");

-- CreateIndex
CREATE UNIQUE INDEX "taxes_year_end_config_company_id_key" ON "taxes_year_end_config"("company_id");

-- CreateIndex
CREATE INDEX "coa_categories_company_id_idx" ON "coa_categories"("company_id");

-- CreateIndex
CREATE UNIQUE INDEX "coa_categories_company_id_code_key" ON "coa_categories"("company_id", "code");

-- CreateIndex
CREATE INDEX "coa_sections_category_id_idx" ON "coa_sections"("category_id");

-- CreateIndex
CREATE UNIQUE INDEX "coa_sections_category_id_code_key" ON "coa_sections"("category_id", "code");

-- CreateIndex
CREATE INDEX "nominal_accounts_section_id_idx" ON "nominal_accounts"("section_id");

-- CreateIndex
CREATE UNIQUE INDEX "nominal_accounts_section_id_code_key" ON "nominal_accounts"("section_id", "code");

-- CreateIndex
CREATE INDEX "bank_accounts_company_id_idx" ON "bank_accounts"("company_id");

-- CreateIndex
CREATE INDEX "customers_company_id_idx" ON "customers"("company_id");

-- CreateIndex
CREATE UNIQUE INDEX "customers_company_id_code_key" ON "customers"("company_id", "code");

-- CreateIndex
CREATE INDEX "suppliers_company_id_idx" ON "suppliers"("company_id");

-- CreateIndex
CREATE UNIQUE INDEX "suppliers_company_id_code_key" ON "suppliers"("company_id", "code");

-- CreateIndex
CREATE INDEX "products_company_id_idx" ON "products"("company_id");

-- CreateIndex
CREATE UNIQUE INDEX "products_company_id_code_key" ON "products"("company_id", "code");

-- CreateIndex
CREATE INDEX "projects_company_id_idx" ON "projects"("company_id");

-- CreateIndex
CREATE UNIQUE INDEX "projects_company_id_code_key" ON "projects"("company_id", "code");

-- CreateIndex
CREATE INDEX "locations_company_id_idx" ON "locations"("company_id");

-- CreateIndex
CREATE UNIQUE INDEX "locations_company_id_code_key" ON "locations"("company_id", "code");

-- CreateIndex
CREATE INDEX "journals_company_id_journal_date_idx" ON "journals"("company_id", "journal_date");

-- CreateIndex
CREATE INDEX "journal_lines_journal_id_idx" ON "journal_lines"("journal_id");

-- CreateIndex
CREATE UNIQUE INDEX "sales_invoices_journal_id_key" ON "sales_invoices"("journal_id");

-- CreateIndex
CREATE INDEX "sales_invoices_company_id_invoice_date_idx" ON "sales_invoices"("company_id", "invoice_date");

-- CreateIndex
CREATE INDEX "sales_invoice_lines_sales_invoice_id_idx" ON "sales_invoice_lines"("sales_invoice_id");

-- CreateIndex
CREATE UNIQUE INDEX "supplier_bills_journal_id_key" ON "supplier_bills"("journal_id");

-- CreateIndex
CREATE INDEX "supplier_bills_company_id_bill_date_idx" ON "supplier_bills"("company_id", "bill_date");

-- CreateIndex
CREATE INDEX "supplier_bill_lines_supplier_bill_id_idx" ON "supplier_bill_lines"("supplier_bill_id");

-- CreateIndex
CREATE UNIQUE INDEX "bank_payments_journal_id_key" ON "bank_payments"("journal_id");

-- CreateIndex
CREATE INDEX "bank_payments_company_id_payment_date_idx" ON "bank_payments"("company_id", "payment_date");

-- CreateIndex
CREATE UNIQUE INDEX "sales_receipts_journal_id_key" ON "sales_receipts"("journal_id");

-- CreateIndex
CREATE INDEX "sales_receipts_company_id_receipt_date_idx" ON "sales_receipts"("company_id", "receipt_date");

-- CreateIndex
CREATE UNIQUE INDEX "supplier_payments_journal_id_key" ON "supplier_payments"("journal_id");

-- CreateIndex
CREATE INDEX "supplier_payments_company_id_payment_date_idx" ON "supplier_payments"("company_id", "payment_date");

-- CreateIndex
CREATE INDEX "sales_receipt_allocations_sales_receipt_id_idx" ON "sales_receipt_allocations"("sales_receipt_id");

-- CreateIndex
CREATE INDEX "sales_receipt_allocations_sales_invoice_id_idx" ON "sales_receipt_allocations"("sales_invoice_id");

-- CreateIndex
CREATE INDEX "supplier_payment_allocations_supplier_payment_id_idx" ON "supplier_payment_allocations"("supplier_payment_id");

-- CreateIndex
CREATE INDEX "supplier_payment_allocations_supplier_bill_id_idx" ON "supplier_payment_allocations"("supplier_bill_id");

-- CreateIndex
CREATE UNIQUE INDEX "bank_receipts_journal_id_key" ON "bank_receipts"("journal_id");

-- CreateIndex
CREATE INDEX "bank_receipts_company_id_receipt_date_idx" ON "bank_receipts"("company_id", "receipt_date");

-- CreateIndex
CREATE INDEX "quotations_company_id_quotation_date_idx" ON "quotations"("company_id", "quotation_date");

-- CreateIndex
CREATE INDEX "quotation_lines_quotation_id_idx" ON "quotation_lines"("quotation_id");

-- CreateIndex
CREATE INDEX "sales_orders_company_id_order_date_idx" ON "sales_orders"("company_id", "order_date");

-- CreateIndex
CREATE INDEX "sales_order_lines_sales_order_id_idx" ON "sales_order_lines"("sales_order_id");

-- CreateIndex
CREATE INDEX "purchase_orders_company_id_order_date_idx" ON "purchase_orders"("company_id", "order_date");

-- CreateIndex
CREATE INDEX "purchase_order_lines_purchase_order_id_idx" ON "purchase_order_lines"("purchase_order_id");

-- CreateIndex
CREATE UNIQUE INDEX "sales_credits_journal_id_key" ON "sales_credits"("journal_id");

-- CreateIndex
CREATE INDEX "sales_credits_company_id_credit_date_idx" ON "sales_credits"("company_id", "credit_date");

-- CreateIndex
CREATE INDEX "sales_credit_lines_sales_credit_id_idx" ON "sales_credit_lines"("sales_credit_id");

-- CreateIndex
CREATE UNIQUE INDEX "supplier_credits_journal_id_key" ON "supplier_credits"("journal_id");

-- CreateIndex
CREATE INDEX "supplier_credits_company_id_credit_date_idx" ON "supplier_credits"("company_id", "credit_date");

-- CreateIndex
CREATE INDEX "supplier_credit_lines_supplier_credit_id_idx" ON "supplier_credit_lines"("supplier_credit_id");

-- CreateIndex
CREATE UNIQUE INDEX "bank_transfers_journal_id_key" ON "bank_transfers"("journal_id");

-- CreateIndex
CREATE INDEX "bank_transfers_company_id_transfer_date_idx" ON "bank_transfers"("company_id", "transfer_date");

-- CreateIndex
CREATE INDEX "attachments_company_id_entity_type_entity_id_idx" ON "attachments"("company_id", "entity_type", "entity_id");

-- CreateIndex
CREATE UNIQUE INDEX "document_number_sequences_company_id_key_key" ON "document_number_sequences"("company_id", "key");

-- CreateIndex
CREATE INDEX "import_jobs_company_id_status_idx" ON "import_jobs"("company_id", "status");

-- CreateIndex
CREATE INDEX "audit_log_entries_company_id_created_at_idx" ON "audit_log_entries"("company_id", "created_at");

-- CreateIndex
CREATE INDEX "approval_policies_company_id_entity_type_idx" ON "approval_policies"("company_id", "entity_type");

-- CreateIndex
CREATE INDEX "stock_adjustments_company_id_adjustment_date_idx" ON "stock_adjustments"("company_id", "adjustment_date");

-- CreateIndex
CREATE INDEX "stock_adjustment_lines_stock_adjustment_id_idx" ON "stock_adjustment_lines"("stock_adjustment_id");

-- CreateIndex
CREATE INDEX "stock_transfers_company_id_transfer_date_idx" ON "stock_transfers"("company_id", "transfer_date");

-- CreateIndex
CREATE INDEX "stock_transfer_lines_stock_transfer_id_idx" ON "stock_transfer_lines"("stock_transfer_id");

-- CreateIndex
CREATE INDEX "product_batches_company_id_expiry_date_idx" ON "product_batches"("company_id", "expiry_date");

-- CreateIndex
CREATE UNIQUE INDEX "product_batches_company_id_product_code_batch_number_key" ON "product_batches"("company_id", "product_code", "batch_number");

-- CreateIndex
CREATE INDEX "delivery_notes_company_id_delivery_date_idx" ON "delivery_notes"("company_id", "delivery_date");

-- CreateIndex
CREATE INDEX "delivery_note_lines_delivery_note_id_idx" ON "delivery_note_lines"("delivery_note_id");

-- CreateIndex
CREATE INDEX "goods_receipt_notes_company_id_receipt_date_idx" ON "goods_receipt_notes"("company_id", "receipt_date");

-- CreateIndex
CREATE INDEX "goods_receipt_note_lines_goods_receipt_note_id_idx" ON "goods_receipt_note_lines"("goods_receipt_note_id");

-- CreateIndex
CREATE UNIQUE INDEX "pdc_received_linked_receipt_id_key" ON "pdc_received"("linked_receipt_id");

-- CreateIndex
CREATE INDEX "pdc_received_company_id_cheque_date_idx" ON "pdc_received"("company_id", "cheque_date");

-- CreateIndex
CREATE UNIQUE INDEX "pdc_issued_linked_payment_id_key" ON "pdc_issued"("linked_payment_id");

-- CreateIndex
CREATE INDEX "pdc_issued_company_id_cheque_date_idx" ON "pdc_issued"("company_id", "cheque_date");

-- CreateIndex
CREATE INDEX "document_tax_summary_company_id_document_kind_document_id_idx" ON "document_tax_summary"("company_id", "document_kind", "document_id");

-- CreateIndex
CREATE INDEX "document_tax_summary_company_id_tax_code_idx" ON "document_tax_summary"("company_id", "tax_code");

-- AddForeignKey
ALTER TABLE "auth_otp_challenges" ADD CONSTRAINT "auth_otp_challenges_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "company_memberships" ADD CONSTRAINT "company_memberships_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "company_memberships" ADD CONSTRAINT "company_memberships_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "company_memberships" ADD CONSTRAINT "company_memberships_role_id_fkey" FOREIGN KEY ("role_id") REFERENCES "roles"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "roles" ADD CONSTRAINT "roles_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "business_information" ADD CONSTRAINT "business_information_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "smart_settings" ADD CONSTRAINT "smart_settings_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "lock_date_settings" ADD CONSTRAINT "lock_date_settings_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "lock_date_per_user" ADD CONSTRAINT "lock_date_per_user_lock_date_settings_id_fkey" FOREIGN KEY ("lock_date_settings_id") REFERENCES "lock_date_settings"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "lock_date_per_user" ADD CONSTRAINT "lock_date_per_user_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "taxes_year_end_config" ADD CONSTRAINT "taxes_year_end_config_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "coa_categories" ADD CONSTRAINT "coa_categories_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "coa_sections" ADD CONSTRAINT "coa_sections_category_id_fkey" FOREIGN KEY ("category_id") REFERENCES "coa_categories"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "nominal_accounts" ADD CONSTRAINT "nominal_accounts_section_id_fkey" FOREIGN KEY ("section_id") REFERENCES "coa_sections"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "bank_accounts" ADD CONSTRAINT "bank_accounts_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "customers" ADD CONSTRAINT "customers_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "suppliers" ADD CONSTRAINT "suppliers_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "products" ADD CONSTRAINT "products_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "projects" ADD CONSTRAINT "projects_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "locations" ADD CONSTRAINT "locations_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "journals" ADD CONSTRAINT "journals_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "journal_lines" ADD CONSTRAINT "journal_lines_journal_id_fkey" FOREIGN KEY ("journal_id") REFERENCES "journals"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "sales_invoices" ADD CONSTRAINT "sales_invoices_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "sales_invoice_lines" ADD CONSTRAINT "sales_invoice_lines_sales_invoice_id_fkey" FOREIGN KEY ("sales_invoice_id") REFERENCES "sales_invoices"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "supplier_bills" ADD CONSTRAINT "supplier_bills_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "supplier_bill_lines" ADD CONSTRAINT "supplier_bill_lines_supplier_bill_id_fkey" FOREIGN KEY ("supplier_bill_id") REFERENCES "supplier_bills"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "bank_payments" ADD CONSTRAINT "bank_payments_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "sales_receipts" ADD CONSTRAINT "sales_receipts_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "supplier_payments" ADD CONSTRAINT "supplier_payments_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "sales_receipt_allocations" ADD CONSTRAINT "sales_receipt_allocations_sales_receipt_id_fkey" FOREIGN KEY ("sales_receipt_id") REFERENCES "sales_receipts"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "sales_receipt_allocations" ADD CONSTRAINT "sales_receipt_allocations_sales_invoice_id_fkey" FOREIGN KEY ("sales_invoice_id") REFERENCES "sales_invoices"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "supplier_payment_allocations" ADD CONSTRAINT "supplier_payment_allocations_supplier_payment_id_fkey" FOREIGN KEY ("supplier_payment_id") REFERENCES "supplier_payments"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "supplier_payment_allocations" ADD CONSTRAINT "supplier_payment_allocations_supplier_bill_id_fkey" FOREIGN KEY ("supplier_bill_id") REFERENCES "supplier_bills"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "bank_receipts" ADD CONSTRAINT "bank_receipts_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "quotations" ADD CONSTRAINT "quotations_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "quotation_lines" ADD CONSTRAINT "quotation_lines_quotation_id_fkey" FOREIGN KEY ("quotation_id") REFERENCES "quotations"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "sales_orders" ADD CONSTRAINT "sales_orders_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "sales_order_lines" ADD CONSTRAINT "sales_order_lines_sales_order_id_fkey" FOREIGN KEY ("sales_order_id") REFERENCES "sales_orders"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "purchase_orders" ADD CONSTRAINT "purchase_orders_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "purchase_order_lines" ADD CONSTRAINT "purchase_order_lines_purchase_order_id_fkey" FOREIGN KEY ("purchase_order_id") REFERENCES "purchase_orders"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "sales_credits" ADD CONSTRAINT "sales_credits_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "sales_credit_lines" ADD CONSTRAINT "sales_credit_lines_sales_credit_id_fkey" FOREIGN KEY ("sales_credit_id") REFERENCES "sales_credits"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "supplier_credits" ADD CONSTRAINT "supplier_credits_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "supplier_credit_lines" ADD CONSTRAINT "supplier_credit_lines_supplier_credit_id_fkey" FOREIGN KEY ("supplier_credit_id") REFERENCES "supplier_credits"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "bank_transfers" ADD CONSTRAINT "bank_transfers_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "attachments" ADD CONSTRAINT "attachments_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "document_number_sequences" ADD CONSTRAINT "document_number_sequences_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "import_jobs" ADD CONSTRAINT "import_jobs_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "audit_log_entries" ADD CONSTRAINT "audit_log_entries_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "approval_policies" ADD CONSTRAINT "approval_policies_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "stock_adjustments" ADD CONSTRAINT "stock_adjustments_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "stock_adjustment_lines" ADD CONSTRAINT "stock_adjustment_lines_stock_adjustment_id_fkey" FOREIGN KEY ("stock_adjustment_id") REFERENCES "stock_adjustments"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "stock_transfers" ADD CONSTRAINT "stock_transfers_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "stock_transfer_lines" ADD CONSTRAINT "stock_transfer_lines_stock_transfer_id_fkey" FOREIGN KEY ("stock_transfer_id") REFERENCES "stock_transfers"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "product_batches" ADD CONSTRAINT "product_batches_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "delivery_notes" ADD CONSTRAINT "delivery_notes_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "delivery_note_lines" ADD CONSTRAINT "delivery_note_lines_delivery_note_id_fkey" FOREIGN KEY ("delivery_note_id") REFERENCES "delivery_notes"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "goods_receipt_notes" ADD CONSTRAINT "goods_receipt_notes_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "goods_receipt_note_lines" ADD CONSTRAINT "goods_receipt_note_lines_goods_receipt_note_id_fkey" FOREIGN KEY ("goods_receipt_note_id") REFERENCES "goods_receipt_notes"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "pdc_received" ADD CONSTRAINT "pdc_received_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "pdc_issued" ADD CONSTRAINT "pdc_issued_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

