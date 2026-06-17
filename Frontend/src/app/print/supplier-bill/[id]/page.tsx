/** Supplier Bill print view — catalog §3.7 VI template. */
"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { DocumentPrint } from "@/components/print/document-print";
import { PrintQueryShell } from "@/components/print/print-query-shell";
import { partiesApi, purchasesApi } from "@/lib/api/tenant";
import { useBusinessPrintHeader } from "@/lib/hooks/use-business-print";
import { usePrintTemplate } from "@/lib/hooks/use-print-template";

export default function SupplierBillPrintPage() {
  const params = useParams<{ id: string }>();
  const biz = useBusinessPrintHeader();
  const templateQuery = usePrintTemplate("vi");

  const billQuery = useTenantListQuery(["print-supplier-bill", params.id], () => purchasesApi.getSupplierBill(params.id),
    { enabled: !!params.id,
    retry: false });
  const suppliersQuery = useTenantListQuery(["suppliers"], () => partiesApi.listSuppliers());

  const bill = billQuery.data?.result;
  const supplier = bill
    ? suppliersQuery.data?.result.find((s) => s.id === bill.supplierId)
    : undefined;

  return (
    <PrintQueryShell
      isLoading={
        billQuery.isLoading ||
        suppliersQuery.isLoading ||
        biz.isLoading ||
        templateQuery.isLoading
      }
      error={billQuery.error}
      ready={Boolean(bill)}
      notFoundMessage="Bill not found."
    >
      {bill ? (
        <DocumentPrint
          title="Supplier Bill"
          documentNumber={String(bill.documentNumber ?? bill.id.slice(0, 8))}
          documentDate={bill.billDate}
          businessName={biz.businessName}
          businessAddress={biz.businessAddress}
          businessLogoUrl={biz.businessLogoUrl}
          party={{
            label: "Bill from",
            name: supplier?.name ?? null,
            code: supplier?.code ?? null,
          }}
          lines={bill.lines.map((l) => ({
            productCode: l.productCode,
            description: null,
            quantity: l.quantity,
            rate: l.rate,
            gstCode: l.gstCode,
            taxAmount: l.taxAmount,
            lineTotal: l.lineTotal,
          }))}
          total={bill.totalAmount}
          template={templateQuery.data?.result}
        />
      ) : null}
    </PrintQueryShell>
  );
}
