/** Edit draft sales invoice — catalog §5.4 */
"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useFieldArray, useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import Decimal from "decimal.js";

import { DocumentWorkspace } from "@/components/patterns/document-workspace";
import { GstLineGrid, type GstLineRow } from "@/components/patterns/gst-line-grid";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { DetailPageLoading } from "@/components/ui/detail-page-loading";
import {
  inventoryApi,
  partiesApi,
  salesApi,
  settingsApi,
  type SalesInvoiceCreateInput,
} from "@/lib/api/tenant";
import { ApiError } from "@/lib/api/client";
import { useCompany } from "@/lib/auth/company-context";
import { salesInvoiceToFormValues } from "@/lib/document-form-mappers";
import { applyLastRateToLine } from "@/lib/document/apply-last-rate";
import { hasMeaningfulLineGridDraft } from "@/lib/hooks/document-draft-helpers";
import { useDocumentWorkspaceDraft } from "@/lib/hooks/use-document-workspace-draft";
import { useLastRateSettings } from "@/lib/hooks/use-last-rate-settings";
import {
  useProductDescriptionColumns,
} from "@/lib/hooks/use-product-description-columns";
import { descriptionFieldsFromLine } from "@/lib/hooks/product-description-columns";

import { invalidateTenantQueries, useTenantListQuery, useTenantDetailQuery } from "@/lib/api/tenant-query";

const descriptionLineFields = {
  description: z.string().optional(),
  text1: z.string().optional(),
  text2: z.string().optional(),
  text3: z.string().optional(),
  text4: z.string().optional(),
  text5: z.string().optional(),
  text6: z.string().optional(),
};

const lineSchema = z.object({
  productCode: z.string().optional(),
  quantity: z.string().regex(/^\d+(\.\d+)?$/u, "Positive number"),
  rate: z.string().regex(/^\d+(\.\d+)?$/u, "Positive number"),
  gstCode: z.string().optional(),
  gstRate: z.string().optional(),
  projectCode: z.string().optional(),
  batchNumber: z.string().optional(),
  expiryDate: z.string().optional(),
  ...descriptionLineFields,
});

const schema = z.object({
  invoiceDate: z.string().min(1, "Required"),
  customerId: z.string().min(1, "Required"),
  lines: z.array(lineSchema).min(1, "At least one line"),
});
type FormValues = z.infer<typeof schema>;

function emptyLine(): GstLineRow {
  return {
    productCode: "",
    quantity: "1",
    rate: "0",
    gstCode: "",
    gstRate: "",
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

export default function EditSalesInvoicePage() {
  const router = useRouter();
  const params = useParams<{ id: string }>();
  const invoiceId = params.id;
  const queryClient = useQueryClient();
  const { companyId } = useCompany();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [hydrated, setHydrated] = useState(false);

  const invoiceQuery = useTenantDetailQuery(["sales-invoice", invoiceId], () => salesApi.getInvoice(invoiceId), { enabled: Boolean(invoiceId) });

  const customersQuery = useTenantListQuery(["customers"], () => partiesApi.listCustomers());
  const productsQuery = useTenantListQuery(["products"], () => inventoryApi.listProducts());
  const taxesQuery = useTenantListQuery(["taxes-year-end"], () => settingsApi.getTaxesYearEnd());
  const gstRates = taxesQuery.data?.result?.gstRates ?? [];
  const { columns: descriptionColumns } = useProductDescriptionColumns("SI");
  const { addEditEnabled: lastRateEnabled } = useLastRateSettings("SI");

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

  useEffect(() => {
    const inv = invoiceQuery.data?.result;
    if (!inv || hydrated) return;
    if (inv.status !== "draft") {
      router.replace(`/sales/invoices/${invoiceId}`);
      return;
    }
    form.reset(salesInvoiceToFormValues(inv));
    setHydrated(true);
  }, [invoiceQuery.data, form, hydrated, invoiceId, router]);

  const { topBanner, clearDraftOnSuccess } = useDocumentWorkspaceDraft({
    scope: `sales-invoice-edit:${invoiceId}`,
    companyId,
    form,
    values: watched,
    enabled: hydrated,
    shouldPersist: hasMeaningfulLineGridDraft,
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
    mutationFn: (input: SalesInvoiceCreateInput) =>
      salesApi.updateInvoice(invoiceId, input),
    onSuccess: async () => {
      clearDraftOnSuccess();
      await invalidateTenantQueries(queryClient, "sales-invoices");
      await invalidateTenantQueries(queryClient, "sales-invoice", invoiceId);
      router.push(`/sales/invoices/${invoiceId}`);
    },
    onError: (err) =>
      setSubmitError(err instanceof ApiError ? err.message : "Could not update invoice"),
  });

  const onSubmit = form.handleSubmit((values) => {
    setSubmitError(null);
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
          projectCode: l.projectCode || null,
        };
        if (l.batchNumber?.trim()) row.batchNumber = l.batchNumber.trim();
        if (l.expiryDate?.trim()) row.expiryDate = new Date(l.expiryDate).toISOString();
        const extra = descriptionFieldsFromLine(l as Record<string, unknown>, descriptionColumns);
        if (extra) row.descriptionFields = extra;
        return row;
      }),
    });
  });

  if (invoiceQuery.isLoading || !hydrated) {
    return <DetailPageLoading />;
  }
  if (invoiceQuery.error instanceof Error) {
    return (
      <div className="rounded-md border border-status-danger/30 bg-status-danger/10 p-3 text-sm text-status-danger">
        {invoiceQuery.error.message}
      </div>
    );
  }

  const inv = invoiceQuery.data?.result;
  const docNo = inv?.documentNumber ?? invoiceId;

  return (
    <DocumentWorkspace
      title={`Edit invoice ${docNo}`}
      breadcrumb={`Sell / Invoices / ${docNo} / Edit`}
      formId="si-edit-form"
      onSubmit={onSubmit}
      topBanner={topBanner}
      isSaving={mutation.isPending}
      saveLabel="Save changes"
      onCancel={() => router.push(`/sales/invoices/${invoiceId}`)}
      grandTotal={grandTotal.toFixed(2)}
      grandTotalLabel="Total incl. tax"
      error={submitError}
      summaryLines={[
        { label: "Customer", value: customerName, emphasis: true },
        { label: "Lines", value: String(watchedLines.length) },
        { label: "Subtotal", value: subtotal.toFixed(2) },
        { label: "Tax", value: grandTotal.minus(subtotal).toFixed(2) },
      ]}
      header={
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
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
      <GstLineGrid
        form={form}
        lines={lines}
        lineTotals={lineTotals}
        products={productsQuery.data?.result}
        gstRates={gstRates}
        emptyLine={emptyLine}
        showBatchExpiry
        descriptionColumns={descriptionColumns}
        onProductSelect={
          lastRateEnabled && customerId
            ? async (lineIndex, productCode) => {
                await applyLastRateToLine(
                  (field, value) => form.setValue(`lines.${lineIndex}.${field}`, value),
                  productCode,
                  { partyKind: "customer", partyId: customerId, docType: "SI" },
                );
              }
            : undefined
        }
      />
    </DocumentWorkspace>
  );
}
