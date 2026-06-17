/** New supplier bill — catalog §6.3 */
"use client";
import { useTenantListQuery, invalidateTenantQueries } from "@/lib/api/tenant-query";


import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useFieldArray, useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import Decimal from "decimal.js";

import { DocumentWorkspace } from "@/components/patterns/document-workspace";
import { GstLineGrid, type GstLineRow } from "@/components/patterns/gst-line-grid";
import { TransactionTemplatePicker } from "@/components/patterns/transaction-template-picker";
import { SmartDocumentFilters } from "@/components/patterns/smart-document-filters";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import {
  inventoryApi,
  partiesApi,
  purchasesApi,
  settingsApi,
  type SupplierBillCreateInput,
} from "@/lib/api/tenant";
import { ApiError } from "@/lib/api/client";
import { useCompany } from "@/lib/auth/company-context";
import { hasMeaningfulLineGridDraft } from "@/lib/hooks/document-draft-helpers";
import { useDocumentWorkspaceDraft } from "@/lib/hooks/use-document-workspace-draft";
import { DemoSandboxBanner } from "@/components/onboarding/demo-sandbox-banner";
import {
  useTourDemoSandbox,
  useTourGhostFill,
} from "@/features/onboarding/hooks/use-tour-ghost-fill";
import { useProductDescriptionColumns } from "@/lib/hooks/use-product-description-columns";
import { descriptionFieldsFromLine } from "@/lib/hooks/product-description-columns";
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
  billDate: z.string().min(1, "Required"),
  supplierId: z.string().min(1, "Required"),
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
    batchNumber: "",
    expiryDate: "",
  };
}

function dec(v: string): Decimal {
  if (!v) return new Decimal(0);
  try {
    return new Decimal(v);
  } catch {
    return new Decimal(0);
  }
}

