/** Batch sales invoice entry — FA §3.9 / §5.4 */
"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useFieldArray, useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import {
  BatchEntryGrid,
  type BatchEntryRow,
} from "@/components/patterns/batch-entry-grid";
import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import {
  inventoryApi,
  partiesApi,
  salesApi,
  settingsApi,
} from "@/lib/api/tenant";
import { ApiError } from "@/lib/api/client";
import { invalidateTenantQueries, useTenantListQuery } from "@/lib/api/tenant-query";

const entrySchema = z.object({
  partyId: z.string().min(1, "Required"),
  productCode: z.string().optional(),
  quantity: z.string().regex(/^\d+(\.\d+)?$/u, "Positive number"),
  rate: z.string().regex(/^\d+(\.\d+)?$/u, "Positive number"),
  gstCode: z.string().optional(),
  gstRate: z.string().optional(),
});

const schema = z.object({
  invoiceDate: z.string().min(1, "Required"),
  entries: z.array(entrySchema).min(1, "At least one row"),
});
type FormValues = z.infer<typeof schema>;

function emptyRow(): BatchEntryRow {
  return { partyId: "", productCode: "", quantity: "1", rate: "0", gstCode: "", gstRate: "" };
}

export default function BatchSalesInvoicesPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  const customersQuery = useTenantListQuery(["customers"], () => partiesApi.listCustomers());
  const productsQuery = useTenantListQuery(["products"], () => inventoryApi.listProducts());
  const taxesQuery = useTenantListQuery(["taxes-year-end"], () => settingsApi.getTaxesYearEnd());

  const parties = useMemo(
    () =>
      (customersQuery.data?.result ?? []).map((c) => ({
        id: c.id,
        label: c.code ? `${c.name} (${c.code})` : c.name,
      })),
    [customersQuery.data],
  );

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      invoiceDate: new Date().toISOString().slice(0, 10),
      entries: [emptyRow()],
    },
  });
  const entries = useFieldArray({ control: form.control, name: "entries" });
  const gstRates = taxesQuery.data?.result?.gstRates ?? [];

  const onSubmit = form.handleSubmit(async (values) => {
    setSubmitError(null);
    setIsSaving(true);
    try {
      const res = await salesApi.createBatchInvoices({
        invoiceDate: new Date(values.invoiceDate).toISOString(),
        entries: values.entries.map((row) => ({
          customerId: row.partyId,
          productCode: row.productCode || null,
          quantity: row.quantity,
          rate: row.rate,
          gstCode: row.gstCode || null,
          gstRate: row.gstRate || null,
        })),
      });
      await invalidateTenantQueries(queryClient, "sales-invoices");
      if (res.result.created.length === 1) {
        router.push(`/sales/invoices/${res.result.created[0].id}`);
      } else {
        router.push("/sales/invoices");
      }
    } catch (err) {
      setSubmitError(err instanceof ApiError ? err.message : "Batch save failed");
    } finally {
      setIsSaving(false);
    }
  });

  return (
    <div className="space-y-4">
      <PageHeader
        title="Batch sales invoices"
        breadcrumb="Sell / Invoices / Batch"
        description="Enter many lines at once. Rows are grouped by customer into separate draft invoices."
        actions={
          <>
            <Button type="button" variant="outline" onClick={() => router.push("/sales/invoices")}>
              Cancel
            </Button>
            <Button type="submit" form="batch-si-form" disabled={isSaving}>
              {isSaving ? "Saving…" : "Save batch"}
            </Button>
          </>
        }
      />
      <form
        id="batch-si-form"
        onSubmit={onSubmit}
        className="space-y-4 rounded-lg border border-border bg-surface p-6"
      >
        <FormField label="Invoice date" required error={form.formState.errors.invoiceDate?.message}>
          <Input type="date" className="max-w-xs" {...form.register("invoiceDate")} />
        </FormField>
        <BatchEntryGrid
          form={form}
          entries={entries}
          partyLabel="Customer"
          parties={parties}
          products={productsQuery.data?.result}
          gstRates={gstRates}
          emptyRow={emptyRow}
        />
        {submitError ? (
          <div className="rounded-md border border-status-danger/30 bg-status-danger/10 px-3 py-2 text-sm text-status-danger">
            {submitError}
          </div>
        ) : null}
      </form>
    </div>
  );
}
