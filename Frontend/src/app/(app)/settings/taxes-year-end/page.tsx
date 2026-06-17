"use client";
import { useTenantReferenceQuery, invalidateTenantQueries } from "@/lib/api/tenant-query";

import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useFieldArray, useForm } from "react-hook-form";

import {
  TaxDisplayGrid,
  TaxRateGrid,
  TaxRegionGrid,
  WhtRateGrid,
} from "@/components/settings/tax-form-grids";
import { TaxAutoCodeHints, useTaxAutoCodePeek } from "@/components/settings/tax-auto-code-hints";
import { DraftRecoveryBanner } from "@/components/ui/draft-recovery-banner";
import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { WorkspaceLoading } from "@/components/ui/workspace-loading";
import {
  settingsApi,
  type TaxesYearEnd,
  type TaxRateRow,
  type WhtRow,
  type TaxRegion,
} from "@/lib/api/tenant";
import type { TaxesYearEndFormShape } from "@/lib/settings/taxes-year-end-form";
import { useCompany } from "@/lib/auth/company-context";
import { useFormDraft } from "@/lib/hooks/use-form-draft";
import { referenceQueryOptions } from "@/lib/query/options";

const TAX_DISPLAY_ROWS = [
  { key: "gstOnInvoice", description: "GST on invoice" },
  { key: "adtOnInvoice", description: "ADT on invoice" },
  { key: "fedOnInvoice", description: "FED on invoice" },
  { key: "wht", description: "WHT (withholding income tax)" },
  { key: "gstWithheld", description: "GST withheld" },
] as const;

function taxesFormFromApi(r: TaxesYearEnd): TaxesYearEndFormShape {
  return {
    yearEndDate: r.yearEndDate ? r.yearEndDate.slice(0, 10) : "",
    taxDisplay: {
      ...Object.fromEntries(
        TAX_DISPLAY_ROWS.map((row) => [
          row.key,
          { label: row.description, supplier: false, customer: false },
        ]),
      ),
      ...(r.taxDisplay as TaxesYearEndFormShape["taxDisplay"] | undefined),
    },
    gstRates: r.gstRates ?? [],
    adtRates: r.adtRates ?? [],
    fedRates: r.fedRates ?? [],
    whtRates: r.whtRates ?? [],
    taxRegions: r.taxRegions ?? [],
  };
}

function emptyRateRow(): TaxRateRow {
  return {
    region: "",
    regionCode: "",
    taxCode: "",
    taxRate: 0,
    additionalTaxRate: 0,
    accountId: "",
    printLabel: "",
    status: "active",
  };
}