export default function NewSupplierBillPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { companyId } = useCompany();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [postingWarning, setPostingWarning] = useState<string | null>(null);

  const suppliersQuery = useTenantListQuery(["suppliers"], () => partiesApi.listSuppliers());
  const productsQuery = useTenantListQuery(["products"], () => inventoryApi.listProducts());
  const taxesQuery = useTenantListQuery(["taxes-year-end"], () => settingsApi.getTaxesYearEnd());
  const gstRates = taxesQuery.data?.result?.gstRates ?? [];
  const adtRates = taxesQuery.data?.result?.adtRates ?? [];
  const fedRates = taxesQuery.data?.result?.fedRates ?? [];
  const { columns: descriptionColumns } = useProductDescriptionColumns("VI");
  const { addEditEnabled: lastRateEnabled } = useLastRateSettings("VI");

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      billDate: new Date().toISOString().slice(0, 10),
      supplierId: "",
      lines: [emptyLine()],
    },
  });

  const lines = useFieldArray({ control: form.control, name: "lines" });
  const watched = form.watch();
  const watchedLines = watched.lines ?? [];
  const supplierId = watched.supplierId;

  const { topBanner, clearDraftOnSuccess } = useDocumentWorkspaceDraft({
    scope: "supplier-bill-new",
    companyId,
    form,
    values: watched,
    shouldPersist: hasMeaningfulLineGridDraft,
  });

  const demoSandbox = useTourDemoSandbox();
  const supplierIds = useMemo(
    () => suppliersQuery.data?.result.map((s) => s.id) ?? [],
    [suppliersQuery.data],
  );
  const productCodes = useMemo(
    () => productsQuery.data?.result.map((p) => p.code).filter(Boolean) as string[] ?? [],
    [productsQuery.data],
  );
  const { filling: ghostFilling } = useTourGhostFill({
    form,
    context: {
      customerIds: [],
      supplierIds,
      bankAccountIds: [],
      productCodes,
    },
  });

  const supplierName = useMemo(() => {
    const s = suppliersQuery.data?.result.find((x) => x.id === supplierId);
    return s?.name ?? "—";
  }, [suppliersQuery.data, supplierId]);

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
      watchedLines.reduce((acc, l) => acc.plus(dec(l.quantity).times(dec(l.rate))), new Decimal(0)),
    [watchedLines],
  );
  const grandTotal = useMemo(
    () => lineTotals.reduce((acc, v) => acc.plus(v), new Decimal(0)),
    [lineTotals],
  );

  const mutation = useMutation({
    mutationFn: (input: SupplierBillCreateInput) => purchasesApi.createSupplierBill(input),
    onSuccess: async (res) => {
      clearDraftOnSuccess();
      await invalidateTenantQueries(queryClient, "supplier-bills");
      const id = res.result?.id;
      if (res.posted === false && res.postingWarning) {
        setPostingWarning(res.postingWarning);
        if (id) setTimeout(() => router.push(`/purchases/bills/${id}`), 1500);
        return;
      }
      if (id) router.push(`/purchases/bills/${id}`);
      else router.push("/purchases/bills");
    },
    onError: (err) =>
      setSubmitError(err instanceof ApiError ? err.message : "Could not create bill"),
  });

  const onSubmit = form.handleSubmit((values) => {
    if (demoSandbox) return;
    setSubmitError(null);
    setPostingWarning(null);
    mutation.mutate({
      billDate: new Date(values.billDate).toISOString(),
      supplierId: values.supplierId,
      lines: values.lines.map((l) => {
        const row: SupplierBillCreateInput["lines"][number] = {
          productCode: l.productCode || null,
          quantity: l.quantity,
          rate: l.rate,
          gstCode: l.gstCode || null,
          gstRate: l.gstRate || null,
          adtCode: l.adtCode || null,
          fedCode: l.fedCode || null,
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
    if (!lastRateEnabled || !supplierId) return;
    await applyLastRateToLine(
      (field, value) => form.setValue(`lines.${lineIndex}.${field}`, value),
      productCode,
      { partyKind: "supplier", partyId: supplierId, docType: "VI" },
    );
  };

  const loadTemplate = (payload: Record<string, unknown>) => {
    if (typeof payload.billDate === "string") form.setValue("billDate", payload.billDate);
    if (typeof payload.supplierId === "string") form.setValue("supplierId", payload.supplierId);
    if (Array.isArray(payload.lines)) {
      form.setValue("lines", payload.lines as FormValues["lines"]);
    }
    if (payload.smartFilters && typeof payload.smartFilters === "object") {
      form.setValue("smartFilters", payload.smartFilters as FormValues["smartFilters"]);
    }
  };

  return (
    <DocumentWorkspace
      title="New supplier bill"
      breadcrumb="Buy / Bills / New"
      tourRoot="bill-new-header"
      tourSummary="bill-new-summary"
      tourSave="bill-new-save"
      formId="vi-form"
      onSubmit={onSubmit}
      topBanner={topBanner}
      demoSandbox={demoSandbox}
      demoSandboxBanner={<DemoSandboxBanner filling={ghostFilling} />}
      isSaving={mutation.isPending}
      saveLabel="Save bill"
      onCancel={() => router.push("/purchases/bills")}
      grandTotal={grandTotal.toFixed(2)}
      error={submitError}
      warning={postingWarning}
      summaryLines={[
        { label: "Supplier", value: supplierName, emphasis: true },
        { label: "Lines", value: String(watchedLines.length) },
        { label: "Subtotal", value: subtotal.toFixed(2) },
        { label: "Tax", value: grandTotal.minus(subtotal).toFixed(2) },
      ]}
      header={
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2" data-tour="bill-new-header">
          <FormField label="Bill date" required error={form.formState.errors.billDate?.message}>
            <Input type="date" {...form.register("billDate")} />
          </FormField>
          <FormField label="Supplier" required error={form.formState.errors.supplierId?.message}>
            <Select {...form.register("supplierId")}>
              <option value="">Select supplier…</option>
              {suppliersQuery.data?.result.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                  {s.code ? ` (${s.code})` : ""}
                </option>
              ))}
            </Select>
          </FormField>
        </div>
      }
    >
      <TransactionTemplatePicker
        module="supplier_bill"
        onLoad={loadTemplate}
        onCapturePayload={() => ({
          billDate: form.getValues("billDate"),
          supplierId: form.getValues("supplierId"),
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
        showProject={false}
        emptyLine={emptyLine}
        tourTarget="bill-new-lines"
        onProductSelect={handleProductSelect}
        descriptionColumns={descriptionColumns}
        showBatchExpiry
      />
      <section className="mt-6 border-t border-border pt-4">
        <h3 className="mb-3 text-sm font-medium text-fg-muted">Smart filters</h3>
        <SmartDocumentFilters module="purchases" register={form.register} />
      </section>
    </DocumentWorkspace>
  );
}
