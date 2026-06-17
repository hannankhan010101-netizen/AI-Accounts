"use client";

import { useParams } from "next/navigation";
import Decimal from "decimal.js";

import { PrintQueryShell } from "@/components/print/print-query-shell";
import { VoucherPrint } from "@/components/print/voucher-print";
import { useVoucherPrintPage } from "@/lib/hooks/use-voucher-print-page";
import { ledgerApi } from "@/lib/api/tenant";

function fmt(v: string | number | undefined | null): string {
  if (v == null || v === "") return "";
  try {
    return new Decimal(typeof v === "string" ? v : v.toString()).toFixed(2);
  } catch {
    return String(v);
  }
}

export default function JournalPrintPage() {
  const params = useParams<{ id: string }>();

  const { query, businessName, businessAddress, businessLogoUrl, template, isLoading, error } = useVoucherPrintPage(
    ["print-journal", params.id],
    () => ledgerApi.getJournal(params.id),
    !!params.id,
  
    "journal",
  );

  const journal = query.data?.result;
  const lines = journal?.lines ?? [];
  const ref = journal?.refNo ?? journal?.reference ?? "—";

  return (
    <PrintQueryShell
      isLoading={isLoading}
      error={error}
      ready={Boolean(journal)}
      notFoundMessage="Journal not found."
    >
      {journal ? (
        <VoucherPrint
          title="Journal Voucher"
          documentNumber={String(journal.journalNumber ?? journal.id.slice(0, 8))}
          documentDate={journal.journalDate}
          businessName={businessName}
          businessAddress={businessAddress}
          businessLogoUrl={businessLogoUrl}
          template={template}
          fields={[
            { label: "Reference", value: ref },
            {
              label: "Total",
              value: fmt(journal.totalAmount ?? journal.totalDebit),
            },
            { label: "Status", value: journal.status ?? "posted" },
            {
              label: "Source",
              value: journal.sourceType
                ? `${journal.sourceType}${journal.sourceId ? ` · ${journal.sourceId}` : ""}`
                : "—",
            },
          ]}
          tableHeaders={["Nominal", "Debit", "Credit", "Project"]}
          tableRows={lines.map((l) => [
            l.nominalCode,
            fmt(l.debit),
            fmt(l.credit),
            l.projectCode ?? "",
          ])}
        />
      ) : null}
    </PrintQueryShell>
  );
}
