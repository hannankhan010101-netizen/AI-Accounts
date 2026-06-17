/** GRN detail — catalog §6. */
"use client";

import { useParams } from "next/navigation";


import { LogisticsDocumentDetail } from "@/components/patterns/logistics-document-detail";
import { useSupplierNameMap } from "@/lib/hooks/use-party-name-map";
import { useTenantDetailQuery } from "@/lib/api/tenant-query";
import { deliveryApi } from "@/lib/api/tenant";

import { DetailPageLoading } from "@/components/ui/detail-page-loading";

export default function GrnDetailPage() {
  const params = useParams<{ id: string }>();
  const supplierNames = useSupplierNameMap();
  const { data, isLoading, error } = useTenantDetailQuery(["grn", params.id], () => deliveryApi.getGrn(params.id), { enabled: Boolean(params.id) });

  if (isLoading) return <DetailPageLoading />;
  if (error instanceof Error)
    return (
      <div className="rounded-md border border-status-danger/30 bg-status-danger/10 p-3 text-sm text-status-danger">
        {error.message}
      </div>
    );

  const grn = data?.result;
  if (!grn) return null;

  return (
    <LogisticsDocumentDetail
      docLabel="GRN"
      breadcrumb="Buy / Goods received / Detail"
      listHref="/purchases/grn"
      voucherNumber={grn.voucherNumber}
      documentDate={grn.receiptDate}
      partyLabel="Supplier"
      partyName={supplierNames.get(grn.supplierId) ?? grn.supplierId}
      status={grn.status}
      sourceKind={grn.sourceKind}
      sourceId={grn.sourceId}
      notes={(grn as { notes?: string | null }).notes}
      lines={grn.lines ?? []}
      printHref={`/print/grn/${params.id}`}
      attachmentEntityType="goods_receipt_note"
      entityId={grn.id}
    />
  );
}
