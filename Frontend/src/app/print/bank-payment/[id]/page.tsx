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

export default function BankPaymentPrintPage() {
  const params = useParams<{ id: string }>();
  const bankNames = useBankAccountNameMap();

  const { query, businessName, businessAddress, businessLogoUrl, template, isLoading, error } = useVoucherPrintPage(
    ["print-bank-payment", params.id],
    () => bankApi.getPayment(params.id),
    !!params.id,
  
    "bank",
  );

  const pay = query.data?.result;

  return (
    <PrintQueryShell
      isLoading={isLoading}
      error={error}
      ready={Boolean(pay)}
      notFoundMessage="Payment not found."
    >
      {pay ? (
        <VoucherPrint
          title="Bank Payment"
          documentNumber={String(pay.voucherNumber ?? pay.id.slice(0, 8))}
          documentDate={pay.paymentDate}
          businessName={businessName}
          businessAddress={businessAddress}
          businessLogoUrl={businessLogoUrl}
          template={template}
          fields={[
            {
              label: "Bank account",
              value: bankNames.get(pay.bankAccountId) ?? pay.bankAccountId,
            },
            { label: "Amount", value: fmt(pay.totalAmount) },
            {
              label: "Nominal",
              value: (pay as { nominalCode?: string | null }).nominalCode ?? "—",
            },
            { label: "Posted", value: pay.journalId ? "Yes" : "No" },
          ]}
        />
      ) : null}
    </PrintQueryShell>
  );
}
