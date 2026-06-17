export type ReportDrillContext = {
  dateFrom?: string;
  dateTo?: string;
};

export function buildGeneralLedgerHref(params: {
  nominalCode: string;
  dateFrom?: string;
  dateTo?: string;
}): string {
  const search = new URLSearchParams({ nominalCode: params.nominalCode });
  if (params.dateFrom) search.set("dateFrom", params.dateFrom);
  if (params.dateTo) search.set("dateTo", params.dateTo);
  return `/reports/general-ledger?${search.toString()}`;
}

export function buildJournalDetailHref(journalId: string): string {
  return `/settings/journals/${journalId}`;
}

export function buildStatementLineHref(kind: string, id: string): string | null {
  switch ((kind || "").toLowerCase()) {
    case "invoice":
      return `/sales/invoices/${id}`;
    case "receipt":
      return `/sales/receipts/${id}`;
    case "bill":
      return `/purchases/bills/${id}`;
    case "payment":
      return `/purchases/payments/${id}`;
    case "adjustment":
      return `/inventory/stock-adjustment/${id}`;
    default:
      return null;
  }
}

function rowId(row: Record<string, unknown>, ...keys: string[]): string | null {
  for (const key of keys) {
    const val = row[key];
    if (val != null && String(val).trim()) return String(val).trim();
  }
  return null;
}

function inferDocumentHref(row: Record<string, unknown>): string | null {
  const id = rowId(row, "id", "entityId", "entity_id");
  if (!id) return null;

  if (
    row.invoiceNumber != null ||
    row.invoiceDate != null ||
    row.invoiceId != null ||
    row.salesInvoiceId != null
  ) {
    return `/sales/invoices/${id}`;
  }
  if (row.billNumber != null || row.billDate != null || row.billId != null) {
    return `/purchases/bills/${id}`;
  }
  if (row.receiptDate != null && row.direction !== "out") {
    return `/bank/receipts/${id}`;
  }
  if (row.paymentDate != null || (row.direction === "out" && row.voucherNumber)) {
    return `/bank/payments/${id}`;
  }
  if (row.transferDate != null) {
    return `/bank/transfers/${id}`;
  }
  if (row.kind === "adjustment" || row.adjustmentId != null || row.quantityDelta != null) {
    return `/inventory/stock-adjustment/${id}`;
  }
  return null;
}

/** Hyperlink cells from generic report runner rows (FA drill-down). */
export function buildDynamicReportCellHref(
  key: string,
  value: unknown,
  row: Record<string, unknown>,
  context?: ReportDrillContext,
): string | null {
  const s = value == null ? "" : String(value).trim();
  if (!s) return null;
  const k = key.toLowerCase();

  if (k === "id" || k.endsWith("id")) {
    const doc = inferDocumentHref({ ...row, [key]: value });
    if (doc) return doc;
  }

  if (k === "customerid" || k === "customer_id" || k === "partyid") {
    const params = new URLSearchParams({ customerId: s });
    if (context?.dateFrom) params.set("dateFrom", context.dateFrom);
    if (context?.dateTo) params.set("dateTo", context.dateTo);
    return `/reports/customer-statement?${params.toString()}`;
  }
  if (k === "supplierid" || k === "supplier_id") {
    const params = new URLSearchParams({ supplierId: s });
    if (context?.dateFrom) params.set("dateFrom", context.dateFrom);
    if (context?.dateTo) params.set("dateTo", context.dateTo);
    return `/reports/supplier-statement?${params.toString()}`;
  }
  if (k.includes("nominal") && (k.includes("code") || k === "nominalcode")) {
    return buildGeneralLedgerHref({
      nominalCode: s,
      dateFrom: context?.dateFrom,
      dateTo: context?.dateTo,
    });
  }
  if (k === "journalid" || k === "journal_id") {
    return buildJournalDetailHref(s);
  }
  if (k === "invoiceid" || k === "invoice_id" || k === "salesinvoiceid") {
    return `/sales/invoices/${s}`;
  }
  if (k === "billid" || k === "bill_id" || k === "supplierbillid") {
    return `/purchases/bills/${s}`;
  }
  if (k === "productcode" || k === "componentproductcode" || k === "finishedproductcode") {
    return `/inventory/products?q=${encodeURIComponent(s)}`;
  }
  if (k === "jobnumber") {
    return `/inventory/assembly/jobs?q=${encodeURIComponent(s)}`;
  }

  const invoiceId = rowId(row, "invoiceId", "invoice_id", "salesInvoiceId");
  const billId = rowId(row, "billId", "bill_id", "supplierBillId");
  if (k.includes("invoice") && (k.includes("number") || k.includes("no"))) {
    if (invoiceId) return `/sales/invoices/${invoiceId}`;
    const rowDocId = rowId(row, "id");
    if (rowDocId && row.invoiceDate) return `/sales/invoices/${rowDocId}`;
  }
  if (k.includes("bill") && (k.includes("number") || k.includes("no"))) {
    if (billId) return `/purchases/bills/${billId}`;
    const rowDocId = rowId(row, "id");
    if (rowDocId && row.billDate) return `/purchases/bills/${rowDocId}`;
  }

  const entityType = String(row.entityType ?? row.entity_type ?? row.kind ?? "").toLowerCase();
  const entityId = rowId(row, "entityId", "entity_id", "id");
  if (entityId && (k === "documentnumber" || k === "reference" || k.includes("voucher"))) {
    const href = buildStatementLineHref(entityType, entityId);
    if (href) return href;
    if (row.paymentDate) return `/bank/payments/${entityId}`;
    if (row.receiptDate) return `/bank/receipts/${entityId}`;
    if (row.transferDate) return `/bank/transfers/${entityId}`;
  }

  if (k.includes("voucher") && entityId) {
    if (row.receiptDate) return `/bank/receipts/${entityId}`;
    if (row.transferDate) return `/bank/transfers/${entityId}`;
    return `/bank/payments/${entityId}`;
  }

  return null;
}
