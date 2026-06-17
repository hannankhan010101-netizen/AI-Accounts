/** Sales receipt detail with allocation picker — P9. */
"use client";

import { useParams } from "next/navigation";

import { SettlementDetail } from "@/components/patterns/settlement-detail";
import { useInvoiceNumberMap } from "@/lib/hooks/use-document-number-map";
import { useBankAccountNameMap } from "@/lib/hooks/use-bank-account-name-map";
import { useCustomerNameMap } from "@/lib/hooks/use-party-name-map";
import { salesApi } from "@/lib/api/tenant";

export default function SalesReceiptDetailPage() {
  const params = useParams<{ id: string }>();
  const customerNames = useCustomerNameMap();
  const bankNames = useBankAccountNameMap();
  const invoiceNumbers = useInvoiceNumberMap();

  return (
    <SettlementDetail
      docLabel="Receipt"
      breadcrumb="Sell / Receipts / Detail"
      listHref="/sales/receipts"
      settlementId={params.id}
      queryKey={["sales-receipt", params.id]}
      fetchDetail={() => salesApi.getReceipt(params.id)}
      mapAllocation={(a) => ({
        id: a.id,
        documentId: a.salesInvoiceId ?? "",
        amount: a.amount,
      })}
      partyLabel="Customer"
      resolvePartyName={(d) => customerNames.get(d.customerId ?? "") ?? d.customerId ?? "—"}
      resolveBankName={(d) => bankNames.get(d.bankAccountId) ?? d.bankAccountId}
      resolvePartyId={(d) => d.customerId ?? ""}
      pickerMode="customer"
      documentLinkPrefix="/sales/invoices"
      documentColumnHeader="Invoice"
      resolveDocumentLabel={(id) => invoiceNumbers.get(id) ?? id}
      allocate={(id, body) => salesApi.allocateReceipt(id, body)}
      printHref={`/print/sales-receipt/${params.id}`}
      attachmentEntityType="sales_receipt"
      returnAdvanceHref={`/sales/receipts/${params.id}/return-advance`}
      postToGl={(id) => salesApi.postReceipt(id)}
    />
  );
}
