/** Bank transfer detail — catalog §4.4. */
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

export default function BankTransferDetailPage() {
  const params = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const bankNames = useBankAccountNameMap();
  const { data, isLoading, error } = useTenantDetailQuery(["bank-transfer", params.id], () => bankApi.getTransfer(params.id), { enabled: Boolean(params.id) });

  const postTransfer = useMutation({
    mutationFn: () => bankApi.postTransfer(params.id),
    onSuccess: () => {
      void invalidateTenantQueries(queryClient, "bank-transfer", params.id);
      void invalidateTenantQueries(queryClient, "bank-transfers");
    },
  });

  if (isLoading) return <DetailPageLoading />;
  if (error instanceof Error)
    return (
      <div className="rounded-md border border-status-danger/30 bg-status-danger/10 p-3 text-sm text-status-danger">
        {error.message}
      </div>
    );

  const tr = data?.result;
  if (!tr) return null;

  return (
    <BankVoucherDetail
      title={`Transfer ${tr.voucherNumber ?? tr.id}`}
      breadcrumb="Money / Transfers / Detail"
      listHref="/bank/transfers"
      voucherId={tr.id}
      attachmentEntityType="bank_transfer"
      journalId={tr.journalId}
      extraActions={
        !tr.journalId && (tr.status ?? "").toLowerCase() === "draft" ? (
          <Button
            type="button"
            disabled={postTransfer.isPending}
            onClick={() => postTransfer.mutate()}
          >
            {postTransfer.isPending ? "Posting…" : "Post to GL"}
          </Button>
        ) : null
      }
      fields={[
        {
          label: "Date",
          value: new Date(tr.transferDate).toLocaleDateString(),
        },
        {
          label: "From",
          value: bankNames.get(tr.fromBankAccountId) ?? tr.fromBankAccountId,
        },
        {
          label: "To",
          value: bankNames.get(tr.toBankAccountId) ?? tr.toBankAccountId,
          emphasis: true,
        },
        { label: "Amount", value: fmt(tr.totalAmount), emphasis: true },
      ]}
      printHref={`/print/bank-transfer/${params.id}`}
    />
  );
}
