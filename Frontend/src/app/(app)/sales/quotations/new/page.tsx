/** New quotation — catalog §5.2. */
"use client";

import { LineGridForm } from "@/components/app/line-grid-form";
import { quotationsApi } from "@/lib/api/tenant";

export default function NewQuotationPage() {
  return (
    <LineGridForm
      title="New quotation"
      breadcrumb="Sell / Quotations / New"
      description="Pre-sale quote (§5.2). No GL impact; convert to a sales order on acceptance."
      partyKind="customer"
      dateLabel="Quotation date"
      cancelHref="/sales/quotations"
      successHref="/sales/quotations"
      draftStorageKey="quotation-new"
      withGst
      descriptionDocType="SQ"
      lastRateDocType="QO"
      saveLabel="Save quotation"
      detailPath={(id) => `/sales/quotations/${id}`}
      onSubmit={({ dateISO, partyId, lines }) =>
        quotationsApi.create({
          quotationDate: dateISO,
          customerId: partyId,
          lines,
        })
      }
    />
  );
}
