/** New delivery note — catalog §5.6. */
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
import {
  deliveryApi,
  inventoryApi,
  partiesApi,
  type DeliveryNoteCreateInput,
  type DeliverySource,
} from "@/lib/api/tenant";
import { ApiError } from "@/lib/api/client";
import { useCompany } from "@/lib/auth/company-context";
import { useDocumentWorkspaceDraft } from "@/lib/hooks/use-document-workspace-draft";

const lineSchema = z.object({
  productCode: z.string().optional(),
  quantity: z.string().regex(/^\d+(\.\d+)?$/u),
  notes: z.string().optional(),
});
const schema = z.object({
  deliveryDate: z.string().min(1),
  customerId: z.string().min(1),
  sourceKind: z.enum(["GDNSI", "GDNSO", "manual"]),
  sourceId: z.string().optional(),
  notes: z.string().optional(),
  lines: z.array(lineSchema).min(1),
});
type FormValues = z.infer<typeof schema>;

function emptyLine() {
  return { productCode: "", quantity: "1", notes: "" };
}

export default function NewDeliveryNotePage() {
  const router = useRouter();
  const { companyId } = useCompany();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const customersQuery = useTenantListQuery(["customers"], () => partiesApi.listCustomers());
  const productsQuery = useTenantListQuery(["products"], () => inventoryApi.listProducts());

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      deliveryDate: new Date().toISOString().slice(0, 10),
      customerId: "",
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
    scope: "delivery-note-new",
    companyId,
    form,
    values: watched,
    shouldPersist: (v) =>
      Boolean(v.customerId) ||
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

  const customerName = useMemo(() => {
    const c = customersQuery.data?.result.find((x) => x.id === form.watch("customerId"));
    return c?.name ?? "—";
  }, [customersQuery.data, form.watch("customerId")]);

  const mutation = useMutation({
    mutationFn: (input: DeliveryNoteCreateInput) => deliveryApi.createDeliveryNote(input),
    onSuccess: () => {
      clearDraftOnSuccess();
      router.push("/sales/delivery-notes");
    },
    onError: (err) => setSubmitError(err instanceof ApiError ? err.message : "Could not save"),
  });

  const onSubmit = form.handleSubmit((v) => {
    setSubmitError(null);
    mutation.mutate({
      deliveryDate: new Date(v.deliveryDate).toISOString(),
      customerId: v.customerId,
      sourceKind: v.sourceKind as DeliverySource,
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
      title="New delivery note"
      breadcrumb="Sell / Delivery notes / New"
      topBanner={topBanner}
      formId="dn-form"
      onSubmit={onSubmit}
      isSaving={mutation.isPending}
      onCancel={() => router.push("/sales/delivery-notes")}
      grandTotal={totalQty.toFixed(2)}
      grandTotalLabel="Total quantity"
      error={submitError}
      summaryLines={[
        { label: "Customer", value: customerName, emphasis: true },
        { label: "Source", value: form.watch("sourceKind") },
        { label: "Lines", value: String(watchedLines.length) },
      ]}
      header={
        <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
          <FormField label="Delivery date" required>
            <Input type="date" {...form.register("deliveryDate")} />
          </FormField>
          <FormField label="Customer" required>
            <Select {...form.register("customerId")}>
              <option value="">Select…</option>
              {customersQuery.data?.result.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </Select>
          </FormField>
          <FormField label="Source kind">
            <Select {...form.register("sourceKind")}>
              <option value="manual">Manual</option>
              <option value="GDNSI">From invoice (GDNSI)</option>
              <option value="GDNSO">From order (GDNSO)</option>
            </Select>
          </FormField>
          <FormField label="Source ID (optional)">
            <Input placeholder="Invoice or order id" {...form.register("sourceId")} />
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
