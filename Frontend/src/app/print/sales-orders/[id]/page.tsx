"use client";

import { PlanningDocumentPrint } from "@/components/print/planning-document-print";
import { salesOrdersApi } from "@/lib/api/tenant";

export default function SalesOrderPrintPage() {
  return (
    <PlanningDocumentPrint
      title="Sales Order"
      partyLabel="Customer"
      templateCode="so"
      queryKey="print-sales-order"
      partyMode="customer"
      fetchDetail={(id) => salesOrdersApi.get(id)}
      mapDoc={(d) => ({
        documentNumber: d.orderNumber,
        documentDate: d.orderDate,
        partyId: d.customerId,
        lines: d.lines,
        totalAmount: d.totalAmount,
      })}
    />
  );
}
