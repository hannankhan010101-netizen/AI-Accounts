import { lastRateApi } from "@/lib/api/tenant";
import type { LastRateDocType } from "@/lib/hooks/use-last-rate-settings";

export async function applyLastRateToLine(
  setLineField: (field: "rate" | "gstRate" | "gstCode", value: string) => void,
  productCode: string,
  opts: {
    partyKind: "customer" | "supplier";
    partyId: string;
    docType: LastRateDocType;
  },
): Promise<void> {
  if (!opts.partyId || !productCode) return;
  try {
    const res =
      opts.partyKind === "customer"
        ? await lastRateApi.sales(opts.partyId, productCode, opts.docType)
        : await lastRateApi.purchase(opts.partyId, productCode, opts.docType);
    const row = res.result;
    if (!row?.rate) return;
    setLineField("rate", row.rate);
    if (row.gstRate) setLineField("gstRate", row.gstRate);
    if (row.gstCode) setLineField("gstCode", row.gstCode);
  } catch {
    /* optional enrichment */
  }
}
