/** New sales order — catalog §5.3. */
"use client";

import { LineGridForm } from "@/components/app/line-grid-form";
import { salesOrdersApi } from "@/lib/api/tenant";

export default function NewSalesOrderPage() {
  return (
    <LineGridForm
      title="New sales order"
      breadcrumb="Sell / Orders / New"
      description="Created in_progress (§5.3). Use the status action on the detail page to approve/reject/invoice."
      partyKind="customer"
      dateLabel="Order date"
      cancelHref="/sales/orders"
      successHref="/sales/orders"
      draftStorageKey="sales-order-new"
      withGst
      descriptionDocType="SO"
      lastRateDocType="SO"
      saveLabel="Save order"
      detailPath={(id) => `/sales/orders/${id}`}
      onSubmit={({ dateISO, partyId, lines }) =>
        salesOrdersApi.create({
          orderDate: dateISO,
          customerId: partyId,
          lines,
        })
      }
    />
  );
}
