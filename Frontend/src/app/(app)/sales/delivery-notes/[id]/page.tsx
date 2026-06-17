/** Delivery note detail — catalog §5.6. */
"use client";

import { useParams } from "next/navigation";


import { LogisticsDocumentDetail } from "@/components/patterns/logistics-document-detail";
import { useCustomerNameMap } from "@/lib/hooks/use-party-name-map";
import { useTenantDetailQuery } from "@/lib/api/tenant-query";
import { deliveryApi } from "@/lib/api/tenant";

import { DetailPageLoading } from "@/components/ui/detail-page-loading";

export default function DeliveryNoteDetailPage() {
  const params = useParams<{ id: string }>();
  const customerNames = useCustomerNameMap();
  const { data, isLoading, error } = useTenantDetailQuery(["delivery-note", params.id], () => deliveryApi.getDeliveryNote(params.id), { enabled: Boolean(params.id) });

  if (isLoading) return <DetailPageLoading />;
  if (error instanceof Error)
    return (
      <div className="rounded-md border border-status-danger/30 bg-status-danger/10 p-3 text-sm text-status-danger">
        {error.message}
      </div>
    );

  const note = data?.result;
  if (!note) return null;

  return (
    <LogisticsDocumentDetail
      docLabel="Delivery note"
      breadcrumb="Sell / Delivery notes / Detail"
      listHref="/sales/delivery-notes"
      voucherNumber={note.voucherNumber}
      documentDate={note.deliveryDate}
      partyLabel="Customer"
      partyName={customerNames.get(note.customerId) ?? note.customerId}
      status={note.status}
      sourceKind={note.sourceKind}
      sourceId={note.sourceId}
      notes={(note as { notes?: string | null }).notes}
      lines={note.lines ?? []}
      printHref={`/print/delivery-notes/${params.id}`}
      attachmentEntityType="delivery_note"
      entityId={note.id}
    />
  );
}
