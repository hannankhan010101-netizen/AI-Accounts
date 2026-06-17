/**

 * FastAccounts report IDs → live AI-Accounts routes.

 * Unmapped IDs use the generic synchronous runner at /reports/run/{id}.

 */



export type ReportHrefContext = {

  category?: string;

};



const DEDICATED_ROUTES: Record<string, string> = {

  TB: "/reports/trial-balance",

  "203": "/reports/trial-balance",

  PNL: "/reports/profit-and-loss",

  PL: "/reports/profit-and-loss",

  "204": "/reports/profit-and-loss",

  BS: "/reports/balance-sheet",

  "205": "/reports/balance-sheet",

  GL: "/reports/general-ledger",

  "206": "/reports/extended/stock-transfer-detail",

  STOCK_XFR: "/reports/extended/stock-transfer-detail",

  FIN_CMP: "/reports/comparative-profit-and-loss",

  "209": "/reports/comparative-profit-and-loss",

  FIN_MTB: "/reports/extended/financial-monthly-balances",

  "210": "/reports/extended/financial-monthly-balances",

  FIN_TB12: "/reports/extended/financial-trial-balance-by-month",

  "208": "/reports/extended/financial-trial-balance-by-month",

  FIN_PNL_CAT: "/reports/comparative-pnl-by-category",

  "207": "/reports/comparative-pnl-by-category",

  ARA: "/reports/ar-aging",

  AR_AGING: "/reports/ar-aging",

  "047": "/reports/extended/customer-balances",

  CUST_BAL: "/reports/extended/customer-balances",

  APA: "/reports/ap-aging",

  AP_AGING: "/reports/ap-aging",

  "067": "/reports/extended/supplier-balances",

  SUPP_BAL: "/reports/extended/supplier-balances",

  BUDGET_VS_ACTUAL: "/reports/budget-vs-actual",

  CST: "/reports/customer-statement",

  "034": "/reports/customer-statement",

  "160": "/reports/customer-statement",

  "243": "/reports/customer-statement",

  "246": "/reports/customer-statement",

  SST: "/reports/supplier-statement",

  "054": "/reports/supplier-statement",

  "028": "/reports/extended/sale-invoices-by-date",

  SID: "/reports/extended/sale-invoices-by-date",

  "141": "/reports/extended/sale-invoices-by-date",

  "029": "/reports/extended/sale-invoices-by-customer",

  SIC: "/reports/extended/sale-invoices-by-customer",

  "142": "/reports/extended/sale-invoices-by-customer",

  "032": "/reports/extended/sale-summary-by-date",

  SSD: "/reports/extended/sale-summary-by-date",

  "033": "/reports/extended/sale-summary-by-customer",

  SSC: "/reports/extended/sale-summary-by-customer",

  "030": "/reports/extended/invoice-line-detail",

  "144": "/reports/extended/invoice-line-detail",

  "240": "/reports/extended/invoice-line-detail",

  "245": "/reports/extended/invoice-line-detail",

  SID_DETAIL: "/reports/extended/invoice-line-detail",

  "031": "/reports/extended/invoice-line-by-customer",

  "178": "/reports/extended/invoice-line-by-customer",

  "241": "/reports/extended/invoice-line-by-customer",

  SIC_DETAIL: "/reports/extended/invoice-line-by-customer",

  "035": "/reports/extended/customer-list",

  CLIST: "/reports/extended/customer-list",

  "143": "/reports/extended/customer-outstanding",

  CUST_OUT: "/reports/extended/customer-outstanding",

  "145": "/reports/extended/customer-products",

  CUST_PROD: "/reports/extended/customer-products",

  "182": "/reports/extended/customer-performance",

  CP: "/reports/extended/customer-performance",

  "048": "/reports/extended/purchase-bills-by-date",

  "272": "/reports/extended/purchase-bills-by-date",

  PBD: "/reports/extended/purchase-bills-by-date",

  "238": "/reports/extended/purchase-bills-by-date",

  "051": "/reports/extended/purchase-bills-by-supplier",

  PBS: "/reports/extended/purchase-bills-by-supplier",

  "085": "/reports/extended/product-sale-detail",

  "084": "/reports/extended/product-sale-detail",

  PSD: "/reports/extended/product-sale-detail",

  "088": "/reports/extended/product-sale-summary",

  "087": "/reports/extended/product-purchase-detail",

  "086": "/reports/extended/product-purchase-detail",

  PPD: "/reports/extended/product-purchase-detail",

  "089": "/reports/extended/product-purchase-summary",

  "078": "/reports/extended/products-list",

  "162": "/reports/extended/product-performance",

  "081": "/reports/extended/product-activity-summary",

  "149": "/reports/extended/product-activity-summary",

  PROD_ACT: "/reports/extended/product-activity-summary",

  "080": "/reports/extended/stock-quantity",

  "164": "/reports/extended/stock-quantity",

  "173": "/reports/extended/stock-quantity",

  SQ: "/reports/extended/stock-quantity",

  "082": "/reports/extended/out-of-stock",

  OOS: "/reports/extended/out-of-stock",

  "083": "/reports/extended/low-stock",

  LOW_STOCK: "/reports/extended/low-stock",

  "071": "/reports/extended/bank-payments-list",

  "300": "/reports/extended/bank-payment-receipt-data",

  "475": "/reports/extended/bank-payment-receipt-data",

  "477": "/reports/extended/bank-payment-receipt-data",

  BPL: "/reports/extended/bank-payments-list",

  "072": "/reports/extended/bank-receipts-list",

  BANK_REC: "/reports/extended/bank-receipts-list",

  "073": "/reports/extended/bank-account-balances",

  BANK_BAL: "/reports/extended/bank-account-balances",

  "074": "/reports/extended/bank-activity-summary",

  BANK_ACT: "/reports/extended/bank-activity-summary",

  "076": "/reports/extended/bank-transfers-list",

  BANK_XFR: "/reports/extended/bank-transfers-list",

  "077": "/reports/extended/bank-cash-flow-monthly",

  BANK_CF: "/reports/extended/bank-cash-flow-monthly",

  "175": "/reports/extended/advanced-stock-quantity",

  "181": "/reports/extended/multi-unit-price-list",

  "079": "/reports/extended/price-list",

  PLIST: "/reports/extended/price-list",

  "148": "/reports/extended/stock-valuation",

  STOCK_VAL: "/reports/extended/stock-valuation",

  "174": "/reports/extended/stock-movement",

  STOCK_MOV: "/reports/extended/stock-movement",

  GRNI: "/reports/grni",

  "185": "/reports/extended/sale-summary-by-field",

  "311": "/reports/extended/customer-field-activity",

  ASM_JOB: "/reports/extended/assembly-job-cost-summary",

  "201": "/reports/extended/assembly-job-cost-summary",

  ASM_TPL: "/reports/extended/assembly-templates",

  ASM_WIP: "/reports/extended/assembly-wip",

  "202": "/reports/extended/assembly-wip",

  ASM_COMP: "/reports/extended/assembly-component-cost",

  PRJ_PAY: "/reports/extended/project-payments",

};



