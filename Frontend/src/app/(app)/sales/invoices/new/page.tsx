/** New sales invoice — catalog §5.4 */
"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useFieldArray, useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import Decimal from "decimal.js";

import { TransactionTemplatePicker } from "@/components/patterns/transaction-template-picker";
import { SmartDocumentFilters } from "@/components/patterns/smart-document-filters";
import { DocumentWorkspace } from "@/components/patterns/document-workspace";
import { GstLineGrid, type GstLineRow } from "@/components/patterns/gst-line-grid";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import {
  inventoryApi,
  partiesApi,
  salesApi,
  settingsApi,
  type SalesInvoiceCreateInput,
} from "@/lib/api/tenant";
import { ApiError } from "@/lib/api/client";
import { useCompany } from "@/lib/auth/company-context";
import { hasMeaningfulLineGridDraft } from "@/lib/hooks/document-draft-helpers";
import { useDocumentWorkspaceDraft } from "@/lib/hooks/use-document-workspace-draft";
import { invalidateTenantQueries, useTenantListQuery } from "@/lib/api/tenant-query";
import { DemoSandboxBanner } from "@/components/onboarding/demo-sandbox-banner";
import {
  useTourDemoSandbox,
  useTourGhostFill,
} from "@/features/onboarding/hooks/use-tour-ghost-fill";
import { useProductDescriptionColumns } from "@/lib/hooks/use-product-description-columns";
import { descriptionFieldsFromLine } from "@/lib/hooks/product-description-columns";
import { useFormFieldVisibility } from "@/lib/hooks/use-form-field-visibility";
import { applyLastRateToLine } from "@/lib/document/apply-last-rate";
import { useLastRateSettings } from "@/lib/hooks/use-last-rate-settings";

const lineSchema = z.object({
  productCode: z.string().optional(),
  quantity: z.string().regex(/^\d+(\.\d+)?$/u, "Positive number"),
  rate: z.string().regex(/^\d+(\.\d+)?$/u, "Positive number"),
  gstCode: z.string().optional(),
  gstRate: z.string().optional(),
  adtCode: z.string().optional(),
  fedCode: z.string().optional(),
  projectCode: z.string().optional(),
  description: z.string().optional(),
  text1: z.string().optional(),
  text2: z.string().optional(),
  text3: z.string().optional(),
  text4: z.string().optional(),
  text5: z.string().optional(),
  text6: z.string().optional(),
  batchNumber: z.string().optional(),
  expiryDate: z.string().optional(),
});

const smartFilterSchema = z.object({
  filter1: z.string().optional(),
  filter2: z.string().optional(),
  filter3: z.string().optional(),
  filter4: z.string().optional(),
  doc1: z.string().optional(),
  doc2: z.string().optional(),
  doc3: z.string().optional(),
  doc4: z.string().optional(),
});

const schema = z.object({
  invoiceDate: z.string().min(1, "Required"),
  customerId: z.string().min(1, "Required"),
  lines: z.array(lineSchema).min(1, "At least one line"),
  smartFilters: smartFilterSchema.optional(),
});
type FormValues = z.infer<typeof schema>;

function emptyLine(): GstLineRow {
  return {
    productCode: "",
    quantity: "1",
    rate: "0",
    gstCode: "",
    gstRate: "",
    adtCode: "",
    fedCode: "",
    projectCode: "",
    batchNumber: "",
    expiryDate: "",
  };
}

function dec(value: string): Decimal {
  if (!value) return new Decimal(0);
  try {
    return new Decimal(value);
  } catch {
    return new Decimal(0);
  }
}

