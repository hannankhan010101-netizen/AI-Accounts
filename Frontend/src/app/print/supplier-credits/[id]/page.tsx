"use client";

import { PlanningDocumentPrint } from "@/components/print/planning-document-print";
import { supplierCreditsApi } from "@/lib/api/tenant";

export default function SupplierCreditPrintPage() {
  return (
    <PlanningDocumentPrint
      title="Supplier Credit"
      partyLabel="Supplier"
      templateCode="vc"
      queryKey="print-supplier-credit"
      partyMode="supplier"
      fetchDetail={(id) => supplierCreditsApi.get(id)}
      mapDoc={(d) => ({
        documentNumber: d.creditNumber,
        documentDate: d.creditDate,
        partyId: d.supplierId,
        lines: d.lines,
        totalAmount: d.totalAmount,
      })}
    />
  );
}
