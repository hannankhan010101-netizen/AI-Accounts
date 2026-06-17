/** New sales credit — catalog §5.5. */
"use client";

import { LineGridForm } from "@/components/app/line-grid-form";
import { salesCreditsApi } from "@/lib/api/tenant";

export default function NewSalesCreditPage() {
  return (
    <LineGridForm
      title="New sales credit"
      breadcrumb="Home / Sales / Credits / New"
      description="Credit note reversing AR (§5.5). Auto-posts DR sales / CR receivables when defaults are set."
      partyKind="customer"
      dateLabel="Credit date"
      cancelHref="/sales/credits"
      successHref="/sales/credits"
      draftStorageKey="sales-credit-new"
      withGst
      detailPath={(id) => `/sales/credits/${id}`}
      onSubmit={({ dateISO, partyId, lines }) =>
        salesCreditsApi.create({
          creditDate: dateISO,
          customerId: partyId,
          lines,
        })
      }
    />
  );
}
