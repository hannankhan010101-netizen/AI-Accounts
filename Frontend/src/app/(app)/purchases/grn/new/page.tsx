/** New GRN — catalog §6. */
"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import { useMemo, useState } from "react";
import { useCompany } from "@/lib/auth/company-context";
import { useDocumentWorkspaceDraft } from "@/lib/hooks/use-document-workspace-draft";
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
import {
  deliveryApi,
  inventoryApi,
  partiesApi,
  type GoodsReceiptNoteCreateInput,
  type GrnSource,
} from "@/lib/api/tenant";
import { ApiError } from "@/lib/api/client";

const lineSchema = z.object({
  productCode: z.string().optional(),
  quantity: z.string().regex(/^\d+(\.\d+)?$/u),
  notes: z.string().optional(),
});
const schema = z.object({
  receiptDate: z.string().min(1),
  supplierId: z.string().min(1),
  sourceKind: z.enum(["GRNPO", "GRNVI", "manual"]),
  sourceId: z.string().optional(),
  notes: z.string().optional(),
  lines: z.array(lineSchema).min(1),
});
type FormValues = z.infer<typeof schema>;

function emptyLine() {
  return { productCode: "", quantity: "1", notes: "" };
}

export default function NewGrnPage() {
  const router = useRouter();
  const { companyId } = useCompany();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const suppliersQuery = useTenantListQuery(["suppliers"], () => partiesApi.listSuppliers());
  const productsQuery = useTenantListQuery(["products"], () => inventoryApi.listProducts());

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      receiptDate: new Date().toISOString().slice(0, 10),
      supplierId: "",
      sourceKind: "manual",
      sourceId: "",
      notes: "",
      lines: [emptyLine()],
    },
  });
  const lines = useFieldArray({ control: form.control, name: "lines" });
  const watched = form.watch();
  const watchedLines = watched.lines ?? [];

  const { topBanner, clearDraftOnSuccess } = useDocumentWorkspaceDraft({
    scope: "grn-new",
    companyId,
    form,
    values: watched,
    shouldPersist: (v) =>
      Boolean(v.supplierId) ||
      Boolean(v.notes?.trim()) ||
      v.lines?.some((l) => l.productCode || l.quantity !== "1" || l.notes),
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

  const supplierName = useMemo(() => {
    const s = suppliersQuery.data?.result.find((x) => x.id === form.watch("supplierId"));
    return s?.name ?? "—";
  }, [suppliersQuery.data, form.watch("supplierId")]);

  const mutation = useMutation({
    mutationFn: (input: GoodsReceiptNoteCreateInput) => deliveryApi.createGrn(input),
    onSuccess: () => {
      clearDraftOnSuccess();
      router.push("/purchases/grn");
    },
    onError: (err) => setSubmitError(err instanceof ApiError ? err.message : "Could not save"),
  });

  const onSubmit = form.handleSubmit((v) => {
    setSubmitError(null);
    mutation.mutate({
      receiptDate: new Date(v.receiptDate).toISOString(),
      supplierId: v.supplierId,
      sourceKind: v.sourceKind as GrnSource,
      sourceId: v.sourceId || null,
      notes: v.notes || null,
      lines: v.lines.map((l) => ({
        productCode: l.productCode || null,
        quantity: l.quantity,
        notes: l.notes || null,
      })),
    });
  });

  return (
    <DocumentWorkspace
      title="New goods receipt note"
      breadcrumb="Buy / GRN / New"
      topBanner={topBanner}
      formId="grn-form"
      onSubmit={onSubmit}
      isSaving={mutation.isPending}
      onCancel={() => router.push("/purchases/grn")}
      grandTotal={totalQty.toFixed(2)}
      grandTotalLabel="Total quantity"
      error={submitError}
      summaryLines={[
        { label: "Supplier", value: supplierName, emphasis: true },
        { label: "Source", value: form.watch("sourceKind") },
        { label: "Lines", value: String(watchedLines.length) },
      ]}
      header={
        <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
          <FormField label="Receipt date" required>
            <Input type="date" {...form.register("receiptDate")} />
          </FormField>
          <FormField label="Supplier" required>
            <Select {...form.register("supplierId")}>
              <option value="">Select…</option>
              {suppliersQuery.data?.result.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </Select>
          </FormField>
          <FormField label="Source kind">
            <Select {...form.register("sourceKind")}>
              <option value="manual">Manual</option>
              <option value="GRNPO">From PO (GRNPO)</option>
              <option value="GRNVI">From Bill (GRNVI)</option>
            </Select>
          </FormField>
          <FormField label="Source ID (optional)">
            <Input placeholder="PO or bill id" {...form.register("sourceId")} />
          </FormField>
        </div>
      }
    >
      <ProductLinesEditor
        form={form}
        lines={lines}
        products={productsQuery.data?.result}
        productOptional
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
          { kind: "text", name: "notes", label: "Notes" },
        ]}
      />
    </DocumentWorkspace>
  );
}
