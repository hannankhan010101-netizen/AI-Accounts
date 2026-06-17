"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import { useMemo, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useFieldArray, useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import Decimal from "decimal.js";
import { Plus, Trash2 } from "lucide-react";

import { DocumentWorkspace } from "@/components/patterns/document-workspace";
import { GstLineGrid, type GstLineRow } from "@/components/patterns/gst-line-grid";
import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { inventoryApi, partiesApi, settingsApi } from "@/lib/api/tenant";
import { ApiError } from "@/lib/api/client";
import { useCompany } from "@/lib/auth/company-context";
import { hasMeaningfulLineGridDraft } from "@/lib/hooks/document-draft-helpers";
import { useDocumentWorkspaceDraft } from "@/lib/hooks/use-document-workspace-draft";
import { applyLastRateToLine } from "@/lib/document/apply-last-rate";
import {
  useLastRateSettings,
  type LastRateDocType,
} from "@/lib/hooks/use-last-rate-settings";
import {
  useProductDescriptionColumns,
  type ProductDescriptionDocType,
} from "@/lib/hooks/use-product-description-columns";
import { descriptionFieldsFromLine } from "@/lib/hooks/product-description-columns";

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
  ...descriptionLineFields,
});

const gstLineSchema = lineSchema.extend({
  gstCode: z.string().optional(),
  gstRate: z.string().optional(),
  projectCode: z.string().optional(),
});

const schema = z.object({
  date: z.string().min(1, "Required"),
  partyId: z.string().min(1, "Required"),
  lines: z.array(lineSchema).min(1, "At least one line"),
});

const schemaWithGst = z.object({
  date: z.string().min(1, "Required"),
  partyId: z.string().min(1, "Required"),
  lines: z.array(gstLineSchema).min(1, "At least one line"),
});

export type LineGridFormValues = z.infer<typeof schema>;
export type LineGridFormValuesGst = z.infer<typeof schemaWithGst>;

function emptyLine(): GstLineRow {
  return { productCode: "", quantity: "1", rate: "0" };
}

function emptyGstLine(): GstLineRow {
  return { productCode: "", quantity: "1", rate: "0", gstCode: "", gstRate: "", projectCode: "" };
}

function dec(v: string): Decimal {
  if (!v) return new Decimal(0);
  try {
    return new Decimal(v);
  } catch {
    return new Decimal(0);
  }
}

interface LineGridFormProps {
  title: string;
  breadcrumb: string;
  description?: string;
  partyKind: "customer" | "supplier";
  dateLabel: string;
  cancelHref: string;
  successHref: string;
  detailPath?: (id: string) => string;
  draftStorageKey?: string;
  saveLabel?: string;
  /** Show GST columns and tax in summary (planning; API stores qty/rate only until backend extends lines). */
  withGst?: boolean;
  descriptionDocType?: ProductDescriptionDocType;
  lastRateDocType?: LastRateDocType;
  onSubmit: (input: {
    dateISO: string;
    partyId: string;
    lines: {
      productCode?: string | null;
      quantity: string;
      rate: string;
      gstCode?: string | null;
      gstRate?: string | null;
    }[];
  }) => Promise<{ result?: { id?: string }; posted?: boolean; postingWarning?: string | null } | unknown>;
}

