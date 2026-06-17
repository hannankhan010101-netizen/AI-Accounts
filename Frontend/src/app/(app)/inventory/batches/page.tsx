/** Product Batches — catalog §7.8. */
"use client";
import { useTenantListQuery, invalidateTenantQueries } from "@/lib/api/tenant-query";


import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { Button } from "@/components/ui/button";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { buildGridExport } from "@/lib/export/grid-export";
import { ListToolbar } from "@/components/ui/list-toolbar";
import { useClientList } from "@/lib/hooks/use-client-list";
import { useConfiguredListColumns } from "@/lib/hooks/use-configured-list-columns";
import { matchText } from "@/lib/list/document-list-filters";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import { PageHeader } from "@/components/ui/page-header";
import {
  inventoryWritesApi,
  type ProductBatch,
  type ProductBatchCreateInput,
} from "@/lib/api/tenant";

const schema = z.object({
  productCode: z.string().min(1),
  batchNumber: z.string().min(1),
  expiryDate: z.string().optional(),
  quantityOnHand: z.string().regex(/^\d+(\.\d+)?$/u),
  notes: z.string().optional(),
});
type FormValues = z.infer<typeof schema>;

export default function ProductBatchesPage() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { data, isLoading, error: queryError } = useTenantListQuery(["product-batches"], () => inventoryWritesApi.listBatches());

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows: data?.result,
    syncUrl: true,
    filterFn: (r, q) => matchText([r.productCode, r.batchNumber, r.notes], q),
  });

  const baseColumns = useMemo(
    () =>
      responsiveListColumns<ProductBatch>([
        { key: "productCode", header: "Product" },
        { key: "batchNumber", header: "Batch" },
        {
          key: "expiryDate",
          header: "Expiry",
          render: (r) =>
            r.expiryDate ? new Date(r.expiryDate).toLocaleDateString() : "—",
        },
        { key: "quantityOnHand", header: "On hand", align: "right" },
        { key: "notes", header: "Notes" },
      ]),
    [],
  );
  const columns = useConfiguredListColumns("product-batches", baseColumns);

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { productCode: "", batchNumber: "", expiryDate: "", quantityOnHand: "0", notes: "" },
  });

  const mutation = useMutation({
    mutationFn: (input: ProductBatchCreateInput) => inventoryWritesApi.createBatch(input),
    onSuccess: () => {
      setOpen(false);
      form.reset();
      invalidateTenantQueries(qc, "product-batches");
    },
    onError: (err) => setError(err instanceof Error ? err.message : "Could not save"),
  });

  return (
    <div>
      <PageHeader
        title="Batches and expiry"
        breadcrumb="Stock / Batches"
        actions={<Button onClick={() => setOpen(true)}>New batch</Button>}
      />
      <ListToolbar search={search} onSearchChange={setSearch} />
      <EnterpriseGrid<ProductBatch>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        error={queryError}
        emptyMessage="No batches yet."
        pagination={pagination}
        exportCsv={{ ...buildGridExport("product-batches", columns), rows: filtered }}
      />

      <Modal
        open={open}
        title="New batch"
        onClose={() => setOpen(false)}
        footer={
          <>
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" form="batch-form" disabled={mutation.isPending}>
              {mutation.isPending ? "Saving…" : "Save"}
            </Button>
          </>
        }
      >
        <form
          id="batch-form"
          onSubmit={form.handleSubmit((v) =>
            mutation.mutate({
              productCode: v.productCode,
              batchNumber: v.batchNumber,
              expiryDate: v.expiryDate ? new Date(v.expiryDate).toISOString() : null,
              quantityOnHand: v.quantityOnHand,
              notes: v.notes || null,
            }),
          )}
          className="space-y-3"
        >
          <FormField label="Product code" required>
            <Input {...form.register("productCode")} />
          </FormField>
          <FormField label="Batch number" required>
            <Input {...form.register("batchNumber")} />
          </FormField>
          <FormField label="Expiry date">
            <Input type="date" {...form.register("expiryDate")} />
          </FormField>
          <FormField label="Quantity on hand">
            <Input inputMode="decimal" {...form.register("quantityOnHand")} />
          </FormField>
          <FormField label="Notes">
            <Input {...form.register("notes")} />
          </FormField>
          {error && (
            <div className="rounded-md border border-status-danger/30 bg-status-danger/10 px-3 py-2 text-sm text-status-danger">
              {error}
            </div>
          )}
        </form>
      </Modal>
    </div>
  );
}
