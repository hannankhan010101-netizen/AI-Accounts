/** New supplier credit — catalog §6.3 (VC). */
"use client";

import { LineGridForm } from "@/components/app/line-grid-form";
import { supplierCreditsApi } from "@/lib/api/tenant";

export default function NewSupplierCreditPage() {
  return (
    <LineGridForm
      title="New supplier credit"
      breadcrumb="Home / Purchases / Credits / New"
      description="Credit note reversing AP (§6.3). Auto-posts DR payables / CR purchases when defaults are set."
      partyKind="supplier"
      dateLabel="Credit date"
      cancelHref="/purchases/credits"
      successHref="/purchases/credits"
      draftStorageKey="purchase-credit-new"
      withGst
      detailPath={(id) => `/purchases/credits/${id}`}
      onSubmit={({ dateISO, partyId, lines }) =>
        supplierCreditsApi.create({
          creditDate: dateISO,
          supplierId: partyId,
          lines,
        })
      }
    />
  );
}
