"use client";

import { useParams } from "next/navigation";
import Decimal from "decimal.js";

import { PrintQueryShell } from "@/components/print/print-query-shell";
import { VoucherPrint } from "@/components/print/voucher-print";
import { useBankAccountNameMap } from "@/lib/hooks/use-bank-account-name-map";
import { useVoucherPrintPage } from "@/lib/hooks/use-voucher-print-page";
import { bankApi } from "@/lib/api/tenant";

function fmt(v: string | number | undefined | null): string {
  if (v == null || v === "") return "—";
  try {
    return new Decimal(typeof v === "string" ? v : v.toString()).toFixed(2);
  } catch {
    return String(v);
  }
}

export default function BankTransferPrintPage() {
  const params = useParams<{ id: string }>();
  const bankNames = useBankAccountNameMap();

  const { query, businessName, businessAddress, businessLogoUrl, template, isLoading, error } = useVoucherPrintPage(
    ["print-bank-transfer", params.id],
    () => bankApi.getTransfer(params.id),
    !!params.id,
  
    "bank",
  );

  const tr = query.data?.result;

  return (
    <PrintQueryShell
      isLoading={isLoading}
      error={error}
      ready={Boolean(tr)}
      notFoundMessage="Transfer not found."
    >
      {tr ? (
        <VoucherPrint
          title="Bank Transfer"
          documentNumber={String(tr.voucherNumber ?? tr.id.slice(0, 8))}
          documentDate={tr.transferDate}
          businessName={businessName}
          businessAddress={businessAddress}
          businessLogoUrl={businessLogoUrl}
          template={template}
          fields={[
            {
              label: "From",
              value: bankNames.get(tr.fromBankAccountId) ?? tr.fromBankAccountId,
            },
            {
              label: "To",
              value: bankNames.get(tr.toBankAccountId) ?? tr.toBankAccountId,
            },
            { label: "Amount", value: fmt(tr.totalAmount) },
            { label: "Posted", value: tr.journalId ? "Yes" : "No" },
          ]}
        />
      ) : null}
    </PrintQueryShell>
  );
}
