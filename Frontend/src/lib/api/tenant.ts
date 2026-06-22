/**
 * Tenant-scoped API wrappers. All paths begin with /api/v1/companies/{companyId}.
 * Pulls the current company id from auth storage; throws if none is selected.
 */
import { apiFetch, apiFetchCached } from "./client";
import { getCurrentCompanyId, getTokens } from "@/lib/auth/storage";

import { resolveApiUrl } from "@/lib/api/base-url";

function requireCompanyId(): string {
  const id = getCurrentCompanyId();
  if (!id) throw new Error("No company selected");
  return id;
}

function path(suffix: string): string {
  return `/api/v1/companies/${requireCompanyId()}${suffix}`;
}

export interface BusinessInformation {
  businessName?: string | null;
  branchName?: string | null;
  addressLine1?: string | null;
  addressLine2?: string | null;
  addressLine3?: string | null;
  addressLine4?: string | null;
  addressLine5?: string | null;
  phoneNumber?: string | null;
  mobileNumber?: string | null;
  emailAddress?: string | null;
  websiteAddress?: string | null;
  logoUrl?: string | null;
  cnic?: string | null;
  stn?: string | null;
  ntn?: string | null;
  applyOnAllPrints?: boolean | null;
  [key: string]: unknown;
}

export const settingsApi = {
  getBusinessInformation: () =>
    apiFetch<{ result: BusinessInformation | null }>(path("/business-information")),
  putBusinessInformation: (body: BusinessInformation) =>
    apiFetch<{ result: BusinessInformation }>(path("/business-information"), {
      method: "PUT",
      body,
    }),

  getLockDate: () =>
    apiFetch<{ result: { globalLockDate?: string | null } | null }>(path("/lock-date")),
  putLockDate: (body: { globalLockDate: string | null }) =>
    apiFetch<{ result: { globalLockDate?: string | null } }>(path("/lock-date"), {
      method: "PUT",
      body,
    }),
  putLockDatePerUser: (userId: string, extendedLockDate: string) =>
    apiFetch<{ result: { userId: string; extendedLockDate: string } }>(
      path(`/lock-date/users/${userId}`),
      { method: "PUT", body: { extendedLockDate } },
    ),

  getSmartSettings: () =>
    apiFetch<{ result: { payload: Record<string, unknown> } }>(path("/smart-settings")),
  putSmartSettings: (payload: Record<string, unknown>) =>
    apiFetch<{ result: { payload: Record<string, unknown> } }>(path("/smart-settings"), {
      method: "PUT",
      body: { payload },
    }),

  getTaxesYearEnd: () =>
    apiFetch<{ result: TaxesYearEnd | null }>(path("/taxes-year-end")),
  putTaxesYearEnd: (body: TaxesYearEnd) =>
    apiFetch<{ result: TaxesYearEnd }>(path("/taxes-year-end"), {
      method: "PUT",
      body,
    }),
};

export interface PrintTemplateSettings {
  code: string;
  title: string;
  showLogo: boolean;
  showBusinessBlock: boolean;
  headerNote: string;
  footerNote: string;
  paperSize: "A4" | "Letter";
  showTaxColumns: boolean;
  printMode?: string;
  twoCopies?: boolean;
  [key: string]: unknown;
}

export interface ListingColumnSetting {
  key: string;
  label: string;
  active: boolean;
  order: number;
}

export interface MenuItemSetting {
  href: string;
  group: string;
  label: string;
  active: boolean;
  order: number;
}

export interface AdvanceUserRule {
  userId: string;
  userLabel?: string;
  customerIds?: string[];
  supplierIds?: string[];
  productIds?: string[];
}

export const appSettingsApi = {
  listPrintTemplates: () =>
    apiFetch<{ result: { code: string; label: string; group: string }[] }>(
      path("/print-templates"),
    ),
  getPrintTemplate: (code: string) =>
    apiFetch<{ result: PrintTemplateSettings }>(path(`/print-templates/${code}`)),
  putPrintTemplate: (code: string, body: Partial<PrintTemplateSettings>) =>
    apiFetch<{ result: PrintTemplateSettings }>(path(`/print-templates/${code}`), {
      method: "PUT",
      body,
    }),
  listContentListings: () =>
    apiFetch<{ result: { id: string; label: string; branch: string }[] }>(
      path("/content-settings/listings"),
    ),
  getListingLayout: (listingId: string) =>
    apiFetch<{ result: { listingId: string; columns: ListingColumnSetting[] } }>(
      path(`/content-settings/listings/${listingId}`),
    ),
  putListingLayout: (listingId: string, columns: ListingColumnSetting[]) =>
    apiFetch<{ result: { listingId: string; columns: ListingColumnSetting[] } }>(
      path(`/content-settings/listings/${listingId}`),
      { method: "PUT", body: { columns } },
    ),
  listContentForms: () =>
    apiFetch<{ result: { id: string; label: string; branch: string }[] }>(
      path("/content-settings/forms"),
    ),
  getFormLayout: (formId: string) =>
    apiFetch<{ result: { formId: string; fields: ListingColumnSetting[] } }>(
      path(`/content-settings/forms/${formId}`),
    ),
  putFormLayout: (formId: string, fields: ListingColumnSetting[]) =>
    apiFetch<{ result: { formId: string; fields: ListingColumnSetting[] } }>(
      path(`/content-settings/forms/${formId}`),
      { method: "PUT", body: { fields } },
    ),
  getMenuLayout: () =>
    apiFetchCached<{ result: { items: MenuItemSetting[] } }>(path("/content-settings/menu")),
  putMenuLayout: (items: MenuItemSetting[]) =>
    apiFetch<{ result: { items: MenuItemSetting[] } }>(path("/content-settings/menu"), {
      method: "PUT",
      body: { items },
    }),
  getFiltersSettings: () =>
    apiFetch<{ result: Record<string, unknown> }>(path("/application-settings/filters")),
  putFiltersSettings: (body: Record<string, unknown>) =>
    apiFetch<{ result: Record<string, unknown> }>(path("/application-settings/filters"), {
      method: "PUT",
      body,
    }),
  getColumnsSettings: () =>
    apiFetch<{ result: Record<string, unknown> }>(path("/application-settings/columns")),
  putColumnsSettings: (body: Record<string, unknown>) =>
    apiFetch<{ result: Record<string, unknown> }>(path("/application-settings/columns"), {
      method: "PUT",
      body,
    }),
  getEmailSettings: () =>
    apiFetch<{ result: Record<string, unknown> }>(path("/application-settings/email")),
  putEmailSettings: (body: Record<string, unknown>) =>
    apiFetch<{ result: Record<string, unknown> }>(path("/application-settings/email"), {
      method: "PUT",
      body,
    }),
  getDashboardSettings: () =>
    apiFetch<{ result: Record<string, unknown> }>(path("/application-settings/dashboards")),
  putDashboardSettings: (body: Record<string, unknown>) =>
    apiFetch<{ result: Record<string, unknown> }>(path("/application-settings/dashboards"), {
      method: "PUT",
      body,
    }),
  getAdvanceUsersSettings: () =>
    apiFetch<{ result: { rules: AdvanceUserRule[] } }>(
      path("/application-settings/advance-users"),
    ),
  putAdvanceUsersSettings: (body: { rules: AdvanceUserRule[] }) =>
    apiFetch<{ result: { rules: AdvanceUserRule[] } }>(
      path("/application-settings/advance-users"),
      { method: "PUT", body },
    ),
  getOpMethodsSettings: () =>
    apiFetch<{ result: Record<string, unknown> }>(path("/application-settings/op-methods")),
  putOpMethodsSettings: (body: Record<string, unknown>) =>
    apiFetch<{ result: Record<string, unknown> }>(path("/application-settings/op-methods"), {
      method: "PUT",
      body,
    }),
  getMissedRecurrenceSettings: () =>
    apiFetch<{ result: Record<string, unknown> }>(
      path("/application-settings/missed-recurrence"),
    ),
  putMissedRecurrenceSettings: (body: Record<string, unknown>) =>
    apiFetch<{ result: Record<string, unknown> }>(
      path("/application-settings/missed-recurrence"),
      { method: "PUT", body },
    ),
  listSentEmails: () =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/sent-emails")),
};

export interface CoaCategory {
  id: string;
  name: string;
  code?: string | null;
  type?: string | null;
  [key: string]: unknown;
}

export interface Customer {
  id: string;
  name: string;
  code?: string | null;
  email?: string | null;
  phone?: string | null;
  [key: string]: unknown;
}

export interface Supplier {
  id: string;
  name: string;
  code?: string | null;
  [key: string]: unknown;
}

export interface Product {
  id: string;
  name: string;
  code?: string | null;
  unit?: string | null;
  category?: string | null;
  salePrice?: string | number | null;
  cost?: string | number | null;
  isStock?: boolean;
  isArchived?: boolean;
  primaryImageAttachmentId?: string | null;
  lowStockLevel?: string | number | null;
  binLocation?: string | null;
  customFields?: Record<string, unknown>;
  uoms?: ProductUomRow[];
  [key: string]: unknown;
}

export interface ProductUomRow {
  id?: string;
  unitCode: string;
  conversionFactor: string;
  salePrice: string;
  isDefault?: boolean;
  synthetic?: boolean;
  [key: string]: unknown;
}

export interface BankAccount {
  id: string;
  name: string;
  code?: string | null;
  currency?: string | null;
  openingBalance?: string | number | null;
  [key: string]: unknown;
}

export interface BankPayment {
  id: string;
  voucherNumber?: string | null;
  paymentDate: string;
  totalAmount: string | number;
  bankAccountId: string;
  nominalCode?: string | null;
  journalId?: string | null;
  status?: string;
  [key: string]: unknown;
}

export interface SalesInvoice {
  id: string;
  documentNumber?: string | null;
  invoiceDate: string;
  customerId: string;
  totalAmount: string | number;
  status?: string;
  journalId?: string | null;
  [key: string]: unknown;
}

export interface SupplierBill {
  id: string;
  documentNumber?: string | null;
  billDate: string;
  supplierId: string;
  totalAmount: string | number;
  status?: string;
  journalId?: string | null;
  [key: string]: unknown;
}

export interface JournalLine {
  id: string;
  nominalCode: string;
  debit: string | number;
  credit: string | number;
  projectCode?: string | null;
  [key: string]: unknown;
}

export interface Journal {
  id: string;
  journalNumber?: string | null;
  journalDate: string;
  refNo?: string | null;
  reference?: string | null;
  totalAmount?: string | number;
  totalDebit?: string | number;
  totalCredit?: string | number;
  status?: string;
  sourceType?: string | null;
  sourceId?: string | null;
  lines?: JournalLine[];
  [key: string]: unknown;
}

export interface CoaSection {
  id: string;
  code: string;
  name: string;
  sortOrder: number;
  categoryId: string;
  categoryName?: string | null;
  categoryCode?: string | null;
  [key: string]: unknown;
}

export interface CoaNominal {
  id: string;
  code: string;
  name: string;
  description?: string | null;
  isChargeDeduction: boolean;
}

export interface CoaTreeSection {
  id: string;
  code: string;
  name: string;
  sortOrder: number;
  nominals: CoaNominal[];
}

export type CategoryType =
  | "Income"
  | "Expense"
  | "Asset"
  | "Liability"
  | "Equity"
  | "Other";

export interface CoaTreeCategory {
  id: string;
  code: string;
  name: string;
  sortOrder: number;
  categoryType?: CategoryType;
  sections: CoaTreeSection[];
}

export interface CreateSectionInput {
  categoryId: string;
  code: string;
  name: string;
}

export interface CreateNominalInput {
  sectionId: string;
  code?: string | null;
  name: string;
  description?: string | null;
  isChargeDeduction?: boolean;
}

export interface UpdateNominalInput {
  name?: string;
  description?: string | null;
  isChargeDeduction?: boolean;
}

export interface MoveNominalInput {
  sectionId: string;
}

export const ledgerApi = {
  listCoaCategories: () =>
    apiFetch<{ result: CoaCategory[] }>(path("/coa/categories")),
  getCoaTree: () =>
    apiFetchCached<{ result: CoaTreeCategory[] }>(path("/coa/tree")),
  listSections: () =>
    apiFetch<{ result: CoaSection[] }>(path("/coa/sections")),
  createSection: (body: CreateSectionInput) =>
    apiFetch<{ result: CoaSection }>(path("/coa/sections"), { method: "POST", body }),
  reorderSection: (sectionId: string, direction: "up" | "down") =>
    apiFetch<{ result: CoaSection }>(path(`/coa/sections/${sectionId}/reorder`), {
      method: "PUT",
      body: { direction },
    }),
  createNominal: (body: CreateNominalInput) =>
    apiFetch<{ result: CoaNominal }>(path("/coa/nominals"), { method: "POST", body }),
  updateNominal: (id: string, body: UpdateNominalInput) =>
    apiFetch<{ result: CoaNominal }>(path(`/coa/nominals/${id}`), { method: "PATCH", body }),
  moveNominal: (id: string, body: MoveNominalInput) =>
    apiFetch<{ result: CoaNominal }>(path(`/coa/nominals/${id}/section`), {
      method: "PUT",
      body,
    }),
  deleteNominal: (id: string) =>
    apiFetch<void>(path(`/coa/nominals/${id}`), { method: "DELETE" }),
  bulkDeleteNominals: (nominalIds: string[]) =>
    apiFetch<{ result: { deleted: number; skipped: number } }>(
      path("/coa/nominals/bulk-delete"),
      { method: "POST", body: { nominalIds } },
    ),
  updateCategoryType: (categoryId: string, categoryType: CategoryType) =>
    apiFetch<{ result: { id: string; categoryType: CategoryType } }>(
      path(`/coa/categories/${categoryId}/type`),
      { method: "PUT", body: { categoryType } },
    ),
  listJournals: () => apiFetch<{ result: Journal[] }>(path("/journals")),
  getJournal: (id: string) => apiFetch<{ result: Journal }>(path(`/journals/${id}`)),
};

