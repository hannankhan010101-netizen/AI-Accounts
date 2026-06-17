"use client";

import { useParams } from "next/navigation";

import { PdcDetail } from "@/components/patterns/pdc-detail";
import { useSupplierNameMap } from "@/lib/hooks/use-party-name-map";

export default function PdcIssuedDetailPage() {
  const params = useParams<{ id: string }>();
  const supplierNames = useSupplierNameMap();

  return (
    <PdcDetail
      mode="issued"
      chequeId={params.id}
      listHref="/purchases/pdc-issued"
      breadcrumb="Buy / PDC Issued / Detail"
      partyLabel="Supplier"
      resolvePartyName={(id) => supplierNames.get(id) ?? id}
      printHref={`/print/pdc-issued/${params.id}`}
    />
  );
}
