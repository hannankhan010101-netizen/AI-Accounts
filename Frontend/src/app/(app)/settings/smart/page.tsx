"use client";
import { useTenantReferenceQuery, invalidateTenantQueries } from "@/lib/api/tenant-query";

import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";

import { Accordion, AccordionItem } from "@/components/ui/accordion";
import { DraftRecoveryBanner } from "@/components/ui/draft-recovery-banner";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { WorkspaceLoading } from "@/components/ui/workspace-loading";
import { useCompany } from "@/lib/auth/company-context";
import { useFormDraft } from "@/lib/hooks/use-form-draft";
import { settingsApi } from "@/lib/api/tenant";
import { referenceQueryOptions } from "@/lib/query/options";

/** Catalog §12.2.1 — 20 accordion sections + "Default nominals" extension for GL posting. */
const SECTION_TITLES = [
  "Default nominals",
  "Others",
  "Sales",
  "Purchases",
  "Bank",
  "Fixed Assets",
  "E-Signatures",
  "Product Description",
  "Template / Draft",
  "Last Rate",
  "Customer Auto Account No.",
  "Supplier Auto Account No.",
  "Product Auto Code",
  "Location Auto Code",
  "Project Auto Code",
  "WHT Auto Code",
  "GST Auto Code",
  "ADT Auto Code",
  "FED Auto Code",
  "Nominal Auto Code",
  "Currency & Time Zone",
] as const;

const OTHERS_TOGGLES = [
  ["setCustomerAsSupplier", "Set customer as supplier"],
  ["warnOverSaleOrder", "Warning on over sale (order)"],
  ["warnOverSaleInvoice", "Warning on over sale (invoice)"],
  ["viewProductLastSaleRate", "View product last sale rate"],
  ["roundOffSales", "Round off sales"],
  ["nonstockTransfer", "Nonstock transfer"],
  ["autoPaymentOffset", "Auto payment offset"],
  ["projectsAccounting", "Projects accounting"],
  ["applyCreditLimit", "Apply credit limit"],
  ["applySoCreditLimit", "Apply SO credit limit"],
  ["customerWht", "Customer WHT"],
  ["quotations", "Quotations"],
  ["customerProducts", "Customer products"],
  ["posInvoices", "POS invoices"],
  ["transactionNotes", "Transaction notes"],
] as const;

import {
  renderSmartSettingsSection,
  type SmartSettingsPayload,
} from "@/components/settings/smart-settings-sections";

export default function SmartSettingsPage() {
  const qc = useQueryClient();
  const { companyId } = useCompany();
  const [savedAt, setSavedAt] = useState<Date | null>(null);

  const { data, isLoading } = useTenantReferenceQuery(["smart-settings"], () => settingsApi.getSmartSettings());

  const form = useForm<SmartSettingsPayload>({
    defaultValues: { others: {}, currency: { dateFormat: "dd/mm/yyyy" } },
  });

  const serverValues = useMemo(
    () =>
      data?.result?.payload
        ? (data.result.payload as SmartSettingsPayload)
        : undefined,
    [data],
  );

  const { hasRecoverableDraft, restoreDraft, discardDraft, clearDraftOnSave } = useFormDraft({
    scope: "smart-settings",
    companyId,
    form,
    serverValues,
    enabled: Boolean(companyId && serverValues),
  });

  useEffect(() => {
    if (serverValues) form.reset(serverValues);
  }, [serverValues, form]);

  const mutation = useMutation({
    mutationFn: (values: SmartSettingsPayload) =>
      settingsApi.putSmartSettings(values as Record<string, unknown>),
    onSuccess: () => {
      setSavedAt(new Date());
      clearDraftOnSave();
      invalidateTenantQueries(qc, "smart-settings");
    },
  });

  const onSubmit = form.handleSubmit((values) => mutation.mutate(values));

  return (
    <div>
      <PageHeader
        title="Smart Settings"
        breadcrumb="Home / Smart Settings"
        description="Central configuration accordion (§12.2). Configure filters, auto-codes, templates, and defaults for each module."
        actions={
          <Button type="submit" form="smart-form" disabled={mutation.isPending}>
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
        <form id="smart-form" onSubmit={onSubmit}>
          <Accordion>
            {SECTION_TITLES.map((title) => {
              if (title === "Default nominals") {
                return (
                  <AccordionItem key={title} title={title} defaultOpen>
                    <p className="mb-3 text-xs text-fg-muted">
                      Codes the GL posting service uses when creating journals for sales
                      invoices, supplier bills, and bank payments. Leave any code blank to
                      skip posting for that document type (the document is still recorded).
                    </p>
                    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                      <FormField label="Receivables (AR) nominal — DR on sales invoices">
                        <Input
                          placeholder="e.g. 1100"
                          {...form.register("defaults.receivablesNominalCode")}
                        />
                      </FormField>
                      <FormField label="Sales (revenue) nominal — CR on sales invoices">
                        <Input
                          placeholder="e.g. 4000"
                          {...form.register("defaults.salesNominalCode")}
                        />
                      </FormField>
                      <FormField label="Payables (AP) nominal — CR on supplier bills">
                        <Input
                          placeholder="e.g. 2100"
                          {...form.register("defaults.payablesNominalCode")}
                        />
                      </FormField>
                      <FormField label="Purchases nominal — DR on supplier bills">
                        <Input
                          placeholder="e.g. 5000"
                          {...form.register("defaults.purchasesNominalCode")}
                        />
                      </FormField>
                    </div>
                  </AccordionItem>
                );
              }
              if (title === "Others") {
                return (
                  <AccordionItem key={title} title={title} defaultOpen>
                    <div className="grid grid-cols-1 gap-2 md:grid-cols-3">
                      {OTHERS_TOGGLES.map(([key, label]) => (
                        <label
                          key={key}
                          className="flex items-center gap-2 text-sm text-fg"
                        >
                          <Checkbox {...form.register(`others.${key}` as const)} />
                          {label}
                        </label>
                      ))}
                    </div>
                  </AccordionItem>
                );
              }
              if (title === "Currency & Time Zone") {
                return (
                  <AccordionItem key={title} title={title}>
                    <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                      <FormField label="Base currency (ISO 4217)">
                        <Input
                          placeholder="PKR / USD / …"
                          {...form.register("currency.baseCurrency")}
                        />
                      </FormField>
                      <FormField label="Time zone">
                        <Input
                          placeholder="Asia/Karachi"
                          {...form.register("currency.timeZone")}
                        />
                      </FormField>
                      <FormField label="Date format">
                        <Input {...form.register("currency.dateFormat")} />
                      </FormField>
                    </div>
                  </AccordionItem>
                );
              }
              const wired = renderSmartSettingsSection(title, form);
              if (wired) return wired;
              return (
                <AccordionItem key={title} title={title}>
                  <div className="text-sm text-fg-muted">
                    Configuration for &ldquo;{title}&rdquo; lands in a follow-up milestone.
                  </div>
                </AccordionItem>
              );
            })}
          </Accordion>

          <div className="mt-4 flex items-center gap-3">
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
