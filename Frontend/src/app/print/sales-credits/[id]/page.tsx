"use client";

import { PlanningDocumentPrint } from "@/components/print/planning-document-print";
import { salesCreditsApi } from "@/lib/api/tenant";

export default function SalesCreditPrintPage() {
  return (
    <PlanningDocumentPrint
      title="Sales Credit"
      partyLabel="Customer"
      templateCode="sc"
      queryKey="print-sales-credit"
      partyMode="customer"
      fetchDetail={(id) => salesCreditsApi.get(id)}
      mapDoc={(d) => ({
        documentNumber: d.creditNumber,
        documentDate: d.creditDate,
        partyId: d.customerId,
        lines: d.lines,
        totalAmount: d.totalAmount,
      })}
    />
  );
}
