"use client";
import { invalidateTenantQueries, useTenantDetailQuery } from "@/lib/api/tenant-query";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
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

export default function BankPaymentDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const bankNames = useBankAccountNameMap();
  const { data, isLoading, error } = useTenantDetailQuery(["bank-payment", params.id], () => bankApi.getPayment(params.id), { enabled: Boolean(params.id) });

  const copyPayment = useMutation({
    mutationFn: () => bankApi.copyPayment(params.id),
    onSuccess: (res) => {
      void invalidateTenantQueries(queryClient, "bank-payments");
      router.push(`/bank/payments/${res.result.id}`);
    },
  });

  const postPayment = useMutation({
    mutationFn: () => bankApi.postPayment(params.id),
    onSuccess: () => {
      void invalidateTenantQueries(queryClient, "bank-payment", params.id);
      void invalidateTenantQueries(queryClient, "bank-payments");
    },
  });

  if (isLoading) return <DetailPageLoading />;
  if (error instanceof Error)
    return (
      <div className="rounded-md border border-status-danger/30 bg-status-danger/10 p-3 text-sm text-status-danger">
        {error.message}
      </div>
    );

  const pay = data?.result;
  if (!pay) return null;

  return (
    <BankVoucherDetail
      title={`Payment ${pay.voucherNumber ?? pay.id}`}
      breadcrumb="Money / Payments out / Detail"
      listHref="/bank/payments"
      voucherId={pay.id}
      attachmentEntityType="bank_payment"
      journalId={pay.journalId as string | null | undefined}
      extraActions={
        <>
          {!pay.journalId && (pay.status ?? "").toLowerCase() === "draft" ? (
            <Button
              type="button"
              disabled={postPayment.isPending}
              onClick={() => postPayment.mutate()}
            >
              {postPayment.isPending ? "Posting…" : "Post to GL"}
            </Button>
          ) : null}
          <Button
            type="button"
            variant="secondary"
            disabled={copyPayment.isPending}
            onClick={() => copyPayment.mutate()}
          >
            {copyPayment.isPending ? "Copying…" : "Copy"}
          </Button>
        </>
      }
      fields={[
        {
          label: "Date",
          value: new Date(pay.paymentDate).toLocaleDateString(),
        },
        {
          label: "Bank account",
          value: bankNames.get(pay.bankAccountId) ?? pay.bankAccountId,
          emphasis: true,
        },
        { label: "Amount", value: fmt(pay.totalAmount), emphasis: true },
        {
          label: "Counterpart nominal",
          value: (pay as { nominalCode?: string | null }).nominalCode ?? "—",
        },
      ]}
      printHref={`/print/bank-payment/${params.id}`}
    />
  );
}
