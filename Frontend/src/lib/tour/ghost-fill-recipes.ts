/** Staged demo values for ghost form fill (display-only during tours). */

export type GhostFillResolver =
  | { type: "literal"; value: string }
  | { type: "firstCustomer" }
  | { type: "firstSupplier" }
  | { type: "firstBankAccount" }
  | { type: "firstProductCode" }
  | { type: "today" };

export type GhostFillEntry = {
  /** react-hook-form path */
  path: string;
  resolve: GhostFillResolver;
  delayMs: number;
};

export type GhostFillRecipe = {
  id: string;
  fields: GhostFillEntry[];
};

export const GHOST_FILL_RECIPES: Record<string, GhostFillRecipe> = {
  "sales-invoice-header": {
    id: "sales-invoice-header",
    fields: [
      { path: "invoiceDate", resolve: { type: "today" }, delayMs: 0 },
      { path: "customerId", resolve: { type: "firstCustomer" }, delayMs: 450 },
    ],
  },
  "sales-invoice-lines": {
    id: "sales-invoice-lines",
    fields: [
      { path: "lines.0.quantity", resolve: { type: "literal", value: "10" }, delayMs: 0 },
      { path: "lines.0.rate", resolve: { type: "literal", value: "4500" }, delayMs: 280 },
      { path: "lines.0.gstRate", resolve: { type: "literal", value: "18" }, delayMs: 560 },
      {
        path: "lines.0.productCode",
        resolve: { type: "firstProductCode" },
        delayMs: 840,
      },
    ],
  },
  "purchase-bill-header": {
    id: "purchase-bill-header",
    fields: [
      { path: "billDate", resolve: { type: "today" }, delayMs: 0 },
      { path: "supplierId", resolve: { type: "firstSupplier" }, delayMs: 450 },
    ],
  },
  "purchase-bill-lines": {
    id: "purchase-bill-lines",
    fields: [
      { path: "lines.0.quantity", resolve: { type: "literal", value: "5" }, delayMs: 0 },
      { path: "lines.0.rate", resolve: { type: "literal", value: "5680" }, delayMs: 300 },
      { path: "lines.0.gstRate", resolve: { type: "literal", value: "18" }, delayMs: 600 },
      {
        path: "lines.0.productCode",
        resolve: { type: "firstProductCode" },
        delayMs: 900,
      },
    ],
  },
  "sales-receipt-header": {
    id: "sales-receipt-header",
    fields: [
      { path: "receiptDate", resolve: { type: "today" }, delayMs: 0 },
      { path: "customerId", resolve: { type: "firstCustomer" }, delayMs: 400 },
      { path: "bankAccountId", resolve: { type: "firstBankAccount" }, delayMs: 750 },
      { path: "totalAmount", resolve: { type: "literal", value: "53100" }, delayMs: 1100 },
    ],
  },
  "supplier-payment-header": {
    id: "supplier-payment-header",
    fields: [
      { path: "paymentDate", resolve: { type: "today" }, delayMs: 0 },
      { path: "supplierId", resolve: { type: "firstSupplier" }, delayMs: 400 },
      { path: "bankAccountId", resolve: { type: "firstBankAccount" }, delayMs: 750 },
      { path: "totalAmount", resolve: { type: "literal", value: "28400" }, delayMs: 1100 },
    ],
  },
  "bank-receipt-header": {
    id: "bank-receipt-header",
    fields: [
      { path: "receiptDate", resolve: { type: "today" }, delayMs: 0 },
      { path: "bankAccountId", resolve: { type: "firstBankAccount" }, delayMs: 450 },
      { path: "totalAmount", resolve: { type: "literal", value: "12500" }, delayMs: 900 },
    ],
  },
  "bank-payment-header": {
    id: "bank-payment-header",
    fields: [
      { path: "bankAccountId", resolve: { type: "firstBankAccount" }, delayMs: 0 },
      { path: "paymentDate", resolve: { type: "today" }, delayMs: 400 },
      { path: "totalAmount", resolve: { type: "literal", value: "8900" }, delayMs: 850 },
    ],
  },
  "bank-recon-start": {
    id: "bank-recon-start",
    fields: [
      { path: "bankAccountId", resolve: { type: "firstBankAccount" }, delayMs: 0 },
      { path: "statementDate", resolve: { type: "today" }, delayMs: 350 },
      {
        path: "statementBalance",
        resolve: { type: "literal", value: "186420.50" },
        delayMs: 700,
      },
    ],
  },
};

export type GhostFillContext = {
  customerIds: string[];
  supplierIds: string[];
  bankAccountIds: string[];
  productCodes: string[];
};

export function resolveGhostValue(
  resolver: GhostFillResolver,
  ctx: GhostFillContext,
): string {
  switch (resolver.type) {
    case "literal":
      return resolver.value;
    case "today":
      return new Date().toISOString().slice(0, 10);
    case "firstCustomer":
      return ctx.customerIds[0] ?? "";
    case "firstSupplier":
      return ctx.supplierIds[0] ?? "";
    case "firstBankAccount":
      return ctx.bankAccountIds[0] ?? "";
    case "firstProductCode":
      return ctx.productCodes[0] ?? "SVC-001";
    default:
      return "";
  }
}
