/** Quotation detail — catalog §5.2 with status + convert-to-order. */
"use client";

import { useParams } from "next/navigation";

import { DocumentDetail } from "@/components/app/document-detail";
import { useCustomerNameMap } from "@/lib/hooks/use-party-name-map";
import { quotationsApi } from "@/lib/api/tenant";

const QUOTATION_STATUSES = ["draft", "approved", "rejected", "accepted", "converted"];
const CONVERTIBLE = ["draft", "approved", "accepted"];

export default function QuotationDetailPage() {
  const params = useParams<{ id: string }>();
  const customerNames = useCustomerNameMap();
  return (
    <DocumentDetail
      docLabel="Quotation"
      breadcrumb="Sell / Quotations / Detail"
      partyLabel="Customer"
      resolvePartyName={(d) => customerNames.get(d.customerId) ?? d.customerId}
      listHref="/sales/quotations"
      statuses={QUOTATION_STATUSES}
      convertLabel="Convert to sales order"
      convertSuccessHref="/sales/orders"
      convertibleStatuses={CONVERTIBLE}
      detailQueryKey={["quotation", params.id]}
      fetchDetail={() => quotationsApi.get(params.id)}
      projectHeader={(d) => ({
        id: d.id,
        number: d.quotationNumber,
        date: d.quotationDate,
        partyId: d.customerId,
        status: d.status,
        totalAmount: d.totalAmount,
      })}
      setStatus={(status) => quotationsApi.setStatus(params.id, status)}
      convert={() => quotationsApi.convertToOrder(params.id)}
      showGst
      descriptionDocType="SQ"
      resolveLastRateContext={(d) => ({
        docType: "QO",
        partyKind: "customer",
        partyId: d.customerId,
      })}
      printHref={`/print/quotations/${params.id}`}
      attachmentEntityType="sales_quotation"
    />
  );
}
