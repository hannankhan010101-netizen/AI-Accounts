/** New stock adjustment — catalog §7.3. */
"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useFieldArray, useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import Decimal from "decimal.js";

import { DocumentWorkspace } from "@/components/patterns/document-workspace";
import { ProductLinesEditor } from "@/components/patterns/product-lines-editor";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { inventoryApi, inventoryWritesApi, type StockAdjustmentCreateInput } from "@/lib/api/tenant";
import { ApiError } from "@/lib/api/client";
import { useCompany } from "@/lib/auth/company-context";
import { useDocumentWorkspaceDraft } from "@/lib/hooks/use-document-workspace-draft";

const lineSchema = z.object({
  productCode: z.string().min(1, "Required"),
  locationCode: z.string().optional(),
  quantityDelta: z.string().regex(/^-?\d+(\.\d+)?$/u, "Numeric"),
  unitCost: z.string().regex(/^\d+(\.\d+)?$/u, "Numeric").optional(),
});

const schema = z.object({
  adjustmentDate: z.string().min(1),
  reason: z.string().min(1).default("adjustment"),
  notes: z.string().optional(),
  lines: z.array(lineSchema).min(1, "At least one line"),
});
type FormValues = z.infer<typeof schema>;

function emptyLine() {
  return { productCode: "", locationCode: "", quantityDelta: "0", unitCost: "0" };
}

export default function NewStockAdjustmentPage() {
  const router = useRouter();
  const { companyId } = useCompany();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const productsQuery = useTenantListQuery(["products"], () => inventoryApi.listProducts());

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      adjustmentDate: new Date().toISOString().slice(0, 10),
      reason: "adjustment",
      notes: "",
      lines: [emptyLine()],
    },
  });
  const lines = useFieldArray({ control: form.control, name: "lines" });
  const watched = form.watch();
  const watchedLines = watched.lines ?? [];

  const { topBanner, clearDraftOnSuccess } = useDocumentWorkspaceDraft({
    scope: "stock-adjustment-new",
    companyId,
    form,
    values: watched,
    shouldPersist: (v) =>
      Boolean(v.notes?.trim()) ||
      v.reason !== "adjustment" ||
      v.lines?.some((l) => l.productCode || l.quantityDelta !== "0"),
  });

  const lineCount = watchedLines.length;
  const totalDelta = useMemo(
    () =>
      watchedLines.reduce((acc, l) => {
        try {
          return acc.plus(new Decimal(l.quantityDelta || "0"));
        } catch {
          return acc;
        }
      }, new Decimal(0)),
    [watchedLines],
  );

  const mutation = useMutation({
    mutationFn: (input: StockAdjustmentCreateInput) =>
      inventoryWritesApi.createStockAdjustment(input),
    onSuccess: () => {
      clearDraftOnSuccess();
      router.push("/inventory/stock-adjustment");
    },
    onError: (err) => setSubmitError(err instanceof ApiError ? err.message : "Could not save"),
  });

  const onSubmit = form.handleSubmit((values) => {
    setSubmitError(null);
    mutation.mutate({
      adjustmentDate: new Date(values.adjustmentDate).toISOString(),
      reason: values.reason,
      notes: values.notes || null,
      lines: values.lines.map((l) => ({
        productCode: l.productCode,
        locationCode: l.locationCode || null,
        quantityDelta: l.quantityDelta,
        unitCost: l.unitCost || "0",
      })),
    });
  });

  return (
    <DocumentWorkspace
      title="New stock adjustment"
      breadcrumb="Stock / Adjustments / New"
      topBanner={topBanner}
      formId="sa-form"
      onSubmit={onSubmit}
      isSaving={mutation.isPending}
      onCancel={() => router.push("/inventory/stock-adjustment")}
      grandTotal={totalDelta.toFixed(2)}
      grandTotalLabel="Net quantity Δ"
      error={submitError}
      summaryLines={[
        { label: "Reason", value: form.watch("reason") || "—" },
        { label: "Lines", value: String(lineCount) },
      ]}
      header={
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <FormField label="Date" required>
            <Input type="date" {...form.register("adjustmentDate")} />
          </FormField>
          <FormField label="Reason">
            <Select {...form.register("reason")}>
              <option value="adjustment">Adjustment</option>
              <option value="writeoff">Write-off</option>
              <option value="opening">Opening stock</option>
              <option value="damage">Damage</option>
            </Select>
          </FormField>
          <FormField label="Notes">
            <Input {...form.register("notes")} />
          </FormField>
        </div>
      }
    >
      <p className="mb-3 text-sm text-fg-muted">
        Positive quantity delta increases stock; negative decreases.
      </p>
      <ProductLinesEditor
        form={form}
        lines={lines}
        products={productsQuery.data?.result}
        emptyLine={emptyLine}
        fields={[
          { kind: "product", name: "productCode" },
          { kind: "text", name: "locationCode", label: "Location", placeholder: "Optional" },
          {
            kind: "text",
            name: "quantityDelta",
            label: "Δ Qty",
            align: "right",
            inputMode: "decimal",
            widthClass: "w-24",
          },
          {
            kind: "text",
            name: "unitCost",
            label: "Unit cost",
            align: "right",
            inputMode: "decimal",
            widthClass: "w-28",
          },
        ]}
      />
    </DocumentWorkspace>
  );
}
