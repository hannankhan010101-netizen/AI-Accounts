import type { EntityModule, TargetFieldDef } from "../types/pipeline.js";

export const TARGET_SCHEMAS: Record<EntityModule, TargetFieldDef[]> = {
  customers: [
    { field: "code", label: "Customer Code", type: "string", required: true },
    { field: "name", label: "Customer Name", type: "string", required: true },
    { field: "email", label: "Email", type: "string" },
    { field: "phone", label: "Phone", type: "string" },
  ],
  suppliers: [
    { field: "code", label: "Supplier Code", type: "string", required: true },
    { field: "name", label: "Supplier Name", type: "string", required: true },
    { field: "email", label: "Email", type: "string" },
    { field: "phone", label: "Phone", type: "string" },
  ],
  products: [
    { field: "code", label: "Product Code", type: "string", required: true },
    { field: "name", label: "Product Name", type: "string", required: true },
    { field: "category", label: "Category", type: "string" },
    { field: "unit", label: "Unit of Measure", type: "string" },
    { field: "cost", label: "Cost", type: "decimal" },
    { field: "salePrice", label: "Sale Price", type: "decimal" },
    { field: "isStock", label: "Track Stock", type: "boolean" },
  ],
  chart_of_accounts: [
    { field: "code", label: "Account Code", type: "string", required: true },
    { field: "name", label: "Account Name", type: "string", required: true },
    { field: "category", label: "Category", type: "string", required: true },
    { field: "accountType", label: "Account Type", type: "string" },
  ],
  invoices: [
    { field: "invoiceNumber", label: "Invoice Number", type: "string", required: true },
    { field: "invoiceDate", label: "Invoice Date", type: "date", required: true },
    { field: "customerCode", label: "Customer Code", type: "string", required: true },
    { field: "totalAmount", label: "Total Amount", type: "decimal", required: true },
    { field: "status", label: "Status", type: "enum", enumValues: ["draft", "posted", "paid"] },
  ],
  bills: [
    { field: "billNumber", label: "Bill Number", type: "string", required: true },
    { field: "billDate", label: "Bill Date", type: "date", required: true },
    { field: "supplierCode", label: "Supplier Code", type: "string", required: true },
    { field: "totalAmount", label: "Total Amount", type: "decimal", required: true },
    { field: "status", label: "Status", type: "enum", enumValues: ["draft", "posted", "paid"] },
  ],
  receipts: [
    { field: "receiptNumber", label: "Receipt Number", type: "string", required: true },
    { field: "receiptDate", label: "Receipt Date", type: "date", required: true },
    { field: "customerCode", label: "Customer Code", type: "string", required: true },
    { field: "totalAmount", label: "Total Amount", type: "decimal", required: true },
    { field: "bankAccountCode", label: "Bank Account", type: "string" },
  ],
  payments: [
    { field: "voucherNumber", label: "Voucher Number", type: "string", required: true },
    { field: "paymentDate", label: "Payment Date", type: "date", required: true },
    { field: "supplierCode", label: "Supplier Code", type: "string", required: true },
    { field: "totalAmount", label: "Total Amount", type: "decimal", required: true },
    { field: "bankAccountCode", label: "Bank Account", type: "string" },
  ],
  bank_transactions: [
    { field: "voucherNumber", label: "Voucher Number", type: "string", required: true },
    { field: "transactionDate", label: "Transaction Date", type: "date", required: true },
    { field: "bankAccountCode", label: "Bank Account", type: "string", required: true },
    { field: "totalAmount", label: "Amount", type: "decimal", required: true },
    { field: "direction", label: "Direction", type: "enum", enumValues: ["in", "out"] },
  ],
  stock_movements: [
    { field: "reference", label: "Reference", type: "string", required: true },
    { field: "movementDate", label: "Movement Date", type: "date", required: true },
    { field: "productCode", label: "Product Code", type: "string", required: true },
    { field: "quantity", label: "Quantity", type: "decimal", required: true },
    { field: "locationCode", label: "Location", type: "string" },
  ],
  journals: [
    { field: "journalNumber", label: "Journal Number", type: "string", required: true },
    { field: "journalDate", label: "Journal Date", type: "date", required: true },
    { field: "refNo", label: "Reference", type: "string" },
    { field: "lines", label: "Journal Lines", type: "string", required: true },
  ],
  taxes: [
    { field: "code", label: "Tax Code", type: "string", required: true },
    { field: "name", label: "Tax Name", type: "string", required: true },
    { field: "rate", label: "Rate %", type: "decimal", required: true },
  ],
  projects: [
    { field: "code", label: "Project Code", type: "string", required: true },
    { field: "name", label: "Project Name", type: "string", required: true },
    { field: "isActive", label: "Active", type: "boolean" },
  ],
};

/** FastAccounts labeled export field aliases → target fields. */
export const FASTACCOUNTS_PRESETS: Partial<
  Record<EntityModule, Record<string, string>>
> = {
  customers: {
    "Account No": "code",
    "Business Name": "name",
    "Contact Name": "name",
    Balance: "openingBalance",
  },
  suppliers: {
    "Account No": "code",
    "Business Name": "name",
  },
  products: {
    "Product Name": "name",
    ID: "code",
    "Sale Price": "salePrice",
    Category: "category",
    Quantity: "openingQty",
  },
  invoices: {
    "Invoice No": "invoiceNumber",
    "Invoice Date": "invoiceDate",
    "Account No": "customerCode",
    Total: "totalAmount",
  },
  bills: {
    "Invoice No": "billNumber",
    "Invoice Date": "billDate",
    "Account No": "supplierCode",
    Total: "totalAmount",
  },
  receipts: {
    "Voucher No": "receiptNumber",
    "Payment Date": "receiptDate",
    "Account No": "customerCode",
    Total: "totalAmount",
  },
  chart_of_accounts: {
    "Account No": "code",
    "Account Name": "name",
    Category: "category",
  },
};

export function getTargetSchema(module: EntityModule): TargetFieldDef[] {
  return TARGET_SCHEMAS[module] ?? [];
}