export interface CreateCustomerInput {
  code?: string | null;
  name: string;
  email?: string | null;
  phone?: string | null;
}

export interface CreateSupplierInput {
  code?: string | null;
  name: string;
  email?: string | null;
  phone?: string | null;
}

export interface OpenInvoiceRow {
  id: string;
  invoiceNumber?: string;
  invoiceDate?: string;
  totalAmount?: string;
  remaining: string;
}

export interface OpenBillRow {
  id: string;
  billNumber?: string;
  billDate?: string;
  totalAmount?: string;
  remaining: string;
}

export const partiesApi = {
  listCustomers: () => apiFetch<{ result: Customer[] }>(path("/customers")),
  createCustomer: (body: CreateCustomerInput) =>
    apiFetch<{ result: Customer }>(path("/customers"), { method: "POST", body }),
  listSuppliers: () => apiFetch<{ result: Supplier[] }>(path("/suppliers")),
  createSupplier: (body: CreateSupplierInput) =>
    apiFetch<{ result: Supplier }>(path("/suppliers"), { method: "POST", body }),
  listOpenInvoices: (customerId: string) =>
    apiFetch<{ result: OpenInvoiceRow[] }>(path(`/customers/${customerId}/open-invoices`)),
  listOpenBills: (supplierId: string) =>
    apiFetch<{ result: OpenBillRow[] }>(path(`/suppliers/${supplierId}/open-bills`)),
};

export interface CreateProductInput {
  code?: string | null;
  name: string;
  isStock: boolean;
  unit?: string;
  category?: string | null;
  salePrice?: number | string | null;
  cost?: number | string | null;
  lowStockLevel?: number | string | null;
  binLocation?: string | null;
  openingStock?: { quantity: number | string; rate?: number | string | null };
}

export interface UpdateProductInput {
  name: string;
  isStock: boolean;
  unit?: string;
  category?: string | null;
  salePrice?: number | string | null;
  cost?: number | string | null;
  lowStockLevel?: number | string | null;
  binLocation?: string | null;
  customFields?: Record<string, unknown>;
}

export const inventoryApi = {
  listProducts: (params?: { page?: number; pageSize?: number; includeArchived?: boolean }) =>
    apiFetch<{ result: Product[]; total?: number; page?: number; pageSize?: number }>(
      path("/products"),
      {
        query: {
          page: params?.page,
          pageSize: params?.pageSize,
          includeArchived: params?.includeArchived,
        },
      },
    ),
  searchProducts: (q: string, limit = 20) =>
    apiFetch<{ result: Product[] }>(path("/products/search"), { query: { q, limit } }),
  getProduct: (productId: string) =>
    apiFetch<{ result: Product }>(path(`/products/${productId}`)),
  createProduct: (body: CreateProductInput) =>
    apiFetch<{ result: Product }>(path("/products"), { method: "POST", body }),
  updateProduct: (productId: string, body: UpdateProductInput) =>
    apiFetch<{ result: Product }>(path(`/products/${productId}`), { method: "PUT", body }),
  archiveProduct: (productId: string) =>
    apiFetch<{ result: Product }>(path(`/products/${productId}/archive`), { method: "POST" }),
  restoreProduct: (productId: string) =>
    apiFetch<{ result: Product }>(path(`/products/${productId}/restore`), { method: "POST" }),
  setPrimaryImage: (productId: string, attachmentId: string | null) =>
    apiFetch<{ result: Product }>(path(`/products/${productId}/primary-image`), {
      method: "PATCH",
      body: { attachmentId },
    }),
  applyOpeningStock: (
    productId: string,
    body: { quantity: number | string; rate?: number | string | null },
  ) =>
    apiFetch<{ result: Product }>(path(`/products/${productId}/opening-stock`), {
      method: "POST",
      body,
    }),
  listProductUoms: (productId: string) =>
    apiFetch<{ result: ProductUomRow[] }>(path(`/products/${productId}/uoms`)),
  upsertProductUom: (
    productId: string,
    body: {
      unitCode: string;
      conversionFactor: string;
      salePrice: string;
      isDefault?: boolean;
    },
  ) =>
    apiFetch<{ result: ProductUomRow }>(path(`/products/${productId}/uoms`), {
      method: "POST",
      body,
    }),
};

export interface BankPaymentNominalLineInput {
  nominalCode: string;
  amount: string;
}

export interface BankPaymentCreateInput {
  bankAccountId: string;
  paymentDate: string;
  totalAmount: string;
  /** Counterpart nominal — DR side of the auto-posted journal. */
  nominalCode?: string;
  nominalLines?: BankPaymentNominalLineInput[];
  smartFilters?: Record<string, string>;
}

export interface CreateBankAccountInput {
  name: string;
  nominalCode?: string | null;
  currency: string;
}

export interface BankReceipt {
  id: string;
  voucherNumber?: string | null;
  receiptDate: string;
  bankAccountId: string;
  nominalCode?: string | null;
  totalAmount: string | number;
  status?: string;
  journalId?: string | null;
  [key: string]: unknown;
}

export interface BankReceiptCreateInput {
  bankAccountId: string;
  receiptDate: string;
  totalAmount: string;
  nominalCode?: string;
}

export interface BankTransfer {
  id: string;
  voucherNumber?: string | null;
  transferDate: string;
  fromBankAccountId: string;
  toBankAccountId: string;
  totalAmount: string | number;
  status?: string;
  journalId?: string | null;
  [key: string]: unknown;
}

export interface BankTransferCreateInput {
  fromBankAccountId: string;
  toBankAccountId: string;
  transferDate: string;
  totalAmount: string;
}

export const bankApi = {
  listAccounts: () => apiFetch<{ result: BankAccount[] }>(path("/bank-accounts")),
  createAccount: (body: CreateBankAccountInput) =>
    apiFetch<{ result: BankAccount }>(path("/bank-accounts"), { method: "POST", body }),
  listPayments: () => apiFetch<{ result: BankPayment[] }>(path("/bank-payments")),
  getPayment: (id: string) =>
    apiFetch<{ result: BankPayment }>(path(`/bank-payments/${id}`)),
  createPayment: (body: BankPaymentCreateInput) =>
    apiFetch<BankPayment>(path("/bank-payments"), { method: "POST", body }),
  copyPayment: (id: string) =>
    apiFetch<{ result: BankPayment; copiedFromId?: string }>(
      path(`/bank-payments/${id}/copy`),
      { method: "POST" },
    ),
  postPayment: (id: string) =>
    apiFetch<{ result: BankPayment; posted: boolean }>(
      path(`/bank-payments/${id}/post`),
      { method: "POST" },
    ),
  listReceipts: () => apiFetch<{ result: BankReceipt[] }>(path("/bank-receipts")),
  getReceipt: (id: string) =>
    apiFetch<{ result: BankReceipt }>(path(`/bank-receipts/${id}`)),
  createReceipt: (body: BankReceiptCreateInput) =>
    apiFetch<{ result: BankReceipt; posted: boolean; postingWarning: string | null }>(
      path("/bank-receipts"),
      { method: "POST", body },
    ),
  postReceipt: (id: string) =>
    apiFetch<{ result: BankReceipt; posted: boolean }>(
      path(`/bank-receipts/${id}/post`),
      { method: "POST" },
    ),
  listTransfers: () => apiFetch<{ result: BankTransfer[] }>(path("/bank-transfers")),
  getTransfer: (id: string) =>
    apiFetch<{ result: BankTransfer }>(path(`/bank-transfers/${id}`)),
  createTransfer: (body: BankTransferCreateInput) =>
    apiFetch<{ result: BankTransfer; posted: boolean; postingWarning: string | null }>(
      path("/bank-transfers"),
      { method: "POST", body },
    ),
  postTransfer: (id: string) =>
    apiFetch<{ result: BankTransfer; posted: boolean }>(
      path(`/bank-transfers/${id}/post`),
      { method: "POST" },
    ),
  listReconciliations: (params?: { bankAccountId?: string }) => {
    const q = params?.bankAccountId
      ? `?bankAccountId=${encodeURIComponent(params.bankAccountId)}`
      : "";
    return apiFetch<{ result: BankReconciliationSession[] }>(
      path(`/bank-reconciliations${q}`)
    );
  },
  getReconciliation: (id: string) =>
    apiFetch<{ result: BankReconciliationSession }>(
      path(`/bank-reconciliations/${id}`)
    ),
  startReconciliation: (body: {
    bankAccountId: string;
    statementDate: string;
    statementBalance: string;
    notes?: string | null;
  }) =>
    apiFetch<{ result: BankReconciliationSession }>(path("/bank-reconciliations"), {
      method: "POST",
      body,
    }),
  completeReconciliation: (id: string) =>
    apiFetch<{ result: unknown }>(
      path(`/bank-reconciliations/${id}/complete`),
      { method: "POST" }
    ),
  clearReconciliationItems: (
    reconciliationId: string,
    body: { itemIds: string[]; cleared?: boolean },
  ) =>
    apiFetch<{ result: BankReconciliationSession }>(
      path(`/bank-reconciliations/${reconciliationId}/clear-items`),
      { method: "POST", body: { itemIds: body.itemIds, cleared: body.cleared ?? true } },
    ),
  autoMatchReconciliation: (reconciliationId: string) =>
    apiFetch<{ result: BankReconciliationSession }>(
      path(`/bank-reconciliations/${reconciliationId}/auto-match`),
      { method: "POST" },
    ),
  importStatement: async (form: FormData) => {
    const companyId = getCurrentCompanyId();
    if (!companyId) throw new Error("No company selected");
    const token = localStorage.getItem("accessToken");
    const res = await fetch(
      `/api/v1/companies/${companyId}/bank-statement-import`,
      {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: form,
      },
    );
    if (!res.ok) {
      const err = (await res.json().catch(() => ({}))) as { detail?: string };
      throw new Error(err.detail ?? res.statusText);
    }
    return res.json() as Promise<{ result: BankReconciliationSession }>;
  },
};

export interface BankReconciliationItem {
  id: string;
  itemType: string;
  itemId: string;
  transactionDate: string;
  amount: string;
  reference?: string | null;
  isCleared: boolean;
  [key: string]: unknown;
}

export interface BankReconciliationSession {
  id: string;
  bankAccountId: string;
  statementDate: string;
  statementBalance: string;
  status: string;
  items?: BankReconciliationItem[];
  [key: string]: unknown;
}

export interface SalesInvoiceLineInput {
  productCode?: string | null;
  quantity: string;
  rate: string;
  gstCode?: string | null;
  gstRate?: string | null;
  adtCode?: string | null;
  fedCode?: string | null;
  projectCode?: string | null;
  description?: string | null;
  descriptionFields?: Record<string, string> | null;
  batchNumber?: string | null;
  expiryDate?: string | null;
}

export interface SalesInvoiceCreateInput {
  invoiceDate: string;
  customerId: string;
  lines: SalesInvoiceLineInput[];
  smartFilters?: Record<string, string>;
}

export interface BatchSalesInvoiceEntryInput extends SalesInvoiceLineInput {
  customerId: string;
}

export interface BatchSalesInvoiceCreateInput {
  invoiceDate: string;
  entries: BatchSalesInvoiceEntryInput[];
  smartFilters?: Record<string, string>;
}

export interface BatchDocumentResult {
  id: string;
  documentNumber: string;
  customerId?: string;
  supplierId?: string;
  totalAmount: string;
}

export interface SalesInvoiceLine {
  id: string;
  productCode?: string | null;
  quantity: string;
  rate: string;
  lineSubtotal?: string | number;
  gstCode?: string | null;
  gstRate?: string | number | null;
  taxAmount?: string | number;
  lineTotal: string;
  projectCode?: string | null;
  [key: string]: unknown;
}

export interface SalesInvoiceDetail extends SalesInvoice {
  lines: SalesInvoiceLine[];
}

export interface SalesReceipt {
  id: string;
  receiptNumber?: string | null;
  receiptDate: string;
  customerId: string;
  bankAccountId: string;
  totalAmount: string | number;
  status?: string;
  journalId?: string | null;
  [key: string]: unknown;
}

export interface SalesReceiptAllocationInput {
  invoiceId: string;
  amount: string;
}

export interface SalesReceiptCreateInput {
  receiptDate: string;
  customerId: string;
  bankAccountId: string;
  totalAmount: string;
  /** Apply FIFO against the customer's open invoices on the server. */
  autoFifo?: boolean;
  allocations?: SalesReceiptAllocationInput[];
  whtCode?: string | null;
  whtAmount?: string | null;
  paymentMethod?: string | null;
  smartFilters?: Record<string, string>;
}

export interface ReceiptCreateResponse {
  result: SalesReceipt;
  posted: boolean;
  postingWarning: string | null;
  allocations: { id: string; salesInvoiceId: string; amount: string }[];
  totalAllocated: string;
  unallocatedBalance: string;
}

export interface SettlementBalance {
  total: string;
  allocated: string;
  returned: string;
  unallocated: string;
}

export interface AdvanceReturnRow {
  id: string;
  amount: string;
  returnDate: string;
  bankPaymentId?: string;
  bankReceiptId?: string;
  [key: string]: unknown;
}

