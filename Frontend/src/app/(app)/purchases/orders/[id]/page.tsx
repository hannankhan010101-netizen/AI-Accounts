/** Purchase order detail — catalog §6.2 with status + convert-to-bill. */
"use client";

import { useParams } from "next/navigation";

import { DocumentDetail } from "@/components/app/document-detail";
import { useSupplierNameMap } from "@/lib/hooks/use-party-name-map";
import { purchaseOrdersApi } from "@/lib/api/tenant";

const PO_STATUSES = ["in_progress", "approved", "rejected", "billed"];
const CONVERTIBLE = ["in_progress", "approved"];

export default function PurchaseOrderDetailPage() {
  const params = useParams<{ id: string }>();
  const supplierNames = useSupplierNameMap();
  return (
    <DocumentDetail
      docLabel="Purchase order"
      breadcrumb="Buy / Orders / Detail"
      partyLabel="Supplier"
      resolvePartyName={(d) => supplierNames.get(d.supplierId) ?? d.supplierId}
      listHref="/purchases/orders"
      statuses={PO_STATUSES}
      convertLabel="Convert to bill"
      convertSuccessHref="/purchases/bills"
      convertibleStatuses={CONVERTIBLE}
      detailQueryKey={["purchase-order", params.id]}
      fetchDetail={() => purchaseOrdersApi.get(params.id)}
      projectHeader={(d) => ({
        id: d.id,
        number: d.orderNumber,
        date: d.orderDate,
        partyId: d.supplierId,
        status: d.status,
        totalAmount: d.totalAmount,
      })}
      setStatus={(status) => purchaseOrdersApi.setStatus(params.id, status)}
      convert={() => purchaseOrdersApi.convertToBill(params.id)}
      showGst
      descriptionDocType="PO"
      resolveLastRateContext={(d) => ({
        docType: "PO",
        partyKind: "supplier",
        partyId: d.supplierId,
      })}
      printHref={`/print/purchase-orders/${params.id}`}
      attachmentEntityType="purchase_order"
    />
  );
}
