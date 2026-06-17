/** Supplier credit detail — catalog §6.3. */
"use client";

import { useParams } from "next/navigation";

import { DocumentDetail } from "@/components/app/document-detail";
import { useSupplierNameMap } from "@/lib/hooks/use-party-name-map";
import { supplierCreditsApi } from "@/lib/api/tenant";

export default function SupplierCreditDetailPage() {
  const params = useParams<{ id: string }>();
  const supplierNames = useSupplierNameMap();
  return (
    <DocumentDetail
      docLabel="Supplier credit"
      breadcrumb="Buy / Credits / Detail"
      partyLabel="Supplier"
      resolvePartyName={(d) => supplierNames.get(d.supplierId) ?? d.supplierId}
      listHref="/purchases/credits"
      statuses={["posted", "void"]}
      detailQueryKey={["supplier-credit", params.id]}
      fetchDetail={() => supplierCreditsApi.get(params.id)}
      projectHeader={(d) => ({
        id: d.id,
        number: d.creditNumber,
        date: d.creditDate,
        partyId: d.supplierId,
        status: d.status,
        totalAmount: d.totalAmount,
      })}
      showGst
      printHref={`/print/supplier-credits/${params.id}`}
      attachmentEntityType="supplier_credit"
    />
  );
}