export default function NewSalesInvoicePage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { companyId } = useCompany();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [postingWarning, setPostingWarning] = useState<string | null>(null);

  const customersQuery = useTenantListQuery(["customers"], () => partiesApi.listCustomers());
  const productsQuery = useTenantListQuery(["products"], () => inventoryApi.listProducts());
  const taxesQuery = useTenantListQuery(["taxes-year-end"], () => settingsApi.getTaxesYearEnd());
  const gstRates = taxesQuery.data?.result?.gstRates ?? [];
  const adtRates = taxesQuery.data?.result?.adtRates ?? [];
  const fedRates = taxesQuery.data?.result?.fedRates ?? [];
  const { columns: descriptionColumns } = useProductDescriptionColumns("SI");
  const { addEditEnabled: lastRateEnabled } = useLastRateSettings("SI");
  const { isVisible: formFieldVisible } = useFormFieldVisibility("sales-invoice");

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      invoiceDate: new Date().toISOString().slice(0, 10),
      customerId: "",
      lines: [emptyLine()],
    },
  });

  const lines = useFieldArray({ control: form.control, name: "lines" });
  const watched = form.watch();
  const watchedLines = watched.lines ?? [];
  const customerId = watched.customerId;

  const { topBanner, clearDraftOnSuccess } = useDocumentWorkspaceDraft({
    scope: "sales-invoice-new",
    companyId,
    form,
    values: watched,
    shouldPersist: hasMeaningfulLineGridDraft,
  });

  const demoSandbox = useTourDemoSandbox();
  const customerIds = useMemo(
    () => customersQuery.data?.result.map((c) => c.id) ?? [],
    [customersQuery.data],
  );
  const productCodes = useMemo(
    () => productsQuery.data?.result.map((p) => p.code).filter(Boolean) as string[] ?? [],
    [productsQuery.data],
  );
  const { filling: ghostFilling } = useTourGhostFill({
    form,
    context: {
      customerIds,
      supplierIds: [],
      bankAccountIds: [],
      productCodes,
    },
  });

  const customerName = useMemo(() => {
    const c = customersQuery.data?.result.find((x) => x.id === customerId);
    return c?.name ?? "—";
  }, [customersQuery.data, customerId]);

  const lineTotals = useMemo(
    () =>
      watchedLines.map((l) => {
        const sub = dec(l.quantity).times(dec(l.rate));
        const ratePct = l.gstRate ? dec(l.gstRate) : new Decimal(0);
        const tax = ratePct.gt(0) ? sub.times(ratePct).div(100) : new Decimal(0);
        return sub.plus(tax);
      }),
    [watchedLines],
  );
  const subtotal = useMemo(
    () =>
      watchedLines.reduce(
        (acc, l) => acc.plus(dec(l.quantity).times(dec(l.rate))),
        new Decimal(0),
      ),
    [watchedLines],
  );
  const grandTotal = useMemo(
    () => lineTotals.reduce((acc, v) => acc.plus(v), new Decimal(0)),
    [lineTotals],
  );

  const mutation = useMutation({
    mutationFn: (input: SalesInvoiceCreateInput) => salesApi.createInvoice(input),
    onSuccess: async (res) => {
      clearDraftOnSuccess();
      await invalidateTenantQueries(queryClient, "sales-invoices");
      await invalidateTenantQueries(queryClient, "sales-invoices");
      const id = res.result?.id;
      if (res.posted === false && res.postingWarning) {
        setPostingWarning(res.postingWarning);
        if (id) {
          setTimeout(() => router.push(`/sales/invoices/${id}`), 1500);
        }
        return;
      }
      if (id) router.push(`/sales/invoices/${id}`);
      else router.push("/sales/invoices");
    },
    onError: (err) =>
      setSubmitError(err instanceof ApiError ? err.message : "Could not create invoice"),
  });

  const onSubmit = form.handleSubmit((values) => {
    if (demoSandbox) return;
    setSubmitError(null);
    setPostingWarning(null);
    mutation.mutate({
      invoiceDate: new Date(values.invoiceDate).toISOString(),
      customerId: values.customerId,
      lines: values.lines.map((l) => {
        const row: SalesInvoiceCreateInput["lines"][number] = {
          productCode: l.productCode || null,
          quantity: l.quantity,
          rate: l.rate,
          gstCode: l.gstCode || null,
          gstRate: l.gstRate || null,
          adtCode: l.adtCode || null,
          fedCode: l.fedCode || null,
          projectCode: l.projectCode || null,
        };
        if (l.description?.trim()) row.description = l.description.trim();
        const extra = descriptionFieldsFromLine(l as Record<string, unknown>, descriptionColumns);
        if (extra) row.descriptionFields = extra;
        if (l.batchNumber?.trim()) row.batchNumber = l.batchNumber.trim();
        if (l.expiryDate?.trim()) row.expiryDate = new Date(l.expiryDate).toISOString();
        return row;
      }),
      smartFilters: values.smartFilters,
    });
  });

  const handleProductSelect = async (lineIndex: number, productCode: string) => {
    if (!lastRateEnabled || !customerId) return;
    await applyLastRateToLine(
      (field, value) => form.setValue(`lines.${lineIndex}.${field}`, value),
      productCode,
      { partyKind: "customer", partyId: customerId, docType: "SI" },
    );
  };

  const loadTemplate = (payload: Record<string, unknown>) => {
    if (typeof payload.invoiceDate === "string") form.setValue("invoiceDate", payload.invoiceDate);
    if (typeof payload.customerId === "string") form.setValue("customerId", payload.customerId);
    if (Array.isArray(payload.lines)) {
      form.setValue("lines", payload.lines as FormValues["lines"]);
    }
    if (payload.smartFilters && typeof payload.smartFilters === "object") {
      form.setValue("smartFilters", payload.smartFilters as FormValues["smartFilters"]);
    }
  };

  return (
    <DocumentWorkspace
      title="New sales invoice"
      breadcrumb="Sell / Invoices / New"
      tourRoot="si-new-header"
      tourSummary="si-new-summary"
      tourSave="si-new-save"
      formId="si-form"
      onSubmit={onSubmit}
      topBanner={topBanner}
      demoSandbox={demoSandbox}
      demoSandboxBanner={<DemoSandboxBanner filling={ghostFilling} />}
      isSaving={mutation.isPending}
      saveLabel="Save invoice"
      onCancel={() => router.push("/sales/invoices")}
      grandTotal={grandTotal.toFixed(2)}
      grandTotalLabel="Total incl. tax"
      error={submitError}
      warning={postingWarning}
      summaryLines={[
        { label: "Customer", value: customerName, emphasis: true },
        { label: "Lines", value: String(watchedLines.length) },
        { label: "Subtotal", value: subtotal.toFixed(2) },
        {
          label: "Tax",
          value: grandTotal.minus(subtotal).toFixed(2),
        },
      ]}
      header={
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2" data-tour="si-new-header">
          <FormField label="Invoice date" required error={form.formState.errors.invoiceDate?.message}>
            <Input type="date" {...form.register("invoiceDate")} />
          </FormField>
          <FormField label="Customer" required error={form.formState.errors.customerId?.message}>
            <Select {...form.register("customerId")}>
              <option value="">Select customer…</option>
              {customersQuery.data?.result.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                  {c.code ? ` (${c.code})` : ""}
                </option>
              ))}
            </Select>
          </FormField>
        </div>
      }
    >
      <TransactionTemplatePicker
        module="sales_invoice"
        onLoad={loadTemplate}
        onCapturePayload={() => ({
          invoiceDate: form.getValues("invoiceDate"),
          customerId: form.getValues("customerId"),
          lines: form.getValues("lines"),
          smartFilters: form.getValues("smartFilters"),
        })}
      />
      <GstLineGrid
        form={form}
        lines={lines}
        lineTotals={lineTotals}
        products={productsQuery.data?.result}
        gstRates={gstRates}
        adtRates={adtRates}
        fedRates={fedRates}
        emptyLine={emptyLine}
        tourTarget="si-new-lines"
        onProductSelect={handleProductSelect}
        descriptionColumns={descriptionColumns}
        showBatchExpiry={formFieldVisible("batchExpiry")}
      />
      {formFieldVisible("smartFilters") ? (
      <section className="mt-6 border-t border-border pt-4">
        <h3 className="mb-3 text-sm font-medium text-fg-muted">Smart filters</h3>
        <SmartDocumentFilters module="sales" register={form.register} />
      </section>
      ) : null}
    </DocumentWorkspace>
  );
}
