/** Maps routes to suggested tour ids for "Tour this page". */

const ROUTE_TOURS: Record<string, string[]> = {
  "/dashboard": ["onboard.core"],
  "/sales/invoices": ["onboard.sell", "workflow.sales-invoice"],
  "/sales/invoices/new": ["workflow.sales-invoice"],
  "/sales/receipts": ["onboard.sell", "workflow.sales-receipt"],
  "/sales/receipts/new": ["workflow.sales-receipt"],
  "/sales/all": ["onboard.sell"],
  "/purchases/bills": ["onboard.buy", "workflow.supplier-bill"],
  "/purchases/bills/new": ["workflow.supplier-bill"],
  "/purchases/payments": ["onboard.buy", "workflow.supplier-payment"],
  "/purchases/payments/new": ["workflow.supplier-payment"],
  "/purchases/all": ["onboard.buy"],
  "/settings/journals": ["workflow.journal"],
  "/settings/journals/new": ["workflow.journal"],
  "/bank/receipts": ["workflow.bank-receipt"],
  "/bank/receipts/new": ["workflow.bank-receipt"],
  "/bank/payments": ["workflow.bank-payment"],
  "/bank/payments/new": ["workflow.bank-payment"],
  "/bank/balances": ["onboard.money"],
  "/bank/reconciliation": ["onboard.money"],
  "/bank/import-statement": ["onboard.money"],
  "/settings/users": ["onboard.admin"],
  "/inventory/products": ["onboard.stock"],
  "/inventory/add": ["onboard.stock"],
  "/reports": ["onboard.reports"],
  "/reports/analytical": ["onboard.reports"],
};

export function toursForPath(pathname: string): string[] {
  if (ROUTE_TOURS[pathname]) return ROUTE_TOURS[pathname];
  for (const [prefix, ids] of Object.entries(ROUTE_TOURS)) {
    if (prefix !== "/" && pathname.startsWith(prefix)) return ids;
  }
  return [];
}
