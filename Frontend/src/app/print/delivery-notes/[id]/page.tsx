"use client";

import { useParams } from "next/navigation";
import Decimal from "decimal.js";

import { PrintQueryShell } from "@/components/print/print-query-shell";
import { VoucherPrint } from "@/components/print/voucher-print";
import { useCustomerNameMap } from "@/lib/hooks/use-party-name-map";
import { useVoucherPrintPage } from "@/lib/hooks/use-voucher-print-page";
import { deliveryApi } from "@/lib/api/tenant";

function fmtQty(v: string): string {
  try {
    return new Decimal(v).toFixed(2);
  } catch {
    return v;
  }
}

export default function DeliveryNotePrintPage() {
  const params = useParams<{ id: string }>();
  const customerNames = useCustomerNameMap();

  const { query, businessName, businessAddress, businessLogoUrl, template, isLoading, error } = useVoucherPrintPage(
    ["print-delivery-note", params.id],
    () => deliveryApi.getDeliveryNote(params.id),
    !!params.id,
  
    "gdnsi",
  );

  const note = query.data?.result;
  const lines = note?.lines ?? [];

  return (
    <PrintQueryShell
      isLoading={isLoading}
      error={error}
      ready={Boolean(note)}
      notFoundMessage="Delivery note not found."
    >
      {note ? (
        <VoucherPrint
          title="Delivery Note"
          documentNumber={note.voucherNumber}
          documentDate={note.deliveryDate}
          businessName={businessName}
          businessAddress={businessAddress}
          businessLogoUrl={businessLogoUrl}
          template={template}
          fields={[
            {
              label: "Customer",
              value: customerNames.get(note.customerId) ?? note.customerId,
            },
            { label: "Status", value: note.status },
            {
              label: "Source",
              value: `${note.sourceKind}${note.sourceId ? ` · ${note.sourceId}` : ""}`,
            },
          ]}
          tableHeaders={["Product", "Quantity", "Notes"]}
          tableRows={lines.map((l) => [
            l.productCode ?? "—",
            fmtQty(l.quantity),
            l.notes ?? "",
          ])}
          notes={(note as { notes?: string | null }).notes ?? undefined}
        />
      ) : null}
    </PrintQueryShell>
  );
}
