/** Return unallocated customer advance — FA §5.8 */
"use client";

import { useParams } from "next/navigation";


import { AdvanceReturnForm } from "@/components/patterns/advance-return-form";
import { DetailPageLoading } from "@/components/ui/detail-page-loading";
import { useTenantDetailQuery } from "@/lib/api/tenant-query";
import { salesApi } from "@/lib/api/tenant";


export default function CustomerAdvanceReturnPage() {
  const params = useParams<{ id: string }>();
  const receiptId = params.id;

  const { data, isLoading, error } = useTenantDetailQuery(["sales-receipt", receiptId], () => salesApi.getReceipt(receiptId), { enabled: Boolean(receiptId) });

  if (isLoading) return <DetailPageLoading />;
  if (error instanceof Error) {
    return (
      <div className="rounded-md border border-status-danger/30 bg-status-danger/10 p-3 text-sm text-status-danger">
        {error.message}
      </div>
    );
  }

  const receipt = data?.result;
  const unallocated = data?.balance?.unallocated ?? "0";
  if (!receipt || Number(unallocated) <= 0) {
    return (
      <div className="rounded-md border border-border p-4 text-sm text-fg-muted">
        No unallocated advance available on this receipt.
      </div>
    );
  }

  const voucher = receipt.receiptNumber ?? receiptId.slice(0, 8);

  return (
    <AdvanceReturnForm
      title={`Return advance — ${voucher}`}
      breadcrumb={`Sell / Receipts / ${voucher} / Return advance`}
      cancelHref={`/sales/receipts/${receiptId}`}
      defaultBankAccountId={receipt.bankAccountId}
      maxAmount={unallocated}
      submitLabel="Return advance"
      onSubmit={async (values) => {
        await salesApi.returnAdvance(receiptId, {
          returnDate: values.returnDate,
          amount: values.amount,
          bankAccountId: values.bankAccountId,
        });
      }}
    />
  );
}