export const salesApi = {
  listInvoices: () => apiFetch<{ result: SalesInvoice[] }>(path("/sales-invoices")),
  getInvoice: (id: string) =>
    apiFetch<{ result: SalesInvoiceDetail }>(path(`/sales-invoices/${id}`)),
  createInvoice: (body: SalesInvoiceCreateInput) =>
    apiFetch<{ result: SalesInvoiceDetail; posted?: boolean; postingWarning?: string | null }>(
      path("/sales-invoices"),
      {
        method: "POST",
        body,
      }
    ),
  createBatchInvoices: (body: BatchSalesInvoiceCreateInput) =>
    apiFetch<{ result: { created: BatchDocumentResult[]; count: number } }>(
      path("/sales-invoices/batch"),
      { method: "POST", body },
    ),
  updateInvoice: (id: string, body: SalesInvoiceCreateInput) =>
    apiFetch<{ result: SalesInvoiceDetail; taxTotal?: string }>(
      path(`/sales-invoices/${id}`),
      { method: "PATCH", body }
    ),
  approveInvoice: (id: string) =>
    apiFetch<{ result: SalesInvoiceDetail; posted: boolean }>(
      path(`/sales-invoices/${id}/approve`),
      { method: "POST" }
    ),
  copyInvoice: (id: string) =>
    apiFetch<{ result: SalesInvoiceDetail; copiedFromId?: string }>(
      path(`/sales-invoices/${id}/copy`),
      { method: "POST" }
    ),
  getGoodsIssue: (invoiceId: string) =>
    apiFetch<{ result: Record<string, unknown> }>(
      path(`/sales-invoices/${invoiceId}/goods-issue`)
    ),
  createGoodsIssue: (invoiceId: string) =>
    apiFetch<{ result: Record<string, unknown>; posted: boolean }>(
      path(`/sales-invoices/${invoiceId}/goods-issue`),
      { method: "POST" }
    ),
  getFbrStatus: (invoiceId: string) =>
    apiFetch<{ result: Record<string, unknown> | null }>(
      path(`/sales-invoices/${invoiceId}/fbr`)
    ),
  submitFbr: (invoiceId: string) =>
    apiFetch<{ result: Record<string, unknown> }>(
      path(`/sales-invoices/${invoiceId}/fbr/submit`),
      { method: "POST" }
    ),
  pollFbr: (invoiceId: string) =>
    apiFetch<{ result: Record<string, unknown> }>(
      path(`/sales-invoices/${invoiceId}/fbr/poll`),
      { method: "POST" }
    ),
  retryFbr: (invoiceId: string) =>
    apiFetch<{ result: Record<string, unknown> }>(
      path(`/sales-invoices/${invoiceId}/fbr/retry`),
      { method: "POST" }
    ),
  voidInvoice: (invoiceId: string, body?: { reversalDate?: string }) =>
    apiFetch<{ result: Record<string, unknown> }>(path(`/sales-invoices/${invoiceId}/void`), {
      method: "POST",
      body: body ?? {},
    }),
  emailInvoice: (invoiceId: string, body?: { to?: string }) =>
    apiFetch<{ result: { emailSent: boolean; to: string; invoiceId: string } }>(
      path(`/sales-invoices/${invoiceId}/email`),
      { method: "POST", body: body ?? {} },
    ),
  listReceipts: () =>
    apiFetch<{ result: SalesReceipt[] }>(path("/sales-receipts")),
  getReceipt: (id: string) =>
    apiFetch<{
      result: SalesReceipt;
      allocations: { id: string; salesInvoiceId: string; amount: string }[];
      balance?: SettlementBalance;
      advanceReturns?: AdvanceReturnRow[];
    }>(path(`/sales-receipts/${id}`)),
  returnAdvance: (
    id: string,
    body: { returnDate: string; amount: string; bankAccountId?: string },
  ) =>
    apiFetch<{ result: AdvanceReturnRow; bankPayment: Record<string, unknown>; posted: boolean }>(
      path(`/sales-receipts/${id}/return-advance`),
      { method: "POST", body },
    ),
  allocateReceipt: (
    id: string,
    body: {
      autoFifo?: boolean;
      allocations?: { invoiceId: string; amount: string }[];
    }
  ) =>
    apiFetch<{
      allocations: { id: string; salesInvoiceId: string; amount: string }[];
      totalAllocated: string;
      unallocatedBalance: string;
    }>(path(`/sales-receipts/${id}/allocate`), { method: "POST", body }),
  createReceipt: (body: SalesReceiptCreateInput) =>
    apiFetch<ReceiptCreateResponse>(path("/sales-receipts"), {
      method: "POST",
      body,
    }),
  postReceipt: (id: string) =>
    apiFetch<{ result: SalesReceipt; posted: boolean }>(
      path(`/sales-receipts/${id}/post`),
      { method: "POST" },
    ),
};

export interface ActivityRow {
  entityType: string;
  entityId: string;
  docType: string;
  documentNumber: string;
  documentDate: string;
  partyId: string;
  partyKind: "customer" | "supplier";
  totalAmount: string;
  status?: string;
  [key: string]: unknown;
}

export interface ActivityListParams {
  includePlanning?: boolean;
  dateFrom?: string;
  dateTo?: string;
  partyId?: string;
  docType?: string;
  status?: string;
}

function activityQuery(base: "sales-activity" | "purchases-activity", params?: ActivityListParams) {
  const q = new URLSearchParams();
  if (params?.includePlanning) q.set("includePlanning", "true");
  if (params?.dateFrom) q.set("dateFrom", params.dateFrom);
  if (params?.dateTo) q.set("dateTo", params.dateTo);
  if (params?.partyId) q.set("partyId", params.partyId);
  if (params?.docType) q.set("docType", params.docType);
  if (params?.status) q.set("status", params.status);
  const qs = q.toString();
  return path(`/${base}${qs ? `?${qs}` : ""}`);
}

export const activityApi = {
  listSales: (params?: ActivityListParams) =>
    apiFetch<{ result: ActivityRow[] }>(activityQuery("sales-activity", params)),
  listPurchases: (params?: ActivityListParams) =>
    apiFetch<{ result: ActivityRow[] }>(activityQuery("purchases-activity", params)),
};

export interface TaskRow {
  entityType: string;
  entityId: string;
  docType: string;
  documentNumber?: string | null;
  documentDate?: string | null;
  summary: string;
}

export interface NotificationItem {
  id: string;
  type: string;
  severity: "critical" | "warn" | "info" | "good";
  title: string;
  message: string;
  href: string;
  createdAt: string;
  read: boolean;
  productCode?: string;
  batchNumber?: string;
  expiryDate?: string | null;
}

export const notificationsApi = {
  list: () =>
    apiFetch<{ result: { items: NotificationItem[]; unreadCount: number } }>(
      path("/notifications"),
    ),
  runExpiryDigest: () =>
    apiFetch<{ result: { sent: boolean; message: string } }>(
      path("/inventory/expiry-alerts/run-due"),
      { method: "POST" },
    ),
};

export const tasksApi = {
  list: () => apiFetch<{ result: TaskRow[] }>(path("/my-tasks")),
};

export interface SupplierBillLineInput {
  productCode?: string | null;
  quantity: string;
  rate: string;
  gstCode?: string | null;
  gstRate?: string | null;
  adtCode?: string | null;
  fedCode?: string | null;
  description?: string | null;
  descriptionFields?: Record<string, string> | null;
  batchNumber?: string | null;
  expiryDate?: string | null;
}

export interface SupplierBillCreateInput {
  billDate: string;
  supplierId: string;
  lines: SupplierBillLineInput[];
  smartFilters?: Record<string, string>;
}

export interface BatchSupplierBillEntryInput extends SupplierBillLineInput {
  supplierId: string;
}

export interface BatchSupplierBillCreateInput {
  billDate: string;
  entries: BatchSupplierBillEntryInput[];
  smartFilters?: Record<string, string>;
}

export interface SupplierBillLine {
  id: string;
  productCode?: string | null;
  quantity: string;
  rate: string;
  lineSubtotal?: string | number;
  gstCode?: string | null;
  gstRate?: string | number | null;
  taxAmount?: string | number;
  lineTotal: string;
  [key: string]: unknown;
}

export interface SupplierBillDetail extends SupplierBill {
  lines: SupplierBillLine[];
}

/* ---------------- Sprint 4 — Quotations, Orders, Credits ---------------- */

export interface DocumentLineInput {
  productCode?: string | null;
  quantity: string;
  rate: string;
  gstCode?: string | null;
  gstRate?: string | number | null;
}

export interface DocumentLine {
  id: string;
  productCode?: string | null;
  quantity: string;
  rate: string;
  lineSubtotal?: string | number;
  gstCode?: string | null;
  gstRate?: string | number | null;
  taxAmount?: string | number;
  lineTotal: string;
  projectCode?: string | null;
  [key: string]: unknown;
}

export interface Quotation {
  id: string;
  quotationNumber: string;
  quotationDate: string;
  customerId: string;
  status: string;
  totalAmount: string | number;
  [key: string]: unknown;
}
export interface QuotationDetail extends Quotation { lines: DocumentLine[]; }
export interface QuotationCreateInput {
  quotationDate: string;
  customerId: string;
  lines: DocumentLineInput[];
}

export interface SalesOrder {
  id: string;
  orderNumber: string;
  orderDate: string;
  customerId: string;
  status: string;
  totalAmount: string | number;
  [key: string]: unknown;
}
export interface SalesOrderDetail extends SalesOrder { lines: DocumentLine[]; }
export interface SalesOrderCreateInput {
  orderDate: string;
  customerId: string;
  lines: DocumentLineInput[];
}

export interface PurchaseOrder {
  id: string;
  orderNumber: string;
  orderDate: string;
  supplierId: string;
  status: string;
  totalAmount: string | number;
  [key: string]: unknown;
}
export interface PurchaseOrderDetail extends PurchaseOrder { lines: DocumentLine[]; }
export interface PurchaseOrderCreateInput {
  orderDate: string;
  supplierId: string;
  lines: DocumentLineInput[];
}

export interface SalesCredit {
  id: string;
  creditNumber: string;
  creditDate: string;
  customerId: string;
  status: string;
  totalAmount: string | number;
  journalId?: string | null;
  [key: string]: unknown;
}
export interface SalesCreditDetail extends SalesCredit { lines: DocumentLine[]; }
export interface SalesCreditCreateInput {
  creditDate: string;
  customerId: string;
  lines: DocumentLineInput[];
}

export interface SupplierCredit {
  id: string;
  creditNumber: string;
  creditDate: string;
  supplierId: string;
  status: string;
  totalAmount: string | number;
  journalId?: string | null;
  [key: string]: unknown;
}
export interface SupplierCreditDetail extends SupplierCredit { lines: DocumentLine[]; }
export interface SupplierCreditCreateInput {
  creditDate: string;
  supplierId: string;
  lines: DocumentLineInput[];
}

interface PostingResponse<T> {
  result: T;
  posted: boolean;
  postingWarning: string | null;
}

export const quotationsApi = {
  list: () => apiFetch<{ result: Quotation[] }>(path("/quotations")),
  get: (id: string) => apiFetch<{ result: QuotationDetail }>(path(`/quotations/${id}`)),
  create: (body: QuotationCreateInput) =>
    apiFetch<{ result: QuotationDetail }>(path("/quotations"), { method: "POST", body }),
  setStatus: (id: string, status: string) =>
    apiFetch<{ result: QuotationDetail }>(path(`/quotations/${id}/status`), {
      method: "PUT",
      body: { status },
    }),
  convertToOrder: (id: string) =>
    apiFetch<{ result: SalesOrderDetail; quotationId: string }>(
      path(`/quotations/${id}/convert-to-order`),
      { method: "POST" },
    ),
};

export const salesOrdersApi = {
  list: () => apiFetch<{ result: SalesOrder[] }>(path("/sales-orders")),
  get: (id: string) => apiFetch<{ result: SalesOrderDetail }>(path(`/sales-orders/${id}`)),
  create: (body: SalesOrderCreateInput) =>
    apiFetch<{ result: SalesOrderDetail }>(path("/sales-orders"), { method: "POST", body }),
  setStatus: (id: string, status: string) =>
    apiFetch<{ result: SalesOrderDetail }>(path(`/sales-orders/${id}/status`), {
      method: "PUT",
      body: { status },
    }),
  convertToInvoice: (id: string) =>
    apiFetch<{ result: SalesInvoiceDetail; orderId: string; posted: boolean }>(
      path(`/sales-orders/${id}/convert-to-invoice`),
      { method: "POST" },
    ),
};

export const purchaseOrdersApi = {
  list: () => apiFetch<{ result: PurchaseOrder[] }>(path("/purchase-orders")),
  get: (id: string) =>
    apiFetch<{ result: PurchaseOrderDetail }>(path(`/purchase-orders/${id}`)),
  create: (body: PurchaseOrderCreateInput) =>
    apiFetch<{ result: PurchaseOrderDetail }>(path("/purchase-orders"), {
      method: "POST",
      body,
    }),
  setStatus: (id: string, status: string) =>
    apiFetch<{ result: PurchaseOrderDetail }>(path(`/purchase-orders/${id}/status`), {
      method: "PUT",
      body: { status },
    }),
  convertToBill: (id: string) =>
    apiFetch<{ result: SupplierBillDetail; orderId: string; posted: boolean }>(
      path(`/purchase-orders/${id}/convert-to-bill`),
      { method: "POST" },
    ),
};

export const salesCreditsApi = {
  list: () => apiFetch<{ result: SalesCredit[] }>(path("/sales-credits")),
  get: (id: string) => apiFetch<{ result: SalesCreditDetail }>(path(`/sales-credits/${id}`)),
  create: (body: SalesCreditCreateInput) =>
    apiFetch<PostingResponse<SalesCreditDetail>>(path("/sales-credits"), {
      method: "POST",
      body,
    }),
};

export const supplierCreditsApi = {
  list: () => apiFetch<{ result: SupplierCredit[] }>(path("/supplier-credits")),
  get: (id: string) =>
    apiFetch<{ result: SupplierCreditDetail }>(path(`/supplier-credits/${id}`)),
  create: (body: SupplierCreditCreateInput) =>
    apiFetch<PostingResponse<SupplierCreditDetail>>(path("/supplier-credits"), {
      method: "POST",
      body,
    }),
};