/** FA reuses numeric ID 206 for GL (Financial) and stock transfers (Inventory). */

const CATEGORY_ROUTE_OVERRIDES: Record<string, Record<string, string>> = {

  Financial: { "206": "/reports/general-ledger" },

};



function resolveDedicatedRoute(reportId: string, context?: ReportHrefContext): string | undefined {

  const category = context?.category?.trim();

  if (category && CATEGORY_ROUTE_OVERRIDES[category]?.[reportId]) {

    return CATEGORY_ROUTE_OVERRIDES[category][reportId];

  }

  return DEDICATED_ROUTES[reportId];

}



/** Resolve navigable href for any catalog report ID. */

export function reportIdHref(reportId: string, context?: ReportHrefContext): string {

  const hit = resolveDedicatedRoute(reportId, context);

  if (hit) return hit;

  return `/reports/run/${encodeURIComponent(reportId)}`;

}



/** @deprecated Use reportIdHref — kept for analytical hub imports. */

export function analyticalReportHref(reportId: string, context?: ReportHrefContext): string {

  return reportIdHref(reportId, context);

}



/** True when the report uses the generic runner (not a dedicated page). */

export function isGenericReportRunner(reportId: string, context?: ReportHrefContext): boolean {

  return reportIdHref(reportId, context).startsWith("/reports/run/");

}


