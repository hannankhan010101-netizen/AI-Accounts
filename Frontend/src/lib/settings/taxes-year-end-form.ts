import type { TaxRateRow, TaxRegion, WhtRow } from "@/lib/api/tenant";

export type TaxesYearEndFormShape = {
  yearEndDate: string;
  taxDisplay: Record<string, { label: string; supplier: boolean; customer: boolean }>;
  gstRates: TaxRateRow[];
  adtRates: TaxRateRow[];
  fedRates: TaxRateRow[];
  whtRates: WhtRow[];
  taxRegions: TaxRegion[];
};