export function LineGridForm({
  title,
  breadcrumb,
  description,
  partyKind,
  dateLabel,
  cancelHref,
  successHref,
  detailPath,
  draftStorageKey,
  saveLabel = "Save",
  withGst = false,
  descriptionDocType,
  lastRateDocType,
  onSubmit,
}: LineGridFormProps) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { companyId } = useCompany();
  const draftEnabled = Boolean(draftStorageKey);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [postingWarning, setPostingWarning] = useState<string | null>(null);

  const partiesQuery = useTenantListQuery([partyKind === "customer" ? "customers" : "suppliers"], () =>
      partyKind === "customer" ? partiesApi.listCustomers() : partiesApi.listSuppliers());
  const productsQuery = useTenantListQuery(["products"], () => inventoryApi.listProducts());
  const taxesQuery = useTenantListQuery(["taxes-year-end"], () => settingsApi.getTaxesYearEnd(),
    { enabled: withGst });

  const form = useForm<LineGridFormValuesGst>({
    resolver: zodResolver(withGst ? schemaWithGst : schema),
    defaultValues: {
      date: new Date().toISOString().slice(0, 10),
      partyId: "",
      lines: [withGst ? emptyGstLine() : emptyLine()],
    },
  });

  const lines = useFieldArray({ control: form.control, name: "lines" });
  const watched = form.watch();
  const watchedLines = watched.lines ?? [];

  const { topBanner, clearDraftOnSuccess } = useDocumentWorkspaceDraft({
    scope: draftStorageKey ?? "line-grid-disabled",
    companyId,
    form,
    values: watched,
    enabled: draftEnabled,
    shouldPersist: hasMeaningfulLineGridDraft,
  });

  const lineTotals = useMemo(() => {
    if (!withGst) {
      return watchedLines.map((l) => dec(l.quantity).times(dec(l.rate)));
    }
    return watchedLines.map((l) => {
      const sub = dec(l.quantity).times(dec(l.rate));
      const ratePct = l.gstRate ? dec(l.gstRate) : new Decimal(0);
      const tax = ratePct.gt(0) ? sub.times(ratePct).div(100) : new Decimal(0);
      return sub.plus(tax);
    });
  }, [watchedLines, withGst]);

  const subtotal = useMemo(
    () =>
      watchedLines.reduce((acc, l) => acc.plus(dec(l.quantity).times(dec(l.rate))), new Decimal(0)),
    [watchedLines],
  );

  const grandTotal = useMemo(
    () => lineTotals.reduce((acc, v) => acc.plus(v), new Decimal(0)),
    [lineTotals],
  );

  const partyName = useMemo(() => {
    const p = partiesQuery.data?.result.find((x) => x.id === watched.partyId);
    return p?.name ? String(p.name) : "—";
  }, [partiesQuery.data, watched.partyId]);

  const gstRates = taxesQuery.data?.result?.gstRates ?? [];
  const { columns: descriptionColumns } = useProductDescriptionColumns(
    descriptionDocType ?? "SI",
  );
  const { addEditEnabled: lastRateEnabled } = useLastRateSettings(lastRateDocType ?? "SI");

  const handleProductSelect = useCallback(
    async (lineIndex: number, productCode: string) => {
      if (!lastRateDocType || !lastRateEnabled || !watched.partyId) return;
      await applyLastRateToLine(
        (field, value) => form.setValue(`lines.${lineIndex}.${field}`, value),
        productCode,
        { partyKind, partyId: watched.partyId, docType: lastRateDocType },
      );
    },
    [form, lastRateDocType, lastRateEnabled, partyKind, watched.partyId],
  );

  const mutation = useMutation({
    mutationFn: (values: LineGridFormValuesGst) =>
      onSubmit({
        dateISO: new Date(values.date).toISOString(),
        partyId: values.partyId,
        lines: values.lines.map((l) => {
          const row = {
            productCode: l.productCode || null,
            quantity: l.quantity,
            rate: l.rate,
            ...(withGst
              ? {
                  gstCode: l.gstCode || null,
                  gstRate: l.gstRate ? l.gstRate : null,
                }
              : {}),
            ...(descriptionDocType
              ? (() => {
                  const extra = descriptionFieldsFromLine(
                    l as Record<string, unknown>,
                    descriptionColumns,
                  );
                  return extra ? { descriptionFields: extra } : {};
                })()
              : {}),
          };
          return row;
        }),
      }),
    onSuccess: (res) => {
      if (draftEnabled) clearDraftOnSuccess();
      const r = res as { result?: { id?: string }; posted?: boolean; postingWarning?: string | null };
      const id = r?.result?.id;
      const go = () => {
        if (id && detailPath) router.push(detailPath(id));
        else router.push(successHref);
      };
      void queryClient.invalidateQueries();
      if (r?.posted === false && r.postingWarning) {
        setPostingWarning(r.postingWarning);
        setTimeout(go, 1500);
      } else {
        go();
      }
    },
    onError: (err) =>
      setSubmitError(err instanceof ApiError ? err.message : "Could not save"),
  });

  const handleSubmit = form.handleSubmit((values) => {
    setSubmitError(null);
    setPostingWarning(null);
    mutation.mutate(values);
  });

  const summaryLines = withGst
    ? [
        {
          label: partyKind === "customer" ? "Customer" : "Supplier",
          value: partyName,
          emphasis: true,
        },
        { label: "Lines", value: String(watchedLines.length) },
        { label: "Subtotal", value: subtotal.toFixed(2) },
        { label: "Tax (est.)", value: grandTotal.minus(subtotal).toFixed(2) },
      ]
    : [
        {
          label: partyKind === "customer" ? "Customer" : "Supplier",
          value: partyName,
          emphasis: true,
        },
        { label: "Lines", value: String(watchedLines.length) },
        { label: dateLabel, value: watched.date || "—" },
      ];

  return (
    <DocumentWorkspace
      title={title}
      breadcrumb={breadcrumb}
      formId="line-grid-form"
      onSubmit={handleSubmit}
      isSaving={mutation.isPending}
      saveLabel={saveLabel}
      onCancel={() => router.push(cancelHref)}
      grandTotal={grandTotal.toFixed(2)}
      grandTotalLabel={withGst ? "Total incl. tax (est.)" : "Document total"}
      error={submitError}
      warning={postingWarning}
      topBanner={topBanner}
      summaryLines={summaryLines}
      header={
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <FormField label={dateLabel} required error={form.formState.errors.date?.message}>
            <Input type="date" {...form.register("date")} />
          </FormField>
          <FormField
            label={partyKind === "customer" ? "Customer" : "Supplier"}
            required
            error={form.formState.errors.partyId?.message}
          >
            <Select {...form.register("partyId")}>
              <option value="">Select…</option>
              {partiesQuery.data?.result.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                  {"code" in p && p.code ? ` (${p.code})` : ""}
                </option>
              ))}
            </Select>
          </FormField>
        </div>
      }
    >
      {description ? <p className="mb-3 text-sm text-fg-muted">{description}</p> : null}
      {withGst ? (
        <>
          <p className="mb-3 text-xs text-fg-muted">
            GST is saved on this document for planning and carries through on conversion to invoice or bill.
          </p>
          <GstLineGrid
            form={form}
            lines={lines}
            lineTotals={lineTotals}
            products={productsQuery.data?.result}
            gstRates={gstRates}
            showProject={false}
            emptyLine={emptyGstLine}
            descriptionColumns={descriptionDocType ? descriptionColumns : []}
            onProductSelect={lastRateDocType && lastRateEnabled ? handleProductSelect : undefined}
          />
        </>
      ) : (
        <>
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-fg">Lines</h2>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => lines.append(emptyLine())}
            >
              <Plus className="mr-1 h-4 w-4" /> Add line
            </Button>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left text-xs uppercase text-fg-muted">
                  <th className="py-2 pr-3">Product</th>
                  <th className="py-2 pr-3 text-right">Quantity</th>
                  <th className="py-2 pr-3 text-right">Rate</th>
                  <th className="py-2 pr-3 text-right">Line total</th>
                  <th className="py-2" />
                </tr>
              </thead>
              <tbody>
                {lines.fields.map((field, i) => (
                  <tr key={field.id} className="border-b border-border">
                    <td className="py-1 pr-3">
                      <Select className="h-8" {...form.register(`lines.${i}.productCode` as const)}>
                        <option value="">— no product —</option>
                        {productsQuery.data?.result.map((p) => (
                          <option key={p.id} value={p.code ?? ""}>
                            {p.code ? `${p.code} — ` : ""}
                            {p.name}
                          </option>
                        ))}
                      </Select>
                    </td>
                    <td className="py-1 pr-3">
                      <Input
                        inputMode="decimal"
                        className="h-8 w-24 text-right tabular-nums"
                        {...form.register(`lines.${i}.quantity` as const)}
                      />
                    </td>
                    <td className="py-1 pr-3">
                      <Input
                        inputMode="decimal"
                        className="h-8 w-32 text-right tabular-nums"
                        {...form.register(`lines.${i}.rate` as const)}
                      />
                    </td>
                    <td className="py-1 pr-3 text-right tabular-nums">
                      {lineTotals[i]?.toFixed(2) ?? "0.00"}
                    </td>
                    <td className="py-1">
                      <button
                        type="button"
                        onClick={() => lines.remove(i)}
                        disabled={lines.fields.length <= 1}
                        aria-label="Remove line"
                        className="rounded p-1 text-fg-muted hover:bg-status-danger/10 hover:text-status-danger disabled:opacity-30"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </DocumentWorkspace>
  );
}
