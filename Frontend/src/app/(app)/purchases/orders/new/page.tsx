/** New purchase order — catalog §6.2. */
"use client";

import { LineGridForm } from "@/components/app/line-grid-form";
import { purchaseOrdersApi } from "@/lib/api/tenant";

export default function NewPurchaseOrderPage() {
  return (
    <LineGridForm
      title="New purchase order"
      breadcrumb="Buy / Purchase orders / New"
      description="Created in_progress (§6.2). No GL impact until billed."
      partyKind="supplier"
      dateLabel="Order date"
      cancelHref="/purchases/orders"
      successHref="/purchases/orders"
      draftStorageKey="purchase-order-new"
      withGst
      descriptionDocType="PO"
      lastRateDocType="PO"
      saveLabel="Save order"
      detailPath={(id) => `/purchases/orders/${id}`}
      onSubmit={({ dateISO, partyId, lines }) =>
        purchaseOrdersApi.create({
          orderDate: dateISO,
          supplierId: partyId,
          lines,
        })
      }
    />
  );
}