export default function TaxesYearEndPage() {
  const qc = useQueryClient();
  const { companyId } = useCompany();
  const [savedAt, setSavedAt] = useState<Date | null>(null);

  const { data, isLoading } = useTenantReferenceQuery(["taxes-year-end"], () => settingsApi.getTaxesYearEnd());

  const form = useForm<TaxesYearEndFormShape>({
    defaultValues: {
      yearEndDate: "",
      taxDisplay: Object.fromEntries(
        TAX_DISPLAY_ROWS.map((r) => [r.key, { label: r.description, supplier: false, customer: false }]),
      ),
      gstRates: [],
      adtRates: [],
      fedRates: [],
      whtRates: [],
      taxRegions: [],
    },
  });

  const serverValues = useMemo(
    () => (data?.result ? taxesFormFromApi(data.result) : undefined),
    [data],
  );

  const { hasRecoverableDraft, restoreDraft, discardDraft, clearDraftOnSave } = useFormDraft({
    scope: "taxes-year-end",
    companyId,
    form,
    serverValues,
    enabled: Boolean(companyId && serverValues),
  });

  useEffect(() => {
    if (serverValues) form.reset(serverValues);
  }, [serverValues, form]);

  const gst = useFieldArray({ control: form.control, name: "gstRates" });
  const adt = useFieldArray({ control: form.control, name: "adtRates" });
  const fed = useFieldArray({ control: form.control, name: "fedRates" });
  const wht = useFieldArray({ control: form.control, name: "whtRates" });
  const regions = useFieldArray({ control: form.control, name: "taxRegions" });
  const taxAutoCodes = useTaxAutoCodePeek();

  const mutation = useMutation({
    mutationFn: (values: TaxesYearEndFormShape) => {
      const payload: TaxesYearEnd = {
        yearEndDate: values.yearEndDate || null,
        taxDisplay: values.taxDisplay,
        gstRates: values.gstRates,
        adtRates: values.adtRates,
        fedRates: values.fedRates,
        whtRates: values.whtRates,
        taxRegions: values.taxRegions,
      };
      return settingsApi.putTaxesYearEnd(payload);
    },
    onSuccess: () => {
      setSavedAt(new Date());
      clearDraftOnSave();
      invalidateTenantQueries(qc, "taxes-year-end");
    },
  });

  const onSubmit = form.handleSubmit((v) => mutation.mutate(v));

  return (
    <div>
      <PageHeader
        title="Taxes and Year End"
        breadcrumb="Admin / Taxes and year end"
        description="Year-end date, tax display, GST/ADT/FED/WHT rates and tax regions (§12.12)."
        actions={
          <Button type="submit" form="tye-form" disabled={mutation.isPending}>
            {mutation.isPending ? "Saving…" : "Save"}
          </Button>
        }
      />

      <DraftRecoveryBanner
        visible={hasRecoverableDraft}
        onRestore={restoreDraft}
        onDiscard={discardDraft}
      />

      {isLoading ? (
        <WorkspaceLoading />
      ) : (
        <form id="tye-form" onSubmit={onSubmit} className="space-y-6">
          <section className="rounded-lg border border-border bg-surface p-4">
            <h2 className="mb-3 text-sm font-semibold text-fg">Year end</h2>
            <FormField label="Year end date" htmlFor="yearEndDate">
              <Input id="yearEndDate" type="date" {...form.register("yearEndDate")} />
            </FormField>
          </section>

          <section className="rounded-lg border border-border bg-surface p-4">
            <h2 className="mb-3 text-sm font-semibold text-fg">Tax display settings</h2>
            <TaxDisplayGrid rows={[...TAX_DISPLAY_ROWS]} register={form.register} />
          </section>

          <TaxAutoCodeHints peek={taxAutoCodes} />

          <TaxRateGrid
            title="GST rates"
            fields={gst.fields}
            namePrefix="gstRates"
            register={form.register}
            onAdd={() =>
              gst.append({ ...emptyRateRow(), taxCode: taxAutoCodes.gst.nextCode ?? "" })
            }
            onRemove={(i) => gst.remove(i)}
          />
          <TaxRateGrid
            title="ADT rates"
            fields={adt.fields}
            namePrefix="adtRates"
            register={form.register}
            onAdd={() =>
              adt.append({ ...emptyRateRow(), taxCode: taxAutoCodes.adt.nextCode ?? "" })
            }
            onRemove={(i) => adt.remove(i)}
          />
          <TaxRateGrid
            title="FED rates"
            fields={fed.fields}
            namePrefix="fedRates"
            register={form.register}
            onAdd={() =>
              fed.append({ ...emptyRateRow(), taxCode: taxAutoCodes.fed.nextCode ?? "" })
            }
            onRemove={(i) => fed.remove(i)}
          />

          <WhtRateGrid
            fields={wht.fields}
            register={form.register}
            onAdd={() =>
              wht.append({
                taxName: "",
                taxCode: taxAutoCodes.wht.nextCode ?? "",
                taxRate: 0,
              })
            }
            onRemove={(i) => wht.remove(i)}
          />

          <TaxRegionGrid
            fields={regions.fields}
            register={form.register}
            onAdd={() => regions.append({ regionName: "", regionCode: "" })}
            onRemove={(i) => regions.remove(i)}
          />

          <div className="flex items-center gap-3">
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? "Saving…" : "Save"}
            </Button>
            {savedAt && (
              <span className="text-xs text-status-success">
                Saved at {savedAt.toLocaleTimeString()}
              </span>
            )}
            {mutation.error instanceof Error && (
              <span className="text-xs text-status-danger">{mutation.error.message}</span>
            )}
          </div>
        </form>
      )}
    </div>
  );
}

