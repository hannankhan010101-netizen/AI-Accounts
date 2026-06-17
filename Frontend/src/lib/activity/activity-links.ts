import type { ActivityRow } from "@/lib/api/tenant";



/** Deep link from unified activity row to the correct detail screen. */

export function activityDetailHref(row: ActivityRow): string {

  switch (row.entityType) {

    case "invoice":

      return `/sales/invoices/${row.entityId}`;

    case "receipt":

      return `/sales/receipts/${row.entityId}`;

    case "credit":

      return row.partyKind === "customer"

        ? `/sales/credits/${row.entityId}`

        : `/purchases/credits/${row.entityId}`;

    case "quotation":

      return `/sales/quotations/${row.entityId}`;

    case "sales_order":

      return `/sales/orders/${row.entityId}`;

    case "pdc_received":

      return `/sales/pdc-received/${row.entityId}`;

    case "delivery_note":

      return `/sales/delivery-notes/${row.entityId}`;

    case "bill":

      return `/purchases/bills/${row.entityId}`;

    case "payment":

      return `/purchases/payments/${row.entityId}`;

    case "purchase_order":

      return `/purchases/orders/${row.entityId}`;

    case "pdc_issued":

      return `/purchases/pdc-issued/${row.entityId}`;

    case "grn":

      return `/purchases/grn/${row.entityId}`;

    default:

      return "#";

  }

}

