/** Supplier payment detail with bill allocations — §6.4. */
"use client";

import { useParams } from "next/navigation";

import { SettlementDetail } from "@/components/patterns/settlement-detail";
import { useBillNumberMap } from "@/lib/hooks/use-document-number-map";
import { useBankAccountNameMap } from "@/lib/hooks/use-bank-account-name-map";
import { useSupplierNameMap } from "@/lib/hooks/use-party-name-map";
import { purchasesApi } from "@/lib/api/tenant";

export default function SupplierPaymentDetailPage() {
  const params = useParams<{ id: string }>();
  const supplierNames = useSupplierNameMap();
  const bankNames = useBankAccountNameMap();
  const billNumbers = useBillNumberMap();

  return (
    <SettlementDetail
      docLabel="Payment"
      breadcrumb="Buy / Payments / Detail"
      listHref="/purchases/payments"
      settlementId={params.id}
      queryKey={["supplier-payment", params.id]}
      fetchDetail={() => purchasesApi.getSupplierPayment(params.id)}
      mapAllocation={(a) => ({
        id: a.id,
        documentId: a.supplierBillId ?? "",
        amount: a.amount,
      })}
      partyLabel="Supplier"
      resolvePartyName={(d) => supplierNames.get(d.supplierId ?? "") ?? d.supplierId ?? "—"}
      resolveBankName={(d) => bankNames.get(d.bankAccountId) ?? d.bankAccountId}
      resolvePartyId={(d) => d.supplierId ?? ""}
      pickerMode="supplier"
      documentLinkPrefix="/purchases/bills"
      documentColumnHeader="Bill"
      resolveDocumentLabel={(id) => billNumbers.get(id) ?? id}
      allocate={(id, body) => purchasesApi.allocateSupplierPayment(id, body)}
      printHref={`/print/supplier-payment/${params.id}`}
      attachmentEntityType="supplier_payment"
      returnAdvanceHref={`/purchases/payments/${params.id}/return-advance`}
      postToGl={(id) => purchasesApi.postSupplierPayment(id)}
    />
  );
}