// ---------------- Sprint 8 — Inventory writes ----------------

export interface StockAdjustmentLineInput {
  productCode: string;
  locationCode?: string | null;
  quantityDelta: string;
  unitCost?: string;
}
export interface StockAdjustmentCreateInput {
  adjustmentDate: string;
  reason?: string;
  notes?: string | null;
  lines: StockAdjustmentLineInput[];
}
export interface StockAdjustment {
  id: string;
  voucherNumber: string;
  adjustmentDate: string;
  reason: string;
  notes?: string | null;
  status: string;
  lines?: {
    id: string;
    productCode: string;
    locationCode?: string | null;
    quantityDelta: string;
    unitCost: string;
  }[];
  [key: string]: unknown;
}

export interface StockTransferLineInput {
  productCode: string;
  quantity: string;
  unitCost?: string;
}
export interface StockTransferCreateInput {
  transferDate: string;
  fromLocationCode: string;
  toLocationCode: string;
  notes?: string | null;
  lines: StockTransferLineInput[];
}
export interface StockTransfer {
  id: string;
  voucherNumber: string;
  transferDate: string;
  fromLocationCode: string;
  toLocationCode: string;
  notes?: string | null;
  status: string;
  lines?: { id: string; productCode: string; quantity: string; unitCost: string }[];
  [key: string]: unknown;
}

export interface ProductBatch {
  id: string;
  productCode: string;
  batchNumber: string;
  expiryDate?: string | null;
  quantityOnHand: string;
  notes?: string | null;
  expiryStatus?: "expired" | "expiring_soon" | "ok" | "no_expiry";
  daysToExpiry?: number | null;
  [key: string]: unknown;
}
export interface ProductBatchCreateInput {
  productCode: string;
  batchNumber: string;
  expiryDate?: string | null;
  quantityOnHand?: string;
  notes?: string | null;
}

export const inventoryWritesApi = {
  listStockAdjustments: () =>
    apiFetch<{ result: StockAdjustment[] }>(path("/stock-adjustments")),
  getStockAdjustment: (id: string) =>
    apiFetch<{ result: StockAdjustment }>(path(`/stock-adjustments/${id}`)),
  createStockAdjustment: (body: StockAdjustmentCreateInput) =>
    apiFetch<{ result: StockAdjustment }>(path("/stock-adjustments"), {
      method: "POST",
      body,
    }),

  listStockTransfers: () =>
    apiFetch<{ result: StockTransfer[] }>(path("/stock-transfers")),
  getStockTransfer: (id: string) =>
    apiFetch<{ result: StockTransfer }>(path(`/stock-transfers/${id}`)),
  createStockTransfer: (body: StockTransferCreateInput) =>
    apiFetch<{ result: StockTransfer }>(path("/stock-transfers"), {
      method: "POST",
      body,
    }),

  listBatches: (params?: {
    productCode?: string;
    filter?: "expired" | "expiring" | "all";
    expiringWithinDays?: number;
  }) =>
    apiFetch<{ result: ProductBatch[] }>(path("/product-batches"), {
      query: {
        productCode: params?.productCode,
        filter: params?.filter,
        expiringWithinDays: params?.expiringWithinDays,
      },
    }),
  createBatch: (body: ProductBatchCreateInput) =>
    apiFetch<{ result: ProductBatch }>(path("/product-batches"), {
      method: "POST",
      body,
    }),
};

// ---------------- Sprint 12 — Delivery / GRN ----------------

export interface DeliveryLineInput {
  productCode?: string | null;
  quantity: string;
  notes?: string | null;
}
export type DeliverySource = "GDNSI" | "GDNSO" | "manual";
export interface DeliveryNoteCreateInput {
  deliveryDate: string;
  customerId: string;
  sourceKind: DeliverySource;
  sourceId?: string | null;
  notes?: string | null;
  lines: DeliveryLineInput[];
}
export interface DeliveryNote {
  id: string;
  voucherNumber: string;
  deliveryDate: string;
  customerId: string;
  sourceKind: DeliverySource;
  sourceId?: string | null;
  status: string;
  lines?: {
    id: string;
    productCode?: string | null;
    quantity: string;
    notes?: string | null;
  }[];
  [key: string]: unknown;
}

export type GrnSource = "GRNPO" | "GRNVI" | "manual";
export interface GoodsReceiptNoteCreateInput {
  receiptDate: string;
  supplierId: string;
  sourceKind: GrnSource;
  sourceId?: string | null;
  notes?: string | null;
  lines: DeliveryLineInput[];
}
export interface GoodsReceiptNote {
  id: string;
  voucherNumber: string;
  receiptDate: string;
  supplierId: string;
  sourceKind: GrnSource;
  sourceId?: string | null;
  status: string;
  lines?: {
    id: string;
    productCode?: string | null;
    quantity: string;
    notes?: string | null;
  }[];
  [key: string]: unknown;
}

export const deliveryApi = {
  listDeliveryNotes: () =>
    apiFetch<{ result: DeliveryNote[] }>(path("/delivery-notes")),
  getDeliveryNote: (id: string) =>
    apiFetch<{ result: DeliveryNote }>(path(`/delivery-notes/${id}`)),
  createDeliveryNote: (body: DeliveryNoteCreateInput) =>
    apiFetch<{ result: DeliveryNote }>(path("/delivery-notes"), {
      method: "POST",
      body,
    }),

  listGrns: () =>
    apiFetch<{ result: GoodsReceiptNote[] }>(path("/goods-receipt-notes")),
  getGrn: (id: string) =>
    apiFetch<{ result: GoodsReceiptNote }>(path(`/goods-receipt-notes/${id}`)),
  createGrn: (body: GoodsReceiptNoteCreateInput) =>
    apiFetch<{ result: GoodsReceiptNote }>(path("/goods-receipt-notes"), {
      method: "POST",
      body,
    }),
};

// ---------------- Sprint 14 — Post-Dated Cheques ----------------

export type PdcStatus =
  | "pending"
  | "presented"
  | "cleared"
  | "bounced"
  | "cancelled";

export interface PdcReceived {
  id: string;
  voucherNumber: string;
  chequeNumber: string;
  bankName: string;
  customerId: string;
  receivedDate: string;
  chequeDate: string;
  amount: string;
  status: PdcStatus;
  linkedReceiptId?: string | null;
  notes?: string | null;
  [key: string]: unknown;
}
export interface PdcReceivedCreateInput {
  chequeNumber: string;
  bankName: string;
  customerId: string;
  receivedDate: string;
  chequeDate: string;
  amount: string;
  notes?: string | null;
}

export interface PdcIssued {
  id: string;
  voucherNumber: string;
  chequeNumber: string;
  bankAccountId: string;
  supplierId: string;
  issuedDate: string;
  chequeDate: string;
  amount: string;
  status: PdcStatus;
  linkedPaymentId?: string | null;
  notes?: string | null;
  [key: string]: unknown;
}
export interface PdcIssuedCreateInput {
  chequeNumber: string;
  bankAccountId: string;
  supplierId: string;
  issuedDate: string;
  chequeDate: string;
  amount: string;
  notes?: string | null;
}

export const pdcApi = {
  listReceived: (status?: PdcStatus) =>
    apiFetch<{ result: PdcReceived[] }>(path("/pdc-received"), {
      query: { status },
    }),
  getReceived: (id: string) =>
    apiFetch<{ result: PdcReceived }>(path(`/pdc-received/${id}`)),
  createReceived: (body: PdcReceivedCreateInput) =>
    apiFetch<{ result: PdcReceived }>(path("/pdc-received"), {
      method: "POST",
      body,
    }),
  setReceivedStatus: (id: string, status: PdcStatus) =>
    apiFetch<{ result: PdcReceived }>(path(`/pdc-received/${id}/status`), {
      method: "PUT",
      body: { status },
    }),
  presentReceived: (id: string) =>
    apiFetch<{ result: PdcReceived }>(path(`/pdc-received/${id}/present`), {
      method: "POST",
    }),
  clearReceived: (
    id: string,
    body: { bankAccountId: string; clearDate: string; autoFifo?: boolean }
  ) =>
    apiFetch<{ result: Record<string, unknown> }>(path(`/pdc-received/${id}/clear`), {
      method: "POST",
      body,
    }),
  bounceReceived: (id: string) =>
    apiFetch<{ result: PdcReceived }>(path(`/pdc-received/${id}/bounce`), {
      method: "POST",
    }),

  listIssued: (status?: PdcStatus) =>
    apiFetch<{ result: PdcIssued[] }>(path("/pdc-issued"), {
      query: { status },
    }),
  getIssued: (id: string) =>
    apiFetch<{ result: PdcIssued }>(path(`/pdc-issued/${id}`)),
  createIssued: (body: PdcIssuedCreateInput) =>
    apiFetch<{ result: PdcIssued }>(path("/pdc-issued"), {
      method: "POST",
      body,
    }),
  setIssuedStatus: (id: string, status: PdcStatus) =>
    apiFetch<{ result: PdcIssued }>(path(`/pdc-issued/${id}/status`), {
      method: "PUT",
      body: { status },
    }),
  presentIssued: (id: string) =>
    apiFetch<{ result: PdcIssued }>(path(`/pdc-issued/${id}/present`), {
      method: "POST",
    }),
  clearIssued: (id: string, body: { clearDate: string; autoFifo?: boolean }) =>
    apiFetch<{ result: Record<string, unknown> }>(path(`/pdc-issued/${id}/clear`), {
      method: "POST",
      body,
    }),
  bounceIssued: (id: string) =>
    apiFetch<{ result: PdcIssued }>(path(`/pdc-issued/${id}/bounce`), {
      method: "POST",
    }),
};

export const importJobsApi = {
  list: () => apiFetch<{ result: Record<string, unknown>[] }>(path("/import-jobs")),
  create: (body: { jobType: string; fileName?: string; rows?: Record<string, unknown>[] }) =>
    apiFetch<{ result: Record<string, unknown> }>(path("/import-jobs"), {
      method: "POST",
      body,
    }),
};

export interface SupplierPayment {
  id: string;
  voucherNumber?: string | null;
  paymentDate: string;
  supplierId: string;
  bankAccountId: string;
  totalAmount: string | number;
  status?: string;
  journalId?: string | null;
  [key: string]: unknown;
}

export interface SupplierPaymentAllocationInput {
  billId: string;
  amount: string;
}

export interface SupplierPaymentCreateInput {
  paymentDate: string;
  supplierId: string;
  bankAccountId: string;
  totalAmount: string;
  /** Apply FIFO against the supplier's open bills on the server. */
  autoFifo?: boolean;
  allocations?: SupplierPaymentAllocationInput[];
  whtCode?: string | null;
  whtAmount?: string | null;
  paymentMethod?: string | null;
  smartFilters?: Record<string, string>;
}

export interface PaymentCreateResponse {
  result: SupplierPayment;
  posted: boolean;
  postingWarning: string | null;
  allocations: { id: string; supplierBillId: string; amount: string }[];
  totalAllocated: string;
  unallocatedBalance: string;
}

export const purchasesApi = {
  listSupplierBills: () =>
    apiFetch<{ result: SupplierBill[] }>(path("/supplier-bills")),
  getSupplierBill: (id: string) =>
    apiFetch<{ result: SupplierBillDetail }>(path(`/supplier-bills/${id}`)),
  createSupplierBill: (body: SupplierBillCreateInput) =>
    apiFetch<{ result: SupplierBillDetail; posted?: boolean; postingWarning?: string | null }>(
      path("/supplier-bills"),
      {
        method: "POST",
        body,
      }
    ),
  createBatchBills: (body: BatchSupplierBillCreateInput) =>
    apiFetch<{ result: { created: BatchDocumentResult[]; count: number } }>(
      path("/supplier-bills/batch"),
      { method: "POST", body },
    ),
  updateSupplierBill: (id: string, body: SupplierBillCreateInput) =>
    apiFetch<{ result: SupplierBillDetail; taxTotal?: string }>(
      path(`/supplier-bills/${id}`),
      { method: "PATCH", body }
    ),
  approveSupplierBill: (id: string) =>
    apiFetch<{ result: SupplierBillDetail; posted: boolean }>(
      path(`/supplier-bills/${id}/approve`),
      { method: "POST" }
    ),
  voidSupplierBill: (billId: string, body?: { reversalDate?: string }) =>
    apiFetch<{ result: Record<string, unknown> }>(path(`/supplier-bills/${billId}/void`), {
      method: "POST",
      body: body ?? {},
    }),
  listSupplierPayments: () =>
    apiFetch<{ result: SupplierPayment[] }>(path("/supplier-payments")),
  getSupplierPayment: (id: string) =>
    apiFetch<{
      result: SupplierPayment;
      allocations: { id: string; supplierBillId: string; amount: string }[];
      balance?: SettlementBalance;
      advanceReturns?: AdvanceReturnRow[];
    }>(path(`/supplier-payments/${id}`)),
  returnAdvance: (
    id: string,
    body: { returnDate: string; amount: string; bankAccountId?: string },
  ) =>
    apiFetch<{ result: AdvanceReturnRow; bankReceipt: Record<string, unknown>; posted: boolean }>(
      path(`/supplier-payments/${id}/return-advance`),
      { method: "POST", body },
    ),
  allocateSupplierPayment: (
    id: string,
    body: {
      autoFifo?: boolean;
      allocations?: { billId: string; amount: string }[];
    },
  ) =>
    apiFetch<{
      allocations: { id: string; supplierBillId: string; amount: string }[];
      totalAllocated: string;
      unallocatedBalance: string;
    }>(path(`/supplier-payments/${id}/allocate`), { method: "POST", body }),
  createSupplierPayment: (body: SupplierPaymentCreateInput) =>
    apiFetch<PaymentCreateResponse>(path("/supplier-payments"), {
      method: "POST",
      body,
    }),
  postSupplierPayment: (id: string) =>
    apiFetch<{ result: SupplierPayment; posted: boolean }>(
      path(`/supplier-payments/${id}/post`),
      { method: "POST" },
    ),
};

