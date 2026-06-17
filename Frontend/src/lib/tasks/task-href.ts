/** Deep links for My Tasks rows. */

const TASK_HREF: Record<string, (id: string) => string> = {
  sales_invoice: (id) => `/sales/invoices/${id}`,
  supplier_bill: (id) => `/purchases/bills/${id}`,
  sales_credit: (id) => `/sales/credits/${id}`,
  supplier_credit: (id) => `/purchases/credits/${id}`,
  quotation: (id) => `/sales/quotations/${id}`,
  sales_order: (id) => `/sales/orders/${id}`,
  purchase_order: (id) => `/purchases/orders/${id}`,
  journal: (id) => `/settings/journals/${id}`,
};

export function taskHref(entityType: string, entityId: string): string {
  const fn = TASK_HREF[entityType];
  return fn ? fn(entityId) : "/my-tasks";
}
