/** Sales credit detail — catalog §5.5. */
"use client";

import { useParams } from "next/navigation";

import { DocumentDetail } from "@/components/app/document-detail";
import { useCustomerNameMap } from "@/lib/hooks/use-party-name-map";
import { salesCreditsApi } from "@/lib/api/tenant";

export default function SalesCreditDetailPage() {
  const params = useParams<{ id: string }>();
  const customerNames = useCustomerNameMap();
  return (
    <DocumentDetail
      docLabel="Sales credit"
      breadcrumb="Sell / Credits / Detail"
      partyLabel="Customer"
      resolvePartyName={(d) => customerNames.get(d.customerId) ?? d.customerId}
      listHref="/sales/credits"
      statuses={["posted", "void"]}
      detailQueryKey={["sales-credit", params.id]}
      fetchDetail={() => salesCreditsApi.get(params.id)}
      projectHeader={(d) => ({
        id: d.id,
        number: d.creditNumber,
        date: d.creditDate,
        partyId: d.customerId,
        status: d.status,
        totalAmount: d.totalAmount,
      })}
      showGst
      printHref={`/print/sales-credits/${params.id}`}
      attachmentEntityType="sales_credit"
    />
  );
}
