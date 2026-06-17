/** Section Management — catalog §9.1.4. */
"use client";
import { useTenantReferenceQuery, invalidateTenantQueries } from "@/lib/api/tenant-query";

import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowDown, ArrowUp, Plus } from "lucide-react";

import { Button } from "@/components/ui/button";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { buildGridExport } from "@/lib/export/grid-export";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { ListToolbar } from "@/components/ui/list-toolbar";
import { Modal } from "@/components/ui/modal";
import { PageHeader } from "@/components/ui/page-header";
import { Select } from "@/components/ui/select";
import {
  ledgerApi,
  type CoaSection,
  type CreateSectionInput,
} from "@/lib/api/tenant";
import { ApiError } from "@/lib/api/client";
import { useClientList } from "@/lib/hooks/use-client-list";
import { matchText } from "@/lib/list/document-list-filters";
import { referenceQueryOptions } from "@/lib/query/options";

const schema = z.object({
  categoryId: z.string().min(1, "Required"),
  code: z.string().min(1, "Required"),
  name: z.string().min(1, "Required"),
});
type FormValues = z.infer<typeof schema>;

type SectionRow = CoaSection & {
  categoryLabel: string;
  indexInCategory: number;
  sectionCountInCategory: number;
};

export default function SectionManagementPage() {
  const qc = useQueryClient();
  const [showAdd, setShowAdd] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  const categoriesQuery = useTenantReferenceQuery(["coa-categories"], () => ledgerApi.listCoaCategories());
  const sectionsQuery = useTenantReferenceQuery(["coa-sections"], () => ledgerApi.listSections());

  const flatSections = useMemo((): SectionRow[] => {
    const cats = categoriesQuery.data?.result ?? [];
    const secs = sectionsQuery.data?.result ?? [];
    const out: SectionRow[] = [];
    for (const cat of cats) {
      const inCat = secs
        .filter((s) => s.categoryId === cat.id)
        .sort((a, b) => a.sortOrder - b.sortOrder);
      inCat.forEach((s, idx) => {
        out.push({
          ...s,
          categoryLabel: `${cat.name} (${cat.code})`,
          indexInCategory: idx,
          sectionCountInCategory: inCat.length,
        });
      });
    }
    return out;
  }, [categoriesQuery.data, sectionsQuery.data]);

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows: flatSections,
    syncUrl: true,
    filterFn: (r, q) => matchText([r.categoryLabel, r.code, r.name], q),
  });

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { categoryId: "", code: "", name: "" },
  });

  const createMutation = useMutation({
    mutationFn: (input: CreateSectionInput) => ledgerApi.createSection(input),
    onSuccess: () => {
      setShowAdd(false);
      setCreateError(null);
      form.reset({ categoryId: "", code: "", name: "" });
      void invalidateTenantQueries(qc, "coa-sections");
      void invalidateTenantQueries(qc, "coa-tree");
    },
    onError: (err) =>
      setCreateError(err instanceof ApiError ? err.message : "Could not create section"),
  });

  const reorderMutation = useMutation({
    mutationFn: ({ id, direction }: { id: string; direction: "up" | "down" }) =>
      ledgerApi.reorderSection(id, direction),
    onSuccess: () => {
      void invalidateTenantQueries(qc, "coa-sections");
      void invalidateTenantQueries(qc, "coa-tree");
    },
  });

  const columns = useMemo(
    () => responsiveListColumns<SectionRow>([
      {
        key: "categoryLabel",
        header: "Category",
        sortable: true,
        sortAccessor: (r) => r.categoryLabel,
      },
      { key: "code", header: "Code", sortable: true, sortAccessor: (r) => r.code },
      { key: "name", header: "Section", sortable: true, sortAccessor: (r) => r.name },
      {
        key: "reorder",
        header: "",
        render: (r) => (
          <div className="flex justify-end gap-1">
            <button
              type="button"
              aria-label="Move up"
              disabled={r.indexInCategory === 0 || reorderMutation.isPending}
              onClick={() => reorderMutation.mutate({ id: r.id, direction: "up" })}
              className="rounded p-1 text-status-success hover:bg-status-success/10 focus-ring disabled:cursor-not-allowed disabled:opacity-30"
            >
              <ArrowUp className="h-4 w-4" />
            </button>
            <button
              type="button"
              aria-label="Move down"
              disabled={
                r.indexInCategory >= r.sectionCountInCategory - 1 || reorderMutation.isPending
              }
              onClick={() => reorderMutation.mutate({ id: r.id, direction: "down" })}
              className="rounded p-1 text-status-danger hover:bg-status-danger/10 disabled:cursor-not-allowed disabled:opacity-30"
            >
              <ArrowDown className="h-4 w-4" />
            </button>
          </div>
        ),
      },
    ]),
    [reorderMutation.isPending],
  );

  const isLoading = sectionsQuery.isLoading || categoriesQuery.isLoading;

  return (
    <div>
      <PageHeader
        title="Section listing"
        breadcrumb="Accounting / Sections"
        description="Sections sit between categories and nominals (§9.1.4). Use Up/Down to reorder within a category."
        actions={
          <Button onClick={() => setShowAdd(true)}>
            <Plus className="mr-1 h-4 w-4" /> Add new
          </Button>
        }
      />

      <ListToolbar search={search} onSearchChange={setSearch} searchPlaceholder="Search sections…" />
      <EnterpriseGrid<SectionRow>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        error={sectionsQuery.error ?? categoriesQuery.error}
        emptyMessage="No sections yet. Add a category first, then create sections."
        pagination={pagination}
        exportCsv={{ ...buildGridExport("coa-sections", columns), rows: filtered }}
        getRowId={(r) => r.id}
      />

      <Modal
        open={showAdd}
        title="Section new"
        onClose={() => {
          setShowAdd(false);
          setCreateError(null);
        }}
        footer={
          <>
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setShowAdd(false);
                setCreateError(null);
              }}
            >
              Cancel
            </Button>
            <Button type="submit" form="section-new-form" disabled={createMutation.isPending}>
              {createMutation.isPending ? "Saving…" : "Save and close"}
            </Button>
          </>
        }
      >
        <form
          id="section-new-form"
          onSubmit={form.handleSubmit((v) => createMutation.mutate(v))}
          className="space-y-3"
        >
          <FormField label="Category" required error={form.formState.errors.categoryId?.message}>
            <Select {...form.register("categoryId")}>
              <option value="">Select category…</option>
              {categoriesQuery.data?.result.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name} ({c.code})
                </option>
              ))}
            </Select>
          </FormField>
          <FormField label="Code" required error={form.formState.errors.code?.message}>
            <Input {...form.register("code")} />
          </FormField>
          <FormField label="Name" required error={form.formState.errors.name?.message}>
            <Input {...form.register("name")} />
          </FormField>
          {createError && (
            <div className="rounded-md border border-status-danger/30 bg-status-danger/10 px-3 py-2 text-sm text-status-danger">
              {createError}
            </div>
          )}
        </form>
      </Modal>
    </div>
  );
}