export interface AuditLogEntry {
  id: string;
  timestamp: string;
  transactionType?: string | null;
  transactionId?: string | null;
  status?: string | null;
  details?: string | null;
  userId?: string | null;
  userName?: string | null;
  [key: string]: unknown;
}

export interface AuditLogFilters {
  userId?: string;
  dateFrom?: string;
  dateTo?: string;
  transactionType?: string;
  transactionId?: string;
  rbacOnly?: boolean;
  /** Substring match on transaction type (e.g. BANK) — P43. */
  typeContains?: string;
}

function auditLogExportUrl(filters: AuditLogFilters = {}): string {
  const base = resolveApiUrl(path("/audit-log/export"));
  const params = new URLSearchParams();
  if (filters.userId) params.set("user_id", filters.userId);
  if (filters.dateFrom) params.set("date_from", filters.dateFrom);
  if (filters.dateTo) params.set("date_to", filters.dateTo);
  if (filters.transactionType) params.set("transaction_type", filters.transactionType);
  if (filters.transactionId) params.set("transaction_id", filters.transactionId);
  if (filters.typeContains) params.set("typeContains", filters.typeContains);
  if (filters.rbacOnly) params.set("rbac_only", "true");
  const qs = params.toString();
  return qs ? `${base}?${qs}` : base;
}

export type AuditTransactionTypeGroup = {
  group: string;
  types: { id: string; label: string }[];
};

