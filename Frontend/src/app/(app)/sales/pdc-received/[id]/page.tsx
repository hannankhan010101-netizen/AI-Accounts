"use client";

import { useParams } from "next/navigation";

import { PdcDetail } from "@/components/patterns/pdc-detail";
import { useCustomerNameMap } from "@/lib/hooks/use-party-name-map";

export default function PdcReceivedDetailPage() {
  const params = useParams<{ id: string }>();
  const customerNames = useCustomerNameMap();

  return (
    <PdcDetail
      mode="received"
      chequeId={params.id}
      listHref="/sales/pdc-received"
      breadcrumb="Sell / PDC Received / Detail"
      partyLabel="Customer"
      resolvePartyName={(id) => customerNames.get(id) ?? id}
      printHref={`/print/pdc-received/${params.id}`}
    />
  );
}
