/** Sales Invoice print view — catalog §3.7 SI template. */
"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { DocumentPrint } from "@/components/print/document-print";
import { PrintQueryShell } from "@/components/print/print-query-shell";
import { partiesApi, salesApi } from "@/lib/api/tenant";
import { useBusinessPrintHeader } from "@/lib/hooks/use-business-print";
import { usePrintTemplate } from "@/lib/hooks/use-print-template";

export default function SalesInvoicePrintPage() {
  const params = useParams<{ id: string }>();
  const biz = useBusinessPrintHeader();
  const templateQuery = usePrintTemplate("si");

  const invoiceQuery = useTenantListQuery(["print-sales-invoice", params.id], () => salesApi.getInvoice(params.id),
    { enabled: !!params.id,
    retry: false });
  const customersQuery = useTenantListQuery(["customers"], () => partiesApi.listCustomers());

  const inv = invoiceQuery.data?.result;
  const customer = customersQuery.data?.result.find((c) => c.id === inv?.customerId);

  return (
    <PrintQueryShell
      isLoading={
        invoiceQuery.isLoading ||
        customersQuery.isLoading ||
        biz.isLoading ||
        templateQuery.isLoading
      }
      error={invoiceQuery.error}
      ready={Boolean(inv)}
      notFoundMessage="Invoice not found."
    >
      {inv ? (
        <DocumentPrint
          title="Sales Invoice"
          documentNumber={String(inv.documentNumber ?? inv.id.slice(0, 8))}
          documentDate={inv.invoiceDate}
          businessName={biz.businessName}
          businessAddress={biz.businessAddress}
          businessLogoUrl={biz.businessLogoUrl}
          party={{
            label: "Bill to",
            name: customer?.name ?? null,
            code: customer?.code ?? null,
            addressLines: customer?.phone ? [`Phone: ${customer.phone}`] : [],
          }}
          lines={inv.lines.map((l) => ({
            productCode: l.productCode,
            description: (l.description as string | null | undefined) ?? null,
            quantity: l.quantity,
            rate: l.rate,
            gstCode: l.gstCode,
            taxAmount: l.taxAmount,
            lineTotal: l.lineTotal,
          }))}
          total={inv.totalAmount}
          template={templateQuery.data?.result}
        />
      ) : null}
    </PrintQueryShell>
  );
}
