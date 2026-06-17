/** Bank receipt detail — catalog §4.3. */
"use client";
import { invalidateTenantQueries, useTenantDetailQuery } from "@/lib/api/tenant-query";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import Decimal from "decimal.js";

import { BankVoucherDetail } from "@/components/patterns/bank-voucher-detail";
import { Button } from "@/components/ui/button";
import { useBankAccountNameMap } from "@/lib/hooks/use-bank-account-name-map";
import { bankApi } from "@/lib/api/tenant";

import { DetailPageLoading } from "@/components/ui/detail-page-loading";

function fmt(v: string | number | undefined | null): string {
  if (v == null || v === "") return "—";
  try {
    return new Decimal(typeof v === "string" ? v : v.toString()).toFixed(2);
  } catch {
    return String(v);
  }
}

export default function BankReceiptDetailPage() {
  const params = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const bankNames = useBankAccountNameMap();
  const { data, isLoading, error } = useTenantDetailQuery(["bank-receipt", params.id], () => bankApi.getReceipt(params.id), { enabled: Boolean(params.id) });

  const postReceipt = useMutation({
    mutationFn: () => bankApi.postReceipt(params.id),
    onSuccess: () => {
      void invalidateTenantQueries(queryClient, "bank-receipt", params.id);
      void invalidateTenantQueries(queryClient, "bank-receipts");
    },
  });

  if (isLoading) return <DetailPageLoading />;
  if (error instanceof Error)
    return (
      <div className="rounded-md border border-status-danger/30 bg-status-danger/10 p-3 text-sm text-status-danger">
        {error.message}
      </div>
    );

  const rec = data?.result;
  if (!rec) return null;

  return (
    <BankVoucherDetail
      title={`Receipt ${rec.voucherNumber ?? rec.id}`}
      breadcrumb="Money / Receipts in / Detail"
      listHref="/bank/receipts"
      voucherId={rec.id}
      attachmentEntityType="bank_receipt"
      journalId={rec.journalId as string | null | undefined}
      extraActions={
        !rec.journalId && (rec.status ?? "").toLowerCase() === "draft" ? (
          <Button
            type="button"
            disabled={postReceipt.isPending}
            onClick={() => postReceipt.mutate()}
          >
            {postReceipt.isPending ? "Posting…" : "Post to GL"}
          </Button>
        ) : null
      }
      fields={[
        {
          label: "Date",
          value: new Date(rec.receiptDate).toLocaleDateString(),
        },
        {
          label: "Bank account",
          value: bankNames.get(rec.bankAccountId) ?? rec.bankAccountId,
          emphasis: true,
        },
        { label: "Amount", value: fmt(rec.totalAmount), emphasis: true },
        {
          label: "Counterpart nominal",
          value: (rec as { nominalCode?: string | null }).nominalCode ?? "—",
        },
      ]}
      printHref={`/print/bank-receipt/${params.id}`}
    />
  );
}