export const auditApi = {
  listRbacTypes: () =>
    apiFetch<{ result: string[] }>(path("/audit-log/rbac-types")),
  listTransactionTypes: () =>
    apiFetch<{ result: AuditTransactionTypeGroup[] }>(path("/audit-log/transaction-types")),
  list: (filters: AuditLogFilters = {}) =>
    apiFetch<{ result: AuditLogEntry[] }>(path("/audit-log"), {
      query: {
        user_id: filters.userId,
        date_from: filters.dateFrom,
        date_to: filters.dateTo,
        transaction_type: filters.transactionType,
        transaction_id: filters.transactionId,
        typeContains: filters.typeContains,
        rbac_only: filters.rbacOnly ? "true" : undefined,
      },
    }),
  exportCsvUrl: (filters: AuditLogFilters = {}) => auditLogExportUrl(filters),
  downloadCsv: async (filters: AuditLogFilters = {}) => {
    const tokens = getTokens();
    const res = await fetch(auditLogExportUrl(filters), {
      headers: tokens?.accessToken
        ? { Authorization: `Bearer ${tokens.accessToken}` }
        : {},
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(text || `Export failed (${res.status})`);
    }
    return res.blob();
  },
};

export interface RbacUser {
  id: string;
  firstName?: string | null;
  lastName?: string | null;
  email?: string | null;
  phone?: string | null;
  type?: string | null;
  role?: string | null;
  status?: string | null;
  [key: string]: unknown;
}

export interface ModuleAccessRow {
  moduleCode: string;
  enabled: boolean;
  sidebarVisible?: boolean;
  routesEnabled?: boolean;
  apiEnabled?: boolean;
  reportsEnabled?: boolean;
  widgetsEnabled?: boolean;
  requiredPermissions?: string[];
  userHasPermission?: boolean;
  canAccess: boolean;
}

export interface MyPermissionsResult {
  permissions: string[];
  roleIds?: string[];
  roles?: { roleId: string; roleName?: string | null; roleCode?: string | null; isPrimary?: boolean }[];
  modules?: ModuleAccessRow[];
}

export interface RbacRole {
  id: string;
  name: string;
  permissions?: string[];
  description?: string | null;
  code?: string | null;
  parentRoleId?: string | null;
  isSystem?: boolean;
  isTemplate?: boolean;
  sortOrder?: number;
  [key: string]: unknown;
}

export interface PermissionTreeSubmodule {
  name: string;
  permissions: { code: string; label: string }[];
}

export interface PermissionTreeGroup {
  group: string;
  permissions: { code: string; label: string }[];
  submodules?: PermissionTreeSubmodule[];
}

export interface InviteUserInput {
  email: string;
  firstName: string;
  lastName: string;
  roleId: string;
}

export interface InviteUserResult extends RbacUser {
  userCreated?: boolean;
  inviteEmailSent?: boolean;
}

export interface PaginatedUsers {
  items: RbacUser[];
  page: number;
  pageSize: number;
  total: number;
}

export const rbacApi = {
  lookupUserByEmail: (email: string) =>
    apiFetch<{
      result: {
        userId: string;
        email: string;
        firstName?: string | null;
        lastName?: string | null;
        isActive?: boolean;
      };
    }>(path("/users/lookup"), { query: { email } }),
  listUsers: (params?: {
    page?: number;
    pageSize?: number;
    q?: string;
    isActive?: boolean;
    roleId?: string;
    userId?: string;
  }) =>
    apiFetch<{ result: PaginatedUsers }>(path("/users"), {
      query: {
        page: params?.page,
        page_size: params?.pageSize,
        q: params?.q,
        is_active: params?.isActive,
        role_id: params?.roleId,
        user_id: params?.userId,
      },
    }),
  listRoles: () => apiFetch<{ result: RbacRole[] }>(path("/roles")),
  getPermissionsCatalog: () =>
    apiFetch<{ result: PermissionTreeGroup[] }>(path("/permissions/catalog")),
  getKnownPermissionCodes: () =>
    apiFetch<{ result: string[] }>(path("/permissions/known-codes")),
  getMyPermissions: () =>
    apiFetch<{ result: MyPermissionsResult }>(path("/permissions/mine")),
  getPermissionsMatrix: () =>
    apiFetch<{ result: import("@/lib/rbac/permission-matrix").PermissionMatrixSchema & {
      fieldSecurityKeys: { key: string; label: string }[];
      fieldAccessLevels: string[];
      dataScopeTypes: string[];
    } }>(path("/permissions/matrix")),
  listRoleTemplates: () =>
    apiFetch<{ result: { code: string; name: string; description?: string; permissions: string[] }[] }>(
      path("/role-templates"),
    ),
  createRoleFromTemplate: (code: string, body?: { name?: string }) =>
    apiFetch<{ result: RbacRole }>(path(`/roles/from-template/${code}`), {
      method: "POST",
      body: body ?? {},
    }),
  seedMissingRoleTemplates: () =>
    apiFetch<{ result: { id: string; name: string; code: string }[] }>(
      path("/roles/seed-missing-templates"),
      { method: "POST", body: {} },
    ),
  assignUserRoles: (userId: string, body: { roleIds: string[]; primaryRoleId?: string }) =>
    apiFetch<{ result: RbacUser }>(path(`/users/${userId}/roles`), {
      method: "PUT",
      body: { roleIds: body.roleIds, primaryRoleId: body.primaryRoleId },
    }),
  getRole: (roleId: string) =>
    apiFetch<{ result: RbacRole }>(path(`/roles/${roleId}`)),
  createRole: (
    body: {
      name: string;
      permissions: string[];
      description?: string | null;
      parentRoleId?: string | null;
      code?: string | null;
    },
    options?: { strict?: boolean }
  ) =>
    apiFetch<{
      result: RbacRole;
      unknownPermissions?: string[];
      permissionWarnings?: string[];
    }>(
      path("/roles") + (options?.strict ? "?strict=true" : ""),
      { method: "POST", body }
    ),
  updateRole: (
    roleId: string,
    body: {
      name?: string;
      permissions?: string[];
      description?: string | null;
      parentRoleId?: string | null;
    },
    options?: { strict?: boolean }
  ) =>
    apiFetch<{
      result: RbacRole;
      unknownPermissions?: string[];
      permissionWarnings?: string[];
    }>(
      path(`/roles/${roleId}`) + (options?.strict ? "?strict=true" : ""),
      { method: "PUT", body }
    ),
  deleteRole: (roleId: string) =>
    apiFetch<{ result: { deleted: boolean; roleId: string } }>(
      path(`/roles/${roleId}`),
      { method: "DELETE" }
    ),
  assignUserRole: (userId: string, roleId: string) =>
    apiFetch<{ result: RbacUser }>(path(`/users/${userId}/role`), {
      method: "PATCH",
      body: { roleId },
    }),
  inviteUser: (body: InviteUserInput) =>
    apiFetch<{ result: InviteUserResult }>(path("/users/invite"), {
      method: "POST",
      body,
    }),
  cloneRole: (roleId: string, body?: { name?: string }, options?: { strict?: boolean }) =>
    apiFetch<{
      result: RbacRole;
      unknownPermissions?: string[];
      permissionWarnings?: string[];
    }>(
      path(`/roles/${roleId}/clone`) + (options?.strict ? "?strict=true" : ""),
      { method: "POST", body: body ?? {} }
    ),
  exportRoles: (params?: { stripIds?: boolean }) =>
    apiFetch<{
      result: { exportedAt: string; roles: RbacRole[]; namesOnly?: boolean };
    }>(path("/roles/export"), {
      query: { stripIds: params?.stripIds ? "true" : undefined },
    }),
  cloneRolesBatch: (
    body: { roleIds: string[]; nameSuffix?: string },
    options?: { strict?: boolean }
  ) =>
    apiFetch<{ result: RbacRole[] }>(
      path("/roles/clone-batch") + (options?.strict ? "?strict=true" : ""),
      { method: "POST", body }
    ),
  resendUserInvite: (userId: string) =>
    apiFetch<{
      result: { emailType: "setup" | "welcome"; emailSent: boolean };
    }>(path(`/users/${userId}/resend-invite`), { method: "POST" }),
  importRoles: (
    body: { roles: { name: string; permissions: string[] }[]; skipExisting?: boolean },
    options?: { strict?: boolean }
  ) =>
    apiFetch<{
      result: {
        created: RbacRole[];
        skipped: { name: string; reason: string; id?: string }[];
      };
    }>(
      path("/roles/import") + (options?.strict ? "?strict=true" : ""),
      { method: "POST", body }
    ),
  getInviteEmailTemplate: () =>
    apiFetch<{
      result: {
        invite: { subject: string; introText: string; introHtml: string };
        welcome: { subject: string; introText: string; introHtml: string };
        placeholders: { invite: string[]; welcome: string[] };
        defaults: {
          invite: { subject: string; introText: string; introHtml: string };
          welcome: { subject: string; introText: string; introHtml: string };
        };
      };
    }>(path("/settings/invite-email-template")),
  updateInviteEmailTemplate: (body: {
    subject?: string;
    introText?: string;
    introHtml?: string;
  }) =>
    apiFetch<{ result: { invite: { subject: string; introText: string; introHtml: string } } }>(
      path("/settings/invite-email-template"),
      { method: "PUT", body }
    ),
  updateWelcomeEmailTemplate: (body: {
    subject?: string;
    introText?: string;
    introHtml?: string;
  }) =>
    apiFetch<{ result: { welcome: { subject: string; introText: string; introHtml: string } } }>(
      path("/settings/welcome-email-template"),
      { method: "PUT", body }
    ),
  previewInviteEmailTemplate: (body: {
    kind: "invite" | "welcome";
    subject?: string;
    introText?: string;
    introHtml?: string;
  }) =>
    apiFetch<{
      result: {
        preview: { subject: string; introText: string; introHtml: string };
        sampleValues: Record<string, string>;
      };
    }>(path("/settings/invite-email-template/preview"), { method: "POST", body }),
  previewImportRoles: (
    body: { roles: { name: string; permissions: string[] }[]; skipExisting?: boolean },
    options?: { strict?: boolean }
  ) =>
    apiFetch<{
      result: {
        wouldCreate: { name: string; permissions: string[] }[];
        wouldSkip: { name: string; reason: string; id?: string }[];
        permissionWarnings: { name: string; unknownPermissions: string[] }[];
      };
    }>(
      path("/roles/import/preview") + (options?.strict ? "?strict=true" : ""),
      { method: "POST", body }
    ),
  bulkAssignRole: (userIds: string[], roleId: string) =>
    apiFetch<{
      result: {
        succeeded: string[];
        failed: { userId: string; error: string }[];
        roleId: string;
      };
    }>(path("/users/bulk-assign-role"), {
      method: "POST",
      body: { userIds, roleId },
    }),
  bulkRevokeMembership: (userIds: string[]) =>
    apiFetch<{
      result: {
        succeeded: string[];
        failed: { userId: string; error: string }[];
      };
    }>(path("/users/bulk-revoke"), { method: "POST", body: { userIds } }),
  revokeUserMembership: (userId: string) =>
    apiFetch<{ result: { userId: string; email: string; revoked: string } }>(
      path(`/users/${userId}/membership`),
      { method: "DELETE" }
    ),
  deactivateUser: (userId: string) =>
    apiFetch<{ result: { userId: string; email: string; isActive: boolean } }>(
      path(`/users/${userId}/deactivate`),
      { method: "POST" }
    ),
  reactivateUser: (userId: string) =>
    apiFetch<{ result: { userId: string; email: string; isActive: boolean } }>(
      path(`/users/${userId}/reactivate`),
      { method: "POST" }
    ),
  updateIpAllowlist: (userId: string, ipAllowlist: string | null) =>
    apiFetch<{ result: RbacUser }>(path(`/users/${userId}/ip-allowlist`), {
      method: "PATCH",
      body: { ipAllowlist },
    }),
  enqueueRoleImportJob: async (
    file: File,
    options?: { skipExisting?: boolean }
  ) => {
    const tokens = getTokens();
    const params = new URLSearchParams();
    if (options?.skipExisting === false) params.set("skip_existing", "false");
    const qs = params.toString();
    const url = `${resolveApiUrl(path("/roles/import/jobs"))}${qs ? `?${qs}` : ""}`;
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(url, {
      method: "POST",
      headers: tokens?.accessToken
        ? { Authorization: `Bearer ${tokens.accessToken}` }
        : {},
      body: form,
    });
    const text = await res.text();
    const parsed = text ? JSON.parse(text) : undefined;
    if (!res.ok) {
      throw new Error(
        typeof parsed?.detail === "string" ? parsed.detail : `Enqueue failed (${res.status})`
      );
    }
    return parsed as { result: { id: string; status: string; jobType: string; resultSummary?: string } };
  },
  getRoleImportJob: (jobId: string) =>
    apiFetch<{
      result: {
        id: string;
        status: string;
        jobType: string;
        fileName?: string;
        resultSummary?: string;
        errorCount?: number;
      };
    }>(path(`/roles/import/jobs/${jobId}`)),
  reinviteUser: (userId: string, roleId: string) =>
    apiFetch<{ result: InviteUserResult }>(path(`/users/${userId}/reinvite`), {
      method: "POST",
      body: { roleId },
    }),
  reinviteByEmail: (body: { email: string; roleId: string }) =>
    apiFetch<{ result: InviteUserResult }>(path("/users/reinvite"), {
      method: "POST",
      body,
    }),
  uploadRoleImport: async (
    file: File,
    options?: { skipExisting?: boolean; dryRun?: boolean; strict?: boolean; forceSync?: boolean }
  ) => {
    const tokens = getTokens();
    const params = new URLSearchParams();
    if (options?.skipExisting === false) params.set("skip_existing", "false");
    if (options?.dryRun) params.set("dry_run", "true");
    if (options?.strict) params.set("strict", "true");
    if (options?.forceSync) params.set("force_sync", "true");
    const qs = params.toString();
    const url = `${resolveApiUrl(path("/roles/import/upload"))}${qs ? `?${qs}` : ""}`;
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(url, {
      method: "POST",
      headers: tokens?.accessToken
        ? { Authorization: `Bearer ${tokens.accessToken}` }
        : {},
      body: form,
    });
    const text = await res.text();
    const parsed = text ? JSON.parse(text) : undefined;
    if (!res.ok) {
      throw new Error(
        typeof parsed?.detail === "string" ? parsed.detail : `Upload failed (${res.status})`
      );
    }
    return { status: res.status, data: parsed as { result: Record<string, unknown> } };
  },
};

export interface JournalLineInput {
  nominalCode: string;
  debit: string;
  credit: string;
  projectCode?: string | null;
}

export interface JournalCreateInput {
  journalDate: string;
  refNo?: string | null;
  lines: JournalLineInput[];
  status?: "draft" | "posted";
}

export interface JournalUpdateInput {
  journalDate?: string;
  refNo?: string | null;
  lines?: JournalLineInput[];
}

export const journalsApi = {
  list: () => apiFetch<{ result: Journal[] }>(path("/journals")),
  get: (id: string) => apiFetch<{ result: Journal }>(path(`/journals/${id}`)),
  create: (body: JournalCreateInput) =>
    apiFetch<{ result: Journal }>(path("/journals"), { method: "POST", body }),
  update: (id: string, body: JournalUpdateInput) =>
    apiFetch<{ result: Journal }>(path(`/journals/${id}`), { method: "PATCH", body }),
  post: (id: string) =>
    apiFetch<{ result: Journal }>(path(`/journals/${id}/post`), { method: "POST" }),
  copy: (id: string) =>
    apiFetch<{ result: Journal }>(path(`/journals/${id}/copy`), { method: "POST" }),
  reverse: (id: string, body: { reversalDate: string; refNo?: string | null }) =>
    apiFetch<{ result: Journal }>(path(`/journals/${id}/reverse`), {
      method: "POST",
      body,
    }),
  bulkDelete: (journalIds: string[]) =>
    apiFetch<{ result: { deleted: number; skipped: number } }>(
      path("/journals/bulk-delete"),
      { method: "POST", body: { journalIds } },
    ),
};

export interface TrialBalanceRow {
  nominalCode: string;
  name?: string | null;
  debit: string;
  credit: string;
  balance: string;
  [key: string]: unknown;
}

export interface GeneralLedgerLine {
  journalId: string;
  journalNumber?: string | null;
  journalDate?: string | null;
  refNo?: string | null;
  projectCode?: string | null;
  debit: string;
  credit: string;
  balance: string;
  [key: string]: unknown;
}

export interface GeneralLedgerResult {
  nominalCode: string;
  openingBalance: string;
  periodDebit: string;
  periodCredit: string;
  closingBalance: string;
  lines: GeneralLedgerLine[];
}

export interface DashboardSummary {
  counts: {
    customers: number;
    suppliers: number;
    products: number;
    bankAccounts: number;
    journals: number;
    salesInvoices: number;
    supplierBills: number;
    bankPayments: number;
  };
  totals: {
    salesAmount: string;
    purchasesAmount: string;
    bankPaymentsAmount: string;
  };
}

export interface BankBalanceRow {
  bankAccountId: string;
  name: string;
  nominalCode: string;
  currency?: string;
  balance: string;
}

export interface BankCashFlowMonth {
  month: string;
  inflow: string;
  outflow: string;
  net: string;
}

export interface DashboardOverview {
  financialYearFrom: string;
  financialYearTo: string;
  bankBalances: BankBalanceRow[];
  bankCashFlow: BankCashFlowMonth[];
  monthlyBankBalance: { month: string; balance: string }[];
  profitAndLoss: {
    totals: { income: string; expense: string; netProfit: string };
    expenseBreakdown: { label: string; amount: string }[];
  };
  salesByMonth: { month: string; totalSales: string }[];
  inventoryStock: {
    inStock: number;
    lowStock: number;
    outOfStock: number;
    oversold: number;
  };
  arAging: AgingResult;
  apAging: AgingResult;
  arTopParties: AgingRow[];
  apTopParties: AgingRow[];
}

export const dashboardApi = {
  summary: () =>
    apiFetch<{ result: DashboardSummary }>(path("/dashboard/summary")),
  overview: () =>
    apiFetch<{ result: DashboardOverview }>(path("/dashboard/overview")),
  commandCenter: (params?: { period?: string; salesGranularity?: string }) =>
    apiFetch<{ result: import("@/components/dashboard/command-center/types/command-center").CommandCenterPayload }>(
      path("/dashboard/command-center"),
      {
        query: {
          period: params?.period,
          salesGranularity: params?.salesGranularity,
        },
      },
    ),
  getLayout: () =>
    apiFetch<{ result: import("@/components/dashboard/command-center/types/command-center").DashboardLayoutSettings & { companyId?: string } }>(
      path("/dashboard/layout"),
    ),
  putLayout: (body: import("@/components/dashboard/command-center/types/command-center").DashboardLayoutSettings) =>
    apiFetch<{ result: import("@/components/dashboard/command-center/types/command-center").DashboardLayoutSettings }>(
      path("/dashboard/layout"),
      { method: "PUT", body },
    ),
};

export interface PlRow {
  nominalCode: string;
  name?: string | null;
  categoryName: string;
  amount: string;
  [key: string]: unknown;
}

export interface ProfitAndLossResult {
  income: PlRow[];
  expense: PlRow[];
  totals: { income: string; expense: string; netProfit: string };
}

export interface BalanceSheetRow {
  nominalCode: string;
  name?: string | null;
  categoryName: string;
  amount: string;
  [key: string]: unknown;
}

export interface BalanceSheetResult {
  assets: BalanceSheetRow[];
  liabilities: BalanceSheetRow[];
  equity: BalanceSheetRow[];
  uncategorized: BalanceSheetRow[];
  totals: {
    assets: string;
    liabilities: string;
    equity: string;
    retainedEarnings: string;
    uncategorized: string;
    difference: string;
  };
}

export const reportsApi = {
  trialBalance: (asOfDate?: string) =>
    apiFetch<{ result: TrialBalanceRow[] }>(path("/reports/trial-balance"), {
      query: { asOfDate },
    }),
  generalLedger: (params: { nominalCode: string; dateFrom?: string; dateTo?: string }) =>
    apiFetch<{ result: GeneralLedgerResult }>(path("/reports/general-ledger"), {
      query: {
        nominalCode: params.nominalCode,
        dateFrom: params.dateFrom,
        dateTo: params.dateTo,
      },
    }),
  profitAndLoss: (params: { dateFrom?: string; dateTo?: string } = {}) =>
    apiFetch<{ result: ProfitAndLossResult }>(path("/reports/profit-and-loss"), {
      query: { dateFrom: params.dateFrom, dateTo: params.dateTo },
    }),
  balanceSheet: (asOfDate?: string) =>
    apiFetch<{ result: BalanceSheetResult }>(path("/reports/balance-sheet"), {
      query: { asOfDate },
    }),
  arAging: (asOfDate?: string) =>
    apiFetch<{ result: AgingResult }>(path("/reports/ar-aging"), {
      query: { asOfDate },
    }),
  apAging: (asOfDate?: string) =>
    apiFetch<{ result: AgingResult }>(path("/reports/ap-aging"), {
      query: { asOfDate },
    }),
  bankAccountBalances: (asOfDate?: string) =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/bank-account-balances"), {
      query: { asOfDate },
    }),
  bankCashFlowMonthly: (params?: { dateFrom?: string; dateTo?: string }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/bank-cash-flow-monthly"), {
      query: params,
    }),
  customerStatement: (params: {
    customerId: string;
    dateFrom?: string;
    dateTo?: string;
  }) =>
    apiFetch<{ result: StatementResult }>(path("/reports/customer-statement"), {
      query: params,
    }),
  supplierStatement: (params: {
    supplierId: string;
    dateFrom?: string;
    dateTo?: string;
  }) =>
    apiFetch<{ result: StatementResult }>(path("/reports/supplier-statement"), {
      query: params,
    }),
  saleInvoicesByDate: (params?: { dateFrom?: string; dateTo?: string }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/sale-invoices-by-date"), {
      query: params,
    }),
  saleInvoicesByCustomer: (params?: { dateFrom?: string; dateTo?: string }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(
      path("/reports/sale-invoices-by-customer"),
      { query: params },
    ),
  saleSummaryByDate: (params?: { dateFrom?: string; dateTo?: string }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/sale-summary-by-date"), {
      query: params,
    }),
  customerPerformance: (params?: { dateFrom?: string; dateTo?: string }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/customer-performance"), {
      query: params,
    }),
  customerBalances: (params?: { dateFrom?: string; dateTo?: string }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/customer-balances"), {
      query: params,
    }),
  purchaseBillsByDate: (params?: { dateFrom?: string; dateTo?: string }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/purchase-bills-by-date"), {
      query: params,
    }),
  purchaseBillsBySupplier: (params?: { dateFrom?: string; dateTo?: string }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(
      path("/reports/purchase-bills-by-supplier"),
      { query: params },
    ),
  productSaleDetail: (params?: { dateFrom?: string; dateTo?: string }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/product-sale-detail"), {
      query: params,
    }),
  productPurchaseDetail: (params?: { dateFrom?: string; dateTo?: string }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/product-purchase-detail"), {
      query: params,
    }),
  stockQuantity: () =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/stock-quantity")),
  outOfStock: () =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/out-of-stock")),
  lowStock: () =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/low-stock")),
  stockValuation: () =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/stock-valuation")),
  stockMovement: (params?: { dateFrom?: string; dateTo?: string }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/stock-movement"), {
      query: params,
    }),
  priceList: () =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/price-list")),
  saleSummaryByCustomer: (params?: { dateFrom?: string; dateTo?: string }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(
      path("/reports/sale-summary-by-customer"),
      { query: params },
    ),
  grni: () => apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/grni")),
  bankPaymentsList: (params?: { dateFrom?: string; dateTo?: string }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/bank-payments-list"), {
      query: params,
    }),
  advancedStockQuantity: () =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/advanced-stock-quantity")),
  multiUnitPriceList: () =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/multi-unit-price-list")),
  saleSummaryByField: (params?: {
    dateFrom?: string;
    dateTo?: string;
    groupByField?: string;
  }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/sale-summary-by-field"), {
      query: params,
    }),
  customerFieldActivity: (params?: { dateFrom?: string; dateTo?: string }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/customer-field-activity"), {
      query: params,
    }),
  catalogCoverage: () =>
    apiFetch<{
      result: {
        catalogIds: number;
        unmappedCatalogIds: string[];
        catalogWithHandler: number;
        moduleReportIds?: number;
        unmappedModuleReportIds?: string[];
      };
    }>(path("/reports/catalog-coverage")),
  listDefinitions: (params?: { hub?: "standard" | "analytical"; category?: string }) =>
    apiFetchCached<{
      result: {
        reportId: string;
        name: string;
        category: string;
        hub: string;
        filterSchema?: Record<string, unknown>;
      }[];
    }>(path("/reports/definitions"), {
      query: {
        hub: params?.hub,
        category: params?.category,
      },
    }),
  executeReport: (params: {
    reportId: string;
    dateFrom?: string;
    dateTo?: string;
    customerId?: string;
    supplierId?: string;
    productCode?: string;
    status?: string;
    budgetId?: string;
    asOfDate?: string;
    page?: number;
    pageSize?: number;
  }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/execute"), {
      query: {
        reportId: params.reportId,
        dateFrom: params.dateFrom,
        dateTo: params.dateTo,
        budgetId: params.budgetId,
        asOfDate: params.asOfDate,
        customerId: params.customerId,
        supplierId: params.supplierId,
        productCode: params.productCode,
        status: params.status,
        page: params.page,
        pageSize: params.pageSize,
      },
    }),
  exportReportSync: (body: {
    reportId: string;
    criteria?: Record<string, unknown>;
    format?: "csv" | "json" | "pdf";
  }) =>
    apiFetch<{
      result: { format: string; content?: string | null; downloadUrl?: string | null };
    }>(path("/reports/export"), {
      method: "POST",
      body: {
        reportId: body.reportId,
        criteria: body.criteria ?? {},
        format: body.format ?? "csv",
      },
    }),
  createReportRun: (body: {
    reportId: string;
    criteria?: Record<string, unknown>;
    sync?: boolean;
  }) =>
    apiFetch<{
      runId: string;
      status: string;
      reportId?: string;
      totalRows?: number;
      rows?: Record<string, unknown>[];
    }>(path("/reports/runs"), {
      method: "POST",
      query: body.sync ? { sync: "true" } : undefined,
      body: { reportId: body.reportId, criteria: body.criteria ?? {} },
    }),
  getReportRun: (runId: string) =>
    apiFetch<{
      runId: string;
      status: string;
      reportId: string;
      totalRows: number;
      rows: Record<string, unknown>[];
    }>(path(`/reports/runs/${runId}`)),
  exportReportRun: (runId: string, format: "csv" | "json" | "pdf" | "xlsx" = "csv") =>
    apiFetch<{
      result: { format: string; content?: string | null; downloadUrl?: string | null };
    }>(path(`/reports/runs/${runId}/export`), {
      method: "POST",
      body: { format },
    }),
  assemblyJobCostSummary: () =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/assembly-job-cost-summary")),
  assemblyTemplates: () =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/assembly-templates")),
  assemblyWip: () =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/assembly-wip")),
  assemblyComponentCost: () =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/assembly-component-cost")),
  bankReceiptsList: (params?: { dateFrom?: string; dateTo?: string }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/bank-receipts"), {
      query: params,
    }),
  bankTransfersList: (params?: { dateFrom?: string; dateTo?: string }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/bank-transfers"), {
      query: params,
    }),
  bankActivitySummary: (params?: { dateFrom?: string; dateTo?: string }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/bank-activity-summary"), {
      query: params,
    }),
  supplierBalances: (params?: { dateFrom?: string; dateTo?: string }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/supplier-balances"), {
      query: params,
    }),
  invoiceLineDetail: (params?: { dateFrom?: string; dateTo?: string }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/invoice-line-detail"), {
      query: params,
    }),
  invoiceLineByCustomer: (params?: {
    dateFrom?: string;
    dateTo?: string;
    customerId?: string;
  }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/invoice-line-by-customer"), {
      query: params,
    }),
  customerList: () =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/customer-list")),
  customerOutstanding: (params?: {
    dateFrom?: string;
    dateTo?: string;
    customerId?: string;
  }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/customer-outstanding"), {
      query: params,
    }),
  customerProducts: (params?: {
    dateFrom?: string;
    dateTo?: string;
    customerId?: string;
  }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/customer-products"), {
      query: params,
    }),
  financialMonthlyBalances: (params?: { dateFrom?: string; dateTo?: string }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(
      path("/reports/financial-monthly-balances"),
      { query: params },
    ),
  financialTrialBalanceByMonth: (params?: { dateTo?: string; periodCount?: number }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(
      path("/reports/financial-trial-balance-by-month"),
      { query: params },
    ),
  productsList: () =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/products-list")),
  productPerformance: (params?: { dateFrom?: string; dateTo?: string }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/product-performance"), {
      query: params,
    }),
  productSaleSummary: (params?: { dateFrom?: string; dateTo?: string }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/product-sale-summary"), {
      query: params,
    }),
  productPurchaseSummary: (params?: { dateFrom?: string; dateTo?: string }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/product-purchase-summary"), {
      query: params,
    }),
  bankPaymentReceiptData: (params?: { dateFrom?: string; dateTo?: string }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/bank-payment-receipt-data"), {
      query: params,
    }),
  stockTransferDetail: (params?: { dateFrom?: string; dateTo?: string }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/stock-transfer-detail"), {
      query: params,
    }),
  productActivitySummary: (params?: { dateFrom?: string; dateTo?: string }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/product-activity-summary"), {
      query: params,
    }),
  projectPayments: (params?: { dateFrom?: string; dateTo?: string }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/reports/project-payments"), {
      query: params,
    }),
  comparativeProfitAndLoss: (params?: { periodCount?: number; asOfDate?: string }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(
      path("/reports/comparative-profit-and-loss"),
      { query: params }
    ),
  comparativePnlByCategory: (params?: { periodCount?: number; asOfDate?: string }) =>
    apiFetch<{ result: Record<string, unknown>[] }>(
      path("/reports/comparative-pnl-by-category"),
      { query: params }
    ),
  comparativePnlByCategoryPivot: (params?: { periodCount?: number; asOfDate?: string }) =>
    apiFetch<{
      result: {
        periods: string[];
        rows: {
          categoryType: string;
          categoryName: string;
          amounts: Record<string, string>;
        }[];
      };
    }>(path("/reports/comparative-pnl-by-category/pivot"), { query: params }),
  downloadComparativePnlByCategoryPivotCsv: async (params?: {
    periodCount?: number;
    asOfDate?: string;
  }) => {
    const q = new URLSearchParams();
    if (params?.periodCount) q.set("periodCount", String(params.periodCount));
    if (params?.asOfDate) q.set("asOfDate", params.asOfDate);
    const qs = q.toString();
    const url = `${resolveApiUrl(path("/reports/comparative-pnl-by-category/pivot/export"))}${qs ? `?${qs}` : ""}`;
    const token = getTokens()?.accessToken;
    const res = await fetch(url, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!res.ok) {
      throw new Error(`Export failed (${res.status})`);
    }
    const blob = await res.blob();
    const objectUrl = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = objectUrl;
    a.download = "comparative-pnl-by-category.csv";
    a.click();
    URL.revokeObjectURL(objectUrl);
  },
  voidSalesInvoiceGoodsIssue: (invoiceId: string, body?: { reversalDate?: string }) =>
    apiFetch<{ result: Record<string, unknown> }>(
      path(`/sales-invoices/${invoiceId}/void-goods-issue`),
      { method: "POST", body: body ?? {} }
    ),
  voidSalesInvoiceGoodsIssueLine: (
    invoiceId: string,
    lineId: string,
    body?: { reversalDate?: string }
  ) =>
    apiFetch<{ result: Record<string, unknown> }>(
      path(`/sales-invoices/${invoiceId}/goods-issue/lines/${lineId}/void`),
      { method: "POST", body: body ?? {} }
    ),
  repostSalesInvoiceGoodsIssueCogs: (
    invoiceId: string,
    body?: { reversalDate?: string }
  ) =>
    apiFetch<{ result: Record<string, unknown> }>(
      path(`/sales-invoices/${invoiceId}/goods-issue/repost-remaining-cogs`),
      { method: "POST", body: body ?? {} }
    ),
  voidDeliveryNote: (noteId: string) =>
    apiFetch<{ result: Record<string, unknown> }>(
      path(`/delivery-notes/${noteId}/void`),
      { method: "POST", body: {} }
    ),
  voidGoodsReceiptNote: (noteId: string) =>
    apiFetch<{ result: Record<string, unknown> }>(
      path(`/goods-receipt-notes/${noteId}/void`),
      { method: "POST", body: {} }
    ),
  voidSalesInvoice: (invoiceId: string, body?: { reversalDate?: string }) =>
    apiFetch<{ result: Record<string, unknown> }>(
      path(`/sales-invoices/${invoiceId}/void`),
      { method: "POST", body: body ?? {} }
    ),
  voidSupplierBill: (billId: string, body?: { reversalDate?: string }) =>
    apiFetch<{ result: Record<string, unknown> }>(
      path(`/supplier-bills/${billId}/void`),
      { method: "POST", body: body ?? {} }
    ),
  voidSalesCredit: (creditId: string, body?: { reversalDate?: string }) =>
    apiFetch<{ result: Record<string, unknown> }>(
      path(`/sales-credits/${creditId}/void`),
      { method: "POST", body: body ?? {} }
    ),
  voidSupplierCredit: (creditId: string, body?: { reversalDate?: string }) =>
    apiFetch<{ result: Record<string, unknown> }>(
      path(`/supplier-credits/${creditId}/void`),
      { method: "POST", body: body ?? {} }
    ),
  reverseStockAdjustment: (adjustmentId: string, body?: { reversalDate?: string }) =>
    apiFetch<{ result: Record<string, unknown> }>(
      path(`/stock-adjustments/${adjustmentId}/reverse`),
      { method: "POST", body: body ?? {} }
    ),
};

