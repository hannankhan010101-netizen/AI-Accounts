import type { AuditLogEntry, AuditLogFilters } from "@/lib/api/tenant";

/** Deep-link to User Log with pre-filled filters (P37). */
export function userLogHref(filters: AuditLogFilters = {}): string {
  const params = new URLSearchParams();
  if (filters.transactionType) params.set("transactionType", filters.transactionType);
  if (filters.transactionId) params.set("transactionId", filters.transactionId);
  if (filters.userId) params.set("userId", filters.userId);
  if (filters.dateFrom) params.set("dateFrom", filters.dateFrom);
  if (filters.dateTo) params.set("dateTo", filters.dateTo);
  if (filters.rbacOnly) params.set("rbacOnly", "true");
  if (filters.typeContains) params.set("typeContains", filters.typeContains);
  const qs = params.toString();
  return qs ? `/settings/user-log?${qs}` : "/settings/user-log";
}

export function roleImportJobAuditHref(jobId: string): string {
  return userLogHref({
    transactionType: "ROLE_IMPORT_JOB",
    transactionId: jobId,
  });
}

type NavRule = {
  test: (type: string) => boolean;
  path: (id: string) => string;
  label: string;
  needsId?: boolean;
};

/** Document / module routes for audit View links (P40). */
const DOCUMENT_NAV_RULES: NavRule[] = [
  {
    test: (t) => t === "USER_MEMBERSHIP_REVOKE" || t === "USER_REINVITE",
    path: (id) => `/settings/users?reinviteUserId=${encodeURIComponent(id)}`,
    label: "Reinvite",
    needsId: true,
  },
  {
    test: (t) => t.startsWith("USER_"),
    path: (id) => `/settings/users?userId=${encodeURIComponent(id)}`,
    label: "Users",
    needsId: true,
  },
  {
    test: (t) => t === "ROLE_CLONE",
    path: (id) => (id ? `/settings/roles/${id}` : "/settings/roles"),
    label: "Role",
  },
  {
    test: (t) => t === "ROLE_IMPORT_JOB",
    path: () => "/settings/roles",
    label: "Roles",
    needsId: false,
  },
  {
    test: (t) => t.startsWith("ROLE_"),
    path: () => "/settings/roles",
    label: "Roles",
    needsId: false,
  },
  {
    test: (t) =>
      t.includes("SALES_INVOICE") ||
      t === "SI_VOID" ||
      t === "SALES_INVOICE_VOID" ||
      (t.includes("INVOICE") && t.includes("SALES")),
    path: (id) => `/sales/invoices/${id}`,
    label: "Invoice",
    needsId: true,
  },
  {
    test: (t) => t.includes("PDC_RECEIVED"),
    path: (id) => `/sales/pdc-received/${id}`,
    label: "PDC received",
    needsId: true,
  },
  {
    test: (t) =>
      t.includes("SALES_RECEIPT") ||
      (t.includes("RECEIPT") && t.includes("SALES")),
    path: (id) => `/sales/receipts/${id}`,
    label: "Receipt",
    needsId: true,
  },
  {
    test: (t) =>
      t.includes("SALES_ORDER") ||
      t === "SO_VOID" ||
      (t.includes("ORDER") && t.includes("SALES")),
    path: (id) => `/sales/orders/${id}`,
    label: "Order",
    needsId: true,
  },
  {
    test: (t) => t.includes("QUOTATION") && t.includes("SALES"),
    path: (id) => `/sales/quotations/${id}`,
    label: "Quotation",
    needsId: true,
  },
  {
    test: (t) => t.includes("DELIVERY") || t.includes("GDNSI") || t.includes("GDNSO"),
    path: () => "/sales/delivery-notes",
    label: "Delivery notes",
    needsId: false,
  },
  {
    test: (t) => t.includes("SALES_CREDIT") || (t.includes("CREDIT") && t.includes("SALES")),
    path: (id) => (id ? `/sales/credits/${id}` : "/sales/credits"),
    label: "Credit",
    needsId: false,
  },
  {
    test: (t) =>
      t.includes("SUPPLIER_BILL") ||
      t.includes("PURCHASE_BILL") ||
      t === "VI_VOID" ||
      (t.includes("BILL") && (t.includes("PURCHASE") || t.includes("SUPPLIER"))),
    path: (id) => `/purchases/bills/${id}`,
    label: "Bill",
    needsId: true,
  },
  {
    test: (t) =>
      t.includes("SUPPLIER_PAYMENT") ||
      t.includes("PURCHASE_PAYMENT") ||
      (t.includes("PAYMENT") && (t.includes("PURCHASE") || t.includes("SUPPLIER"))),
    path: (id) => (id ? `/purchases/payments/${id}` : "/purchases/payments"),
    label: "Payment",
    needsId: false,
  },
  {
    test: (t) =>
      t.includes("PURCHASE_ORDER") ||
      t === "PO_VOID" ||
      (t.includes("ORDER") && t.includes("PURCHASE")),
    path: (id) => `/purchases/orders/${id}`,
    label: "PO",
    needsId: true,
  },
  {
    test: (t) => t.includes("GRN") || t.includes("GOODS_RECEIPT"),
    path: () => "/purchases/grn",
    label: "GRN",
    needsId: false,
  },
  {
    test: (t) => t.includes("PDC_ISSUED"),
    path: (id) => `/purchases/pdc-issued/${id}`,
    label: "PDC issued",
    needsId: true,
  },
  {
    test: (t) => t.includes("BANK_RECEIPT"),
    path: (id) => `/bank/receipts/${id}`,
    label: "Bank receipt",
    needsId: true,
  },
  {
    test: (t) => t.includes("BANK_PAYMENT"),
    path: (id) => `/bank/payments/${id}`,
    label: "Bank payment",
    needsId: true,
  },
  {
    test: (t) => t.includes("BANK_TRANSFER"),
    path: (id) => `/bank/transfers/${id}`,
    label: "Bank transfer",
    needsId: true,
  },
  {
    test: (t) => t.includes("BANK_RECONCILIATION"),
    path: (id) => `/bank/reconciliation/${id}`,
    label: "Reconciliation",
    needsId: true,
  },
  {
    test: (t) => t.includes("JOURNAL"),
    path: (id) => (id ? `/settings/journals/${id}` : "/settings/journals"),
    label: "Journal",
    needsId: false,
  },
  {
    test: (t) => t.includes("IMPORT_JOB") || t.includes("ROLE_IMPORT"),
    path: (id) => (id ? userLogHref({ transactionId: id }) : "/settings/import-jobs"),
    label: "Import job",
    needsId: false,
  },
  {
    test: (t) => t.includes("CUSTOMER"),
    path: (id) => (id ? `/sales/customers?highlight=${encodeURIComponent(id)}` : "/sales/customers"),
    label: "Customer",
    needsId: false,
  },
  {
    test: (t) => t.includes("SUPPLIER"),
    path: (id) =>
      id ? `/purchases/suppliers?highlight=${encodeURIComponent(id)}` : "/purchases/suppliers",
    label: "Supplier",
    needsId: false,
  },
  {
    test: (t) => t.includes("PRODUCT"),
    path: () => "/inventory/products",
    label: "Products",
    needsId: false,
  },
  {
    test: (t) => t.includes("BUDGET"),
    path: () => "/settings/budgets",
    label: "Budgets",
    needsId: false,
  },
];

function matchDocumentNav(type: string, id: string): NavRule | null {
  for (const rule of DOCUMENT_NAV_RULES) {
    if (!rule.test(type)) continue;
    if (rule.needsId !== false && !id) continue;
    return rule;
  }
  return null;
}

/** Resolve a View link for an audit row when a settings or document route exists. */
export function auditNavigationHref(entry: AuditLogEntry): string | null {
  const type = String(entry.transactionType ?? "").trim();
  const id = String(entry.transactionId ?? "").trim();
  if (!type) return null;

  if (type.startsWith("security.")) {
    return null;
  }

  const doc = matchDocumentNav(type, id);
  if (doc) {
    return doc.path(id);
  }

  return null;
}

export function auditNavigationLabel(entry: AuditLogEntry): string {
  const type = String(entry.transactionType ?? "").trim();
  const id = String(entry.transactionId ?? "").trim();
  if (!type || type.startsWith("security.")) {
    return "";
  }

  const doc = matchDocumentNav(type, id);
  return doc?.label ?? "";
}
