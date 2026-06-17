/** New stock transfer — catalog §7.2. */
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
import { inventoryApi, inventoryWritesApi, type StockTransferCreateInput } from "@/lib/api/tenant";
import { ApiError } from "@/lib/api/client";
import { useCompany } from "@/lib/auth/company-context";
import { useDocumentWorkspaceDraft } from "@/lib/hooks/use-document-workspace-draft";

const lineSchema = z.object({
  productCode: z.string().min(1, "Required"),
  quantity: z.string().regex(/^\d+(\.\d+)?$/u, "Positive"),
  unitCost: z.string().regex(/^\d+(\.\d+)?$/u, "Numeric").optional(),
});
const schema = z
  .object({
    transferDate: z.string().min(1),
    fromLocationCode: z.string().min(1, "Required"),
    toLocationCode: z.string().min(1, "Required"),
    notes: z.string().optional(),
    lines: z.array(lineSchema).min(1),
  })
  .refine((v) => v.fromLocationCode !== v.toLocationCode, {
    message: "From and To must differ",
    path: ["toLocationCode"],
  });
type FormValues = z.infer<typeof schema>;

function emptyLine() {
  return { productCode: "", quantity: "1", unitCost: "0" };
}

export default function NewStockTransferPage() {
  const router = useRouter();
  const { companyId } = useCompany();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const productsQuery = useTenantListQuery(["products"], () => inventoryApi.listProducts());

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      transferDate: new Date().toISOString().slice(0, 10),
      fromLocationCode: "",
      toLocationCode: "",
      notes: "",
      lines: [emptyLine()],
    },
  });
  const lines = useFieldArray({ control: form.control, name: "lines" });
  const watched = form.watch();
  const watchedLines = watched.lines ?? [];

  const { topBanner, clearDraftOnSuccess } = useDocumentWorkspaceDraft({
    scope: "stock-transfer-new",
    companyId,
    form,
    values: watched,
    shouldPersist: (v) =>
      Boolean(v.fromLocationCode) ||
      Boolean(v.toLocationCode) ||
      Boolean(v.notes?.trim()) ||
      v.lines?.some((l) => l.productCode || l.quantity !== "1"),
  });

  const totalQty = useMemo(
    () =>
      watchedLines.reduce((acc, l) => {
        try {
          return acc.plus(new Decimal(l.quantity || "0"));
        } catch {
          return acc;
        }
      }, new Decimal(0)),
    [watchedLines],
  );

  const mutation = useMutation({
    mutationFn: (input: StockTransferCreateInput) =>
      inventoryWritesApi.createStockTransfer(input),
    onSuccess: () => {
      clearDraftOnSuccess();
      router.push("/inventory/stock-transfer");
    },
    onError: (err) => setSubmitError(err instanceof ApiError ? err.message : "Could not save"),
  });

  const onSubmit = form.handleSubmit((values) => {
    setSubmitError(null);
    mutation.mutate({
      transferDate: new Date(values.transferDate).toISOString(),
      fromLocationCode: values.fromLocationCode,
      toLocationCode: values.toLocationCode,
      notes: values.notes || null,
      lines: values.lines.map((l) => ({
        productCode: l.productCode,
        quantity: l.quantity,
        unitCost: l.unitCost || "0",
      })),
    });
  });

  return (
    <DocumentWorkspace
      title="New stock transfer"
      breadcrumb="Stock / Transfers / New"
      topBanner={topBanner}
      formId="st-form"
      onSubmit={onSubmit}
      isSaving={mutation.isPending}
      onCancel={() => router.push("/inventory/stock-transfer")}
      grandTotal={totalQty.toFixed(2)}
      grandTotalLabel="Total quantity"
      error={submitError}
      summaryLines={[
        { label: "From", value: form.watch("fromLocationCode") || "—", emphasis: true },
        { label: "To", value: form.watch("toLocationCode") || "—", emphasis: true },
        { label: "Lines", value: String(watchedLines.length) },
      ]}
      header={
        <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
          <FormField label="Date" required>
            <Input type="date" {...form.register("transferDate")} />
          </FormField>
          <FormField
            label="From location"
            required
            error={form.formState.errors.fromLocationCode?.message}
          >
            <Input {...form.register("fromLocationCode")} />
          </FormField>
          <FormField
            label="To location"
            required
            error={form.formState.errors.toLocationCode?.message}
          >
            <Input {...form.register("toLocationCode")} />
          </FormField>
          <FormField label="Notes">
            <Input {...form.register("notes")} />
          </FormField>
        </div>
      }
    >
      <ProductLinesEditor
        form={form}
        lines={lines}
        products={productsQuery.data?.result}
        emptyLine={emptyLine}
        fields={[
          { kind: "product", name: "productCode" },
          {
            kind: "text",
            name: "quantity",
            label: "Quantity",
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