export const accessControlApi = {
  listModules: () =>
    apiFetch<{ result: ModuleAccessRow[] }>(path("/access-control/modules")),
  replaceModules: (modules: ModuleAccessRow[]) =>
    apiFetch<{ result: ModuleAccessRow[] }>(path("/access-control/modules"), {
      method: "PUT",
      body: { modules },
    }),
  getEffective: () =>
    apiFetch<{ result: { permissions: string[]; membership: unknown; modules: ModuleAccessRow[] } }>(
      path("/access-control/effective"),
    ),
  listFieldSecurity: (roleId?: string) =>
    apiFetch<{ result: { id: string; roleId: string; fieldKey: string; accessLevel: string }[] }>(
      path("/access-control/field-security"),
      { query: roleId ? { roleId } : undefined },
    ),
  replaceFieldSecurity: (body: {
    roleId: string;
    policies: { fieldKey: string; accessLevel: string }[];
  }) =>
    apiFetch<{ result: unknown[] }>(path("/access-control/field-security"), {
      method: "PUT",
      body,
    }),
  listDataScope: (membershipId: string) =>
    apiFetch<{ result: { scopeType: string; scopeId: string }[] }>(
      path(`/access-control/data-scope/${membershipId}`),
    ),
  replaceDataScope: (
    membershipId: string,
    assignments: { scopeType: string; scopeId: string }[],
  ) =>
    apiFetch<{ result: unknown[] }>(path(`/access-control/data-scope/${membershipId}`), {
      method: "PUT",
      body: { assignments },
    }),
};

export const modulesApi = {
  listEntitlements: () =>
    apiFetch<{ result: { moduleCode: string; enabled: boolean }[] }>(
      path("/module-entitlements")
    ),
  replaceEntitlements: (entitlements: { moduleCode: string; enabled: boolean }[]) =>
    apiFetch<{ result: { moduleCode: string; enabled: boolean }[] }>(
      path("/module-entitlements"),
      { method: "PUT", body: { entitlements } }
    ),
  accessMatrix: () =>
    apiFetch<{ result: ModuleAccessRow[] }>(path("/module-access-matrix")),
};

export interface BillingProviderStatus {
  configured?: boolean;
  ready?: boolean;
  mode?: "live" | "stub" | "off";
  missingEnvKeys?: string[];
  stubAvailable?: boolean;
}

export interface BillingSeatUsage {
  used: number;
  limit: number | null;
  remaining: number | null;
  atLimit: boolean;
}

export interface BillingStatus {
  planCode: string;
  status: string;
  externalCustomerId?: string | null;
  currentPeriodEnd?: string | null;
  seats?: BillingSeatUsage;
  billing?: BillingProviderStatus;
  entitlements?: { moduleCode: string; enabled: boolean }[];
  [key: string]: unknown;
}

export const billingApi = {
  status: () => apiFetch<{ result: BillingStatus }>(path("/billing/status")),
  checkoutSession: (body: {
    planCode?: string;
    successUrl?: string;
    cancelUrl?: string;
  }) =>
    apiFetch<{ result: { mode: string; sessionId: string; url: string; planCode: string } }>(
      path("/billing/checkout-session"),
      { method: "POST", body }
    ),
  portalSession: (body?: { returnUrl?: string }) =>
    apiFetch<{ result: { mode: string; sessionId: string; url: string; warning?: string } }>(
      path("/billing/portal-session"),
      { method: "POST", body: body ?? {} }
    ),
};

export const customFieldsApi = {
  listDefinitions: (entityType?: string) =>
    apiFetch<{
      result: {
        id: string;
        entityType: string;
        fieldKey: string;
        label: string;
        fieldType: string;
      }[];
    }>(path("/custom-field-definitions"), { query: { entityType } }),
  createDefinition: (body: {
    entityType: string;
    fieldKey: string;
    label: string;
    fieldType?: string;
    isRequired?: boolean;
    picklistOptions?: string[];
  }) =>
    apiFetch<{ result: Record<string, unknown> }>(path("/custom-field-definitions"), {
      method: "POST",
      body,
    }),
};

export interface AgingRow {
  partyId: string;
  partyName?: string | null;
  partyCode?: string | null;
  kind: "customer" | "supplier";
  invoicesTotal: string;
  receiptsTotal: string;
  balance: string;
  oldestDate?: string | null;
  ageDays: number;
  bucket: string;
  [key: string]: unknown;
}

export interface AgingBucket {
  label: string;
  total: string;
  count: number;
}

export interface AgingResult {
  asOfDate: string;
  rows: AgingRow[];
  buckets: AgingBucket[];
  totals: { outstanding: string; partyCount: number };
}

export interface StatementLine {
  date: string;
  kind: string;
  reference?: string | null;
  debit: string;
  credit: string;
  balance: string;
  id: string;
  [key: string]: unknown;
}

export interface StatementResult {
  party: { id: string; name?: string | null; code?: string | null };
  lines: StatementLine[];
  totals: { debit: string; credit: string; balance: string };
}

