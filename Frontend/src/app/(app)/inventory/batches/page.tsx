/** Product Batches — catalog §7.8. */
"use client";
import { useTenantListQuery, invalidateTenantQueries } from "@/lib/api/tenant-query";
import { useTenantReferenceQuery } from "@/lib/api/tenant-query";

import { useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { buildGridExport } from "@/lib/export/grid-export";
import { ListToolbar } from "@/components/ui/list-toolbar";
import { useClientList } from "@/lib/hooks/use-client-list";
import { useConfiguredListColumns } from "@/lib/hooks/use-configured-list-columns";
import { matchText } from "@/lib/list/document-list-filters";
import {
  getExpiryStatus,
  EXPIRY_ALERT_WINDOW_DAYS,
  matchesExpiryFilter,
  sortBatchesByExpiryUrgency,
} from "@/lib/inventory/expiry-status";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import { PageHeader } from "@/components/ui/page-header";
import {
  inventoryWritesApi,
  settingsApi,
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

function ExpiryCell({ row }: { row: ProductBatch }) {
  const meta =
    row.expiryStatus && row.daysToExpiry !== undefined
      ? {
          status: row.expiryStatus,
          label:
            row.expiryStatus === "expired"
              ? "Expired"
              : row.expiryStatus === "expiring_soon"
                ? row.daysToExpiry === 0
                  ? "Expires today"
                  : `Expires in ${row.daysToExpiry}d`
                : row.expiryDate
                  ? new Date(row.expiryDate).toLocaleDateString()
                  : "—",
          variant:
            row.expiryStatus === "expired"
              ? ("danger" as const)
              : row.expiryStatus === "expiring_soon"
                ? ("warning" as const)
                : ("default" as const),
        }
      : getExpiryStatus(row.expiryDate, { quantityOnHand: row.quantityOnHand });

  if (meta.status === "no_expiry" && !row.expiryDate) {
    return <span className="text-fg-muted">—</span>;
  }

  return (
    <div className="flex flex-col gap-0.5">
      {row.expiryDate ? (
        <span className="text-sm">{new Date(row.expiryDate).toLocaleDateString()}</span>
      ) : null}
      {meta.status === "expired" || meta.status === "expiring_soon" ? (
        <Badge variant={meta.variant} aria-label={`Batch expiry: ${meta.label}`}>
          {meta.label}
        </Badge>
      ) : null}
    </div>
  );
}

export default function ProductBatchesPage() {
  const qc = useQueryClient();
  const searchParams = useSearchParams();
  const expiryFilter = searchParams.get("filter");
  const [open, setOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const smartSettingsQuery = useTenantReferenceQuery(["smart-settings", "expiry-window"], () =>
    settingsApi.getSmartSettings(),
  );
  const inventoryAlerts = smartSettingsQuery.data?.result?.payload?.inventoryAlerts as
    | { windowDays?: number }
    | undefined;
  const alertWindowDays = Number(inventoryAlerts?.windowDays) || EXPIRY_ALERT_WINDOW_DAYS;

  const { data, isLoading, error: queryError } = useTenantListQuery(
    ["product-batches", expiryFilter ?? "all"],
    () =>
      inventoryWritesApi.listBatches(
        expiryFilter === "expired" || expiryFilter === "expiring"
          ? { filter: expiryFilter }
          : undefined,
      ),
  );

  const sortedRows = useMemo(
    () => sortBatchesByExpiryUrgency(data?.result ?? []),
    [data?.result],
  );

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows: sortedRows,
    syncUrl: true,
    filterFn: (r, q) =>
      matchesExpiryFilter(r, expiryFilter) &&
      matchText([r.productCode, r.batchNumber, r.notes], q),
  });

  const baseColumns = useMemo(
    () =>
      responsiveListColumns<ProductBatch>([
        { key: "productCode", header: "Product" },
        { key: "batchNumber", header: "Batch" },
        {
          key: "expiryDate",
          header: "Expiry",
          render: (r) => <ExpiryCell row={r} />,
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

  const filterLabel =
    expiryFilter === "expired"
      ? "Showing expired batches"
      : expiryFilter === "expiring"
        ? `Showing batches expiring within ${alertWindowDays} days`
        : null;

  return (
    <div>
      <PageHeader
        title="Batches and expiry"
        breadcrumb="Stock / Batches"
        actions={<Button onClick={() => setOpen(true)}>New batch</Button>}
      />
      {filterLabel ? (
        <p className="mb-3 text-sm text-fg-muted" role="status">
          {filterLabel}.{" "}
          <a href="/inventory/batches" className="text-brand hover:underline">
            Clear filter
          </a>
        </p>
      ) : null}
      <ListToolbar search={search} onSearchChange={setSearch} />
      <EnterpriseGrid<ProductBatch>
        columns={columns as GridColumn<ProductBatch>[]}
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
