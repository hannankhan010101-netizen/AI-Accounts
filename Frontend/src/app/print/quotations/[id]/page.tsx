"use client";

import { PlanningDocumentPrint } from "@/components/print/planning-document-print";
import { quotationsApi } from "@/lib/api/tenant";

export default function QuotationPrintPage() {
  return (
    <PlanningDocumentPrint
      title="Quotation"
      partyLabel="Customer"
      templateCode="so"
      queryKey="print-quotation"
      partyMode="customer"
      fetchDetail={(id) => quotationsApi.get(id)}
      mapDoc={(d) => ({
        documentNumber: d.quotationNumber,
        documentDate: d.quotationDate,
        partyId: d.customerId,
        lines: d.lines,
        totalAmount: d.totalAmount,
      })}
    />
  );
}