export interface TaxRateRow {
  region?: string;
  regionCode?: string;
  taxCode?: string;
  taxRate?: number;
  additionalTaxRate?: number;
  accountId?: string;
  printLabel?: string;
  status?: string;
  [key: string]: unknown;
}

export interface WhtRow {
  taxName?: string;
  taxCode?: string;
  taxRate?: number;
  [key: string]: unknown;
}

export interface TaxRegion {
  regionName?: string;
  regionCode?: string;
  [key: string]: unknown;
}

export interface TaxesYearEnd {
  yearEndDate?: string | null;
  taxDisplay?: Record<string, { label?: string; supplier?: boolean; customer?: boolean }>;
  gstRates?: TaxRateRow[];
  fedRates?: TaxRateRow[];
  adtRates?: TaxRateRow[];
  whtRates?: WhtRow[];
  taxRegions?: TaxRegion[];
}

export interface PaymentInitiateInput {
  customerId: string;
  amount: string;
  bankAccountId?: string | null;
}

export interface AssemblyTemplate {
  id: string;
  code: string;
  name: string;
  finishedProductCode: string;
  lines?: Array<{ componentProductCode: string; quantity: string }>;
  [key: string]: unknown;
}

export interface AssemblyJob {
  id: string;
  jobNumber: string;
  jobDate: string;
  templateId?: string | null;
  finishedProductCode: string;
  quantity: string;
  status: string;
  [key: string]: unknown;
}

export interface ProjectRow {
  id: string;
  code: string;
  name: string;
  isActive: boolean;
  [key: string]: unknown;
}

export interface LocationRow {
  id: string;
  code: string;
  name: string;
  isMain: boolean;
  [key: string]: unknown;
}

export interface FxRevaluationRun {
  id: string;
  revaluationDate: string;
  bankAccountId: string;
  [key: string]: unknown;
}

export const assemblyApi = {
  listTemplates: () =>
    apiFetch<{ result: AssemblyTemplate[] }>(path("/assembly/templates")),
  createTemplate: (body: {
    code: string;
    name: string;
    finishedProductCode: string;
    lines: Array<{ componentProductCode: string; quantity: string }>;
  }) =>
    apiFetch<{ result: AssemblyTemplate }>(path("/assembly/templates"), {
      method: "POST",
      body,
    }),
  listJobs: () => apiFetch<{ result: AssemblyJob[] }>(path("/assembly/jobs")),
  createJob: (body: {
    templateId: string;
    jobDate: string;
    quantity: string;
    batchNumber?: string;
    expiryDate?: string;
  }) =>
    apiFetch<{ result: AssemblyJob }>(path("/assembly/jobs"), { method: "POST", body }),
  finishJob: (jobId: string) =>
    apiFetch<{ result: AssemblyJob; posted: boolean }>(
      path(`/assembly/jobs/${jobId}/finish`),
      { method: "POST" },
    ),
};

export const fxRevaluationApi = {
  list: () => apiFetch<{ result: FxRevaluationRun[] }>(path("/bank/fx-revaluations")),
  create: (body: {
    bankAccountId: string;
    revaluationDate: string;
    foreignBalance: string;
    exchangeRate: string;
    bookBalanceBase?: string;
  }) =>
    apiFetch<{ result: Record<string, unknown>; posted: boolean }>(
      path("/bank/fx-revaluations"),
      { method: "POST", body },
    ),
};

export const projectsApi = {
  list: () => apiFetch<{ result: ProjectRow[] }>(path("/projects")),
  create: (body: { code: string; name: string }) =>
    apiFetch<{ result: ProjectRow }>(path("/projects"), { method: "POST", body }),
  update: (id: string, body: { name?: string; isActive?: boolean }) =>
    apiFetch<{ result: ProjectRow }>(path(`/projects/${id}`), { method: "PATCH", body }),
};

export const locationsApi = {
  list: () => apiFetch<{ result: LocationRow[] }>(path("/locations")),
  create: (body: { code: string; name: string; isMain?: boolean }) =>
    apiFetch<{ result: LocationRow }>(path("/locations"), { method: "POST", body }),
  update: (id: string, body: { name?: string; isMain?: boolean }) =>
    apiFetch<{ result: LocationRow }>(path(`/locations/${id}`), { method: "PATCH", body }),
};

export interface BudgetLineRow {
  id: string;
  nominalCode: string;
  period: string;
  amount: string;
  [key: string]: unknown;
}

export interface BudgetRow {
  id: string;
  code: string;
  name: string;
  fiscalYear: number;
  isActive: boolean;
  lines?: BudgetLineRow[];
  [key: string]: unknown;
}

export const budgetsApi = {
  list: () => apiFetch<{ result: BudgetRow[] }>(path("/budgets")),
  get: (id: string) => apiFetch<{ result: BudgetRow }>(path(`/budgets/${id}`)),
  create: (body: {
    code: string;
    name: string;
    fiscalYear: number;
    lines?: { nominalCode: string; period?: string; amount: number | string }[];
  }) => apiFetch<{ result: BudgetRow }>(path("/budgets"), { method: "POST", body }),
  update: (id: string, body: { name?: string; isActive?: boolean }) =>
    apiFetch<{ result: BudgetRow }>(path(`/budgets/${id}`), { method: "PATCH", body }),
};

export interface ApprovalPolicyRow {
  id: string;
  entityType: string;
  rules: { minAmount?: number | string; requiresApprovalAbove?: number | string };
  [key: string]: unknown;
}

export interface ApprovalRequestRow {
  id: string;
  entityType: string;
  entityId: string;
  amount: string;
  status: string;
  notes?: string | null;
  createdAt?: string;
  [key: string]: unknown;
}

export const approvalApi = {
  listPolicies: () => apiFetch<{ result: ApprovalPolicyRow[] }>(path("/approval-policies")),
  upsertPolicy: (body: { entityType: string; rules: Record<string, unknown> }) =>
    apiFetch<{ result: ApprovalPolicyRow }>(path("/approval-policies"), {
      method: "PUT",
      body,
    }),
  listRequests: (status?: string) =>
    apiFetch<{ result: ApprovalRequestRow[] }>(
      path(status ? `/approval-requests?status=${encodeURIComponent(status)}` : "/approval-requests"),
    ),
  approve: (id: string) =>
    apiFetch<{ result: ApprovalRequestRow }>(path(`/approval-requests/${id}/approve`), {
      method: "POST",
    }),
  reject: (id: string) =>
    apiFetch<{ result: ApprovalRequestRow }>(path(`/approval-requests/${id}/reject`), {
      method: "POST",
    }),
};

export interface AttachmentRow {
  id: string;
  fileName: string;
  byteSize: number;
  mimeType?: string | null;
  createdAt?: string;
  [key: string]: unknown;
}

export const attachmentsApi = {
  list: (entityType: string, entityId: string) =>
    apiFetch<{ result: AttachmentRow[] }>(
      path(
        `/attachments?entityType=${encodeURIComponent(entityType)}&entityId=${encodeURIComponent(entityId)}`,
      ),
    ),
  upload: async (entityType: string, entityId: string, file: File) => {
    const companyId = getCurrentCompanyId();
    if (!companyId) throw new Error("No company selected");
    const form = new FormData();
    form.append("entityType", entityType);
    form.append("entityId", entityId);
    form.append("file", file);
    const token =
      typeof window !== "undefined" ? localStorage.getItem("accessToken") : null;
    const res = await fetch(`/api/v1/companies/${companyId}/attachments/upload`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: form,
    });
    if (!res.ok) {
      const err = (await res.json().catch(() => ({}))) as { detail?: string };
      throw new Error(err.detail ?? res.statusText);
    }
    return res.json() as Promise<{ result: AttachmentRow }>;
  },
  downloadUrl: (attachmentId: string) => {
    const companyId = getCurrentCompanyId();
    if (!companyId) return "#";
    return `/api/v1/companies/${companyId}/attachments/${attachmentId}/download`;
  },
  delete: async (attachmentId: string, entityType?: string) => {
    const companyId = getCurrentCompanyId();
    if (!companyId) throw new Error("No company selected");
    const qs = entityType ? `?entityType=${encodeURIComponent(entityType)}` : "";
    const token =
      typeof window !== "undefined" ? localStorage.getItem("accessToken") : null;
    const res = await fetch(
      `/api/v1/companies/${companyId}/attachments/${attachmentId}${qs}`,
      {
        method: "DELETE",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      },
    );
    if (!res.ok && res.status !== 204) {
      const err = (await res.json().catch(() => ({}))) as { detail?: string };
      throw new Error(err.detail ?? res.statusText);
    }
  },
  productImageUrl: (attachmentId: string | null | undefined) =>
    attachmentId ? attachmentsApi.downloadUrl(attachmentId) : null,
};

export interface IntegrationProviderStatus {
  enabled: boolean;
  configured: boolean;
  ready: boolean;
  mode?: "off" | "stub" | "live";
  missingEnvKeys?: string[];
  stubAvailable?: boolean;
  errorCount?: number;
  dueRetryCount?: number;
  retryWorkerEnabled?: boolean;
}

export interface IntegrationsReadiness {
  fbr: IntegrationProviderStatus;
  paypro: IntegrationProviderStatus;
  kuickpay: IntegrationProviderStatus;
  fbrRetryWorker: boolean;
}

export const integrationsApi = {
  getReadiness: () =>
    apiFetch<{ result: IntegrationsReadiness }>(path("/integrations/readiness")),
};

export const fbrApi = {
  listErrors: () =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/fbr/submissions/errors")),
  retryPending: () =>
    apiFetch<{ result: { queued: number } }>(path("/fbr/retry-pending"), {
      method: "POST",
    }),
};

export const paymentsApi = {
  listPaypro: () =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/payments/paypro/transactions")),
  initiatePaypro: (body: PaymentInitiateInput) =>
    apiFetch<{ result: Record<string, unknown> }>(path("/payments/paypro/initiate"), {
      method: "POST",
      body,
    }),
  listKuickpay: () =>
    apiFetch<{ result: Record<string, unknown>[] }>(path("/payments/kuickpay/transactions")),
  initiateKuickpay: (body: PaymentInitiateInput) =>
    apiFetch<{ result: Record<string, unknown> }>(path("/payments/kuickpay/initiate"), {
      method: "POST",
      body,
    }),
};

export const autoCodeApi = {
  peek: (entityKey: string) =>
    apiFetch<{ result: { enabled: boolean; nextCode: string | null } }>(
      path(`/auto-codes/${encodeURIComponent(entityKey)}/peek`),
    ),
};

export interface TransactionTemplate {
  id: string;
  module: string;
  name: string;
  payload: Record<string, unknown>;
  createdAt?: string;
}

export const templatesApi = {
  list: (module: string) =>
    apiFetch<{ result: TransactionTemplate[] }>(
      path(`/transaction-templates?module=${encodeURIComponent(module)}`),
    ),
  get: (id: string) =>
    apiFetch<{ result: TransactionTemplate }>(path(`/transaction-templates/${id}`)),
  create: (body: { module: string; name: string; payload: Record<string, unknown> }) =>
    apiFetch<{ result: TransactionTemplate }>(path("/transaction-templates"), {
      method: "POST",
      body,
    }),
  remove: (id: string) =>
    apiFetch<void>(path(`/transaction-templates/${id}`), { method: "DELETE" }),
};

export interface RecurringSchedule {
  id: string;
  name: string;
  module: string;
  frequency: string;
  interval: number;
  nextRunDate: string;
  endDate?: string | null;
  isActive: boolean;
  payload: Record<string, unknown>;
  lastRunAt?: string | null;
  createdAt?: string;
}

export interface RecurringScheduleCreateInput {
  name: string;
  module: string;
  frequency?: string;
  interval?: number;
  nextRunDate: string;
  endDate?: string | null;
  isActive?: boolean;
  payload?: Record<string, unknown>;
}

export const recurringSchedulesApi = {
  list: () => apiFetch<{ result: RecurringSchedule[] }>(path("/recurring-schedules")),
  create: (body: RecurringScheduleCreateInput) =>
    apiFetch<{ result: RecurringSchedule }>(path("/recurring-schedules"), {
      method: "POST",
      body,
    }),
  update: (id: string, body: Partial<RecurringScheduleCreateInput>) =>
    apiFetch<{ result: RecurringSchedule }>(path(`/recurring-schedules/${id}`), {
      method: "PATCH",
      body,
    }),
  remove: (id: string) =>
    apiFetch<void>(path(`/recurring-schedules/${id}`), { method: "DELETE" }),
  runDue: () =>
    apiFetch<{ result: { executed: unknown[]; count: number } }>(
      path("/recurring-schedules/run-due"),
      { method: "POST" },
    ),
};

export const lastRateApi = {
  sales: (customerId: string, productCode: string, docType = "SI", forEdit = true) =>
    apiFetch<{
      result: {
        rate: string;
        gstCode?: string | null;
        gstRate?: string;
        invoiceNumber?: string;
        documentNumber?: string;
        documentLabel?: string;
      } | null;
    }>(
      path(
        `/sales/last-rate?customerId=${encodeURIComponent(customerId)}&productCode=${encodeURIComponent(productCode)}&docType=${encodeURIComponent(docType)}&forEdit=${forEdit ? "true" : "false"}`,
      ),
    ),
  purchase: (supplierId: string, productCode: string, docType = "VI", forEdit = true) =>
    apiFetch<{
      result: {
        rate: string;
        gstCode?: string | null;
        gstRate?: string;
        billNumber?: string;
        documentNumber?: string;
        documentLabel?: string;
      } | null;
    }>(
      path(
        `/purchases/last-rate?supplierId=${encodeURIComponent(supplierId)}&productCode=${encodeURIComponent(productCode)}&docType=${encodeURIComponent(docType)}&forEdit=${forEdit ? "true" : "false"}`,
      ),
    ),
};
