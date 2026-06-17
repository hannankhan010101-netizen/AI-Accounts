"use client";

import { PlanningDocumentPrint } from "@/components/print/planning-document-print";
import { purchaseOrdersApi } from "@/lib/api/tenant";

export default function PurchaseOrderPrintPage() {
  return (
    <PlanningDocumentPrint
      title="Purchase Order"
      partyLabel="Supplier"
      templateCode="po"
      queryKey="print-purchase-order"
      partyMode="supplier"
      fetchDetail={(id) => purchaseOrdersApi.get(id)}
      mapDoc={(d) => ({
        documentNumber: d.orderNumber,
        documentDate: d.orderDate,
        partyId: d.supplierId,
        lines: d.lines,
        totalAmount: d.totalAmount,
      })}
    />
  );
}
