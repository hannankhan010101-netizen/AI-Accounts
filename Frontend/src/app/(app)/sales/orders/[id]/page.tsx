/** Sales order detail — catalog §5.3 with status + convert-to-invoice. */
"use client";

import { useParams } from "next/navigation";

import { DocumentDetail } from "@/components/app/document-detail";
import { useCustomerNameMap } from "@/lib/hooks/use-party-name-map";
import { salesOrdersApi } from "@/lib/api/tenant";

const SO_STATUSES = ["in_progress", "approved", "rejected", "invoiced"];
const CONVERTIBLE = ["in_progress", "approved"];

export default function SalesOrderDetailPage() {
  const params = useParams<{ id: string }>();
  const customerNames = useCustomerNameMap();
  return (
    <DocumentDetail
      docLabel="Sales order"
      breadcrumb="Sell / Orders / Detail"
      partyLabel="Customer"
      resolvePartyName={(d) => customerNames.get(d.customerId) ?? d.customerId}
      listHref="/sales/orders"
      statuses={SO_STATUSES}
      convertLabel="Convert to invoice"
      convertSuccessHref="/sales/invoices"
      convertibleStatuses={CONVERTIBLE}
      detailQueryKey={["sales-order", params.id]}
      fetchDetail={() => salesOrdersApi.get(params.id)}
      projectHeader={(d) => ({
        id: d.id,
        number: d.orderNumber,
        date: d.orderDate,
        partyId: d.customerId,
        status: d.status,
        totalAmount: d.totalAmount,
      })}
      setStatus={(status) => salesOrdersApi.setStatus(params.id, status)}
      convert={() => salesOrdersApi.convertToInvoice(params.id)}
      showGst
      descriptionDocType="SO"
      resolveLastRateContext={(d) => ({
        docType: "SO",
        partyKind: "customer",
        partyId: d.customerId,
      })}
      printHref={`/print/sales-orders/${params.id}`}
      attachmentEntityType="sales_order"
    />
  );
}
