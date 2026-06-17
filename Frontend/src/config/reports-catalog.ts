/**
 * Live report routes — keep in sync with Insights hub and command palette.
 */

export interface ReportCatalogItem {
  id: string;
  name: string;
  href: string;
  category: string;
}

export const reportCatalog: ReportCatalogItem[] = [
  { id: "TB", name: "Trial Balance", href: "/reports/trial-balance", category: "Financial" },
  { id: "GL", name: "General Ledger", href: "/reports/general-ledger", category: "Financial" },
  { id: "PL", name: "Profit & Loss", href: "/reports/profit-and-loss", category: "Financial" },
  { id: "FIN_CMP", name: "Comparative P&L (12 months)", href: "/reports/comparative-profit-and-loss", category: "Financial" },
  { id: "FIN_MTB", name: "Monthly Income vs Expense", href: "/reports/extended/financial-monthly-balances", category: "Financial" },
  { id: "FIN_TB12", name: "Trial Balance by Month", href: "/reports/extended/financial-trial-balance-by-month", category: "Financial" },
  { id: "FIN_PNL_CAT", name: "Comparative P&L by category", href: "/reports/comparative-pnl-by-category", category: "Financial" },
  { id: "BS", name: "Balance Sheet", href: "/reports/balance-sheet", category: "Financial" },
  {
    id: "BUDGET_VS_ACTUAL",
    name: "Budget vs Actual",
    href: "/reports/budget-vs-actual",
    category: "Financial",
  },
  { id: "ARA", name: "AR Aging", href: "/reports/ar-aging", category: "Accounts Receivable" },
  { id: "047", name: "Customer Balances", href: "/reports/extended/customer-balances", category: "Accounts Receivable" },
  { id: "CST", name: "Customer Statement", href: "/reports/customer-statement", category: "Accounts Receivable" },
  { id: "APA", name: "AP Aging", href: "/reports/ap-aging", category: "Accounts Payable" },
  { id: "067", name: "Supplier Balances", href: "/reports/extended/supplier-balances", category: "Accounts Payable" },
  { id: "SST", name: "Supplier Statement", href: "/reports/supplier-statement", category: "Accounts Payable" },
  { id: "SID", name: "Sale Invoices by Date", href: "/reports/extended/sale-invoices-by-date", category: "Sales" },
  { id: "SIC", name: "Sale Invoices by Customer", href: "/reports/extended/sale-invoices-by-customer", category: "Sales" },
  { id: "SSD", name: "Sale Summary by Date", href: "/reports/extended/sale-summary-by-date", category: "Sales" },
  { id: "033", name: "Sale Summary by Customer", href: "/reports/extended/sale-summary-by-customer", category: "Sales" },
  { id: "030", name: "Sale Invoice Line Detail", href: "/reports/extended/invoice-line-detail", category: "Sales" },
  { id: "031", name: "Sale Invoice Line by Customer", href: "/reports/extended/invoice-line-by-customer", category: "Sales" },
  { id: "035", name: "Customer List", href: "/reports/extended/customer-list", category: "Sales" },
  { id: "143", name: "Customer Outstanding Items", href: "/reports/extended/customer-outstanding", category: "Sales" },
  { id: "145", name: "Customer Products", href: "/reports/extended/customer-products", category: "Sales" },
  { id: "CP", name: "Customer Performance", href: "/reports/extended/customer-performance", category: "Sales" },
  { id: "PSD", name: "Product Sale Detail", href: "/reports/extended/product-sale-detail", category: "Sales" },
  { id: "088", name: "Product Sale Summary", href: "/reports/extended/product-sale-summary", category: "Sales" },
  { id: "PPD", name: "Product Purchase Detail", href: "/reports/extended/product-purchase-detail", category: "Purchases" },
  { id: "089", name: "Product Purchase Summary", href: "/reports/extended/product-purchase-summary", category: "Purchases" },
  { id: "PBD", name: "Purchase Bills by Date", href: "/reports/extended/purchase-bills-by-date", category: "Purchases" },
  { id: "PBS", name: "Purchase Bills by Supplier", href: "/reports/extended/purchase-bills-by-supplier", category: "Purchases" },
  { id: "BANK_BAL", name: "Bank Account Balances", href: "/reports/extended/bank-account-balances", category: "Bank & Assembly" },
  { id: "BANK_CF", name: "Bank Cash Flow (Monthly)", href: "/reports/extended/bank-cash-flow-monthly", category: "Bank & Assembly" },
  { id: "BPL", name: "Bank Payments List", href: "/reports/extended/bank-payments-list", category: "Bank & Assembly" },
  { id: "BANK_REC", name: "Bank Receipts List", href: "/reports/extended/bank-receipts-list", category: "Bank & Assembly" },
  { id: "BANK_XFR", name: "Bank Transfers List", href: "/reports/extended/bank-transfers-list", category: "Bank & Assembly" },
  { id: "BANK_ACT", name: "Bank Activity Summary", href: "/reports/extended/bank-activity-summary", category: "Bank & Assembly" },
  { id: "300", name: "Bank Payment & Receipt Data", href: "/reports/extended/bank-payment-receipt-data", category: "Bank & Assembly" },
  { id: "ASM_JOB", name: "Assembly Job Cost Summary", href: "/reports/extended/assembly-job-cost-summary", category: "Bank & Assembly" },
  { id: "ASM_TPL", name: "Assembly Templates", href: "/reports/extended/assembly-templates", category: "Bank & Assembly" },
  { id: "ASM_WIP", name: "Assembly WIP Jobs", href: "/reports/extended/assembly-wip", category: "Bank & Assembly" },
  { id: "ASM_COMP", name: "Assembly Component Cost", href: "/reports/extended/assembly-component-cost", category: "Bank & Assembly" },
  { id: "PRJ_PAY", name: "Project Payments", href: "/reports/extended/project-payments", category: "Bank & Assembly" },
  { id: "SQ", name: "Stock Quantity", href: "/reports/extended/stock-quantity", category: "Inventory" },
  { id: "OOS", name: "Out of Stock", href: "/reports/extended/out-of-stock", category: "Inventory" },
  { id: "083", name: "Low Stock", href: "/reports/extended/low-stock", category: "Inventory" },
  { id: "148", name: "Stock Valuation", href: "/reports/extended/stock-valuation", category: "Inventory" },
  { id: "174", name: "Stock Movement", href: "/reports/extended/stock-movement", category: "Inventory" },
  { id: "079", name: "Price List", href: "/reports/extended/price-list", category: "Inventory" },
  { id: "078", name: "Products List", href: "/reports/extended/products-list", category: "Inventory" },
  { id: "081", name: "Product Activity", href: "/reports/extended/product-activity-summary", category: "Inventory" },
  { id: "149", name: "Product Activity Summary", href: "/reports/extended/product-activity-summary", category: "Inventory" },
  { id: "162", name: "Product Performance", href: "/reports/extended/product-performance", category: "Inventory" },
  { id: "206", name: "Stock Transfer Detail", href: "/reports/extended/stock-transfer-detail", category: "Inventory" },
  { id: "GRNI", name: "GRNI (Goods Received Not Invoiced)", href: "/reports/grni", category: "Inventory" },
  { id: "175", name: "Advanced Stock Quantity", href: "/reports/extended/advanced-stock-quantity", category: "Inventory" },
  { id: "181", name: "Multi-Unit Price List", href: "/reports/extended/multi-unit-price-list", category: "Inventory" },
  { id: "185", name: "Sale Summary by Field", href: "/reports/extended/sale-summary-by-field", category: "Inventory" },
  { id: "311", name: "Customer Field Activity", href: "/reports/extended/customer-field-activity", category: "Inventory" },
];

export const reportCatalogByCategory = reportCatalog.reduce(
  (acc, item) => {
    if (!acc[item.category]) acc[item.category] = [];
    acc[item.category].push(item);
    return acc;
  },
  {} as Record<string, ReportCatalogItem[]>,
);
