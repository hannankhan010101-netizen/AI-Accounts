/** Return unallocated supplier advance — FA §6.4 */
"use client";

import { useParams } from "next/navigation";


import { AdvanceReturnForm } from "@/components/patterns/advance-return-form";
import { DetailPageLoading } from "@/components/ui/detail-page-loading";
import { useTenantDetailQuery } from "@/lib/api/tenant-query";
import { purchasesApi } from "@/lib/api/tenant";


export default function SupplierAdvanceReturnPage() {
  const params = useParams<{ id: string }>();
  const paymentId = params.id;

  const { data, isLoading, error } = useTenantDetailQuery(["supplier-payment", paymentId], () => purchasesApi.getSupplierPayment(paymentId), { enabled: Boolean(paymentId) });

  if (isLoading) return <DetailPageLoading />;
  if (error instanceof Error) {
    return (
      <div className="rounded-md border border-status-danger/30 bg-status-danger/10 p-3 text-sm text-status-danger">
        {error.message}
      </div>
    );
  }

  const payment = data?.result;
  const unallocated = data?.balance?.unallocated ?? "0";
  if (!payment || Number(unallocated) <= 0) {
    return (
      <div className="rounded-md border border-border p-4 text-sm text-fg-muted">
        No unallocated advance available on this payment.
      </div>
    );
  }

  const voucher = payment.voucherNumber ?? paymentId.slice(0, 8);

  return (
    <AdvanceReturnForm
      title={`Return advance — ${voucher}`}
      breadcrumb={`Buy / Payments / ${voucher} / Return advance`}
      cancelHref={`/purchases/payments/${paymentId}`}
      defaultBankAccountId={payment.bankAccountId}
      maxAmount={unallocated}
      submitLabel="Return advance"
      onSubmit={async (values) => {
        await purchasesApi.returnAdvance(paymentId, {
          returnDate: values.returnDate,
          amount: values.amount,
          bankAccountId: values.bankAccountId,
        });
      }}
    />
  );
}
