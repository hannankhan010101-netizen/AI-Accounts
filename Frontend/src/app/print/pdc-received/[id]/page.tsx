"use client";

import { useParams } from "next/navigation";
import Decimal from "decimal.js";

import { PrintQueryShell } from "@/components/print/print-query-shell";
import { VoucherPrint } from "@/components/print/voucher-print";
import { useCustomerNameMap } from "@/lib/hooks/use-party-name-map";
import { useVoucherPrintPage } from "@/lib/hooks/use-voucher-print-page";
import { pdcApi } from "@/lib/api/tenant";

function fmt(v: string | number): string {
  try {
    return new Decimal(typeof v === "string" ? v : v.toString()).toFixed(2);
  } catch {
    return String(v);
  }
}

export default function PdcReceivedPrintPage() {
  const params = useParams<{ id: string }>();
  const customerNames = useCustomerNameMap();

  const { query, businessName, businessAddress, businessLogoUrl, template, isLoading, error } = useVoucherPrintPage(
    ["print-pdc-received", params.id],
    () => pdcApi.getReceived(params.id),
    !!params.id,
  
    "pdcr",
  );

  const row = query.data?.result;

  return (
    <PrintQueryShell
      isLoading={isLoading}
      error={error}
      ready={Boolean(row)}
      notFoundMessage="Cheque not found."
    >
      {row ? (
        <VoucherPrint
          title="PDC Received"
          documentNumber={row.voucherNumber}
          documentDate={row.receivedDate}
          businessName={businessName}
          businessAddress={businessAddress}
          businessLogoUrl={businessLogoUrl}
          template={template}
          fields={[
            { label: "Cheque no.", value: row.chequeNumber },
            { label: "Amount", value: fmt(row.amount) },
            {
              label: "Customer",
              value: customerNames.get(row.customerId) ?? row.customerId,
            },
            { label: "Drawer bank", value: row.bankName ?? "—" },
            {
              label: "Cheque date",
              value: new Date(row.chequeDate).toLocaleDateString(),
            },
            { label: "Status", value: row.status },
          ]}
        />
      ) : null}
    </PrintQueryShell>
  );
}
