/**
 * Chart of Account tree — catalog §9.1.1.
 * + Nominal account button opens the Nominal Account New modal (§9.1.2).
 */
"use client";
import { useTenantReferenceQuery, invalidateTenantQueries } from "@/lib/api/tenant-query";

import { useMemo, useState } from "react";
import Link from "next/link";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { ChevronDown, ChevronRight, Plus } from "lucide-react";

import { CoaNominalGrid } from "@/components/settings/coa-nominal-grid";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import { PageHeader } from "@/components/ui/page-header";
import { WorkspaceLoading } from "@/components/ui/workspace-loading";
import { Select } from "@/components/ui/select";
import { cn } from "@/lib/utils";
import { brandSoftClasses } from "@/lib/design-tokens/brand-surfaces";
import {
  ledgerApi,
  type CategoryType,
  type CoaTreeCategory,
  type CoaTreeSection,
  type CreateNominalInput,
} from "@/lib/api/tenant";
import { ApiError } from "@/lib/api/client";
import { referenceQueryOptions } from "@/lib/query/options";
import { useAutoCodePreview } from "@/lib/hooks/use-auto-code-preview";

const schema = z.object({
  sectionId: z.string().min(1, "Required"),
  code: z.string().optional(),
  name: z.string().min(1, "Required"),
  description: z.string().optional(),
  isChargeDeduction: z.boolean().default(false),
});
type FormValues = z.infer<typeof schema>;

const editSchema = z.object({
  name: z.string().min(1, "Required"),
  description: z.string().optional(),
  isChargeDeduction: z.boolean().default(false),
  sectionId: z.string().min(1, "Required"),
});
type EditFormValues = z.infer<typeof editSchema>;

export default function ChartOfAccountPage() {
  const qc = useQueryClient();
  const [showAdd, setShowAdd] = useState(false);
  const [editNominal, setEditNominal] = useState<{
    id: string;
    code: string;
    name: string;
    description?: string | null;
    isChargeDeduction: boolean;
    sectionId: string;
  } | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const [view, setView] = useState<"tree" | "grid">("tree");
  const [selectedNominalIds, setSelectedNominalIds] = useState<Set<string>>(() => new Set());

  const treeQuery = useTenantReferenceQuery(["coa-tree"], () => ledgerApi.getCoaTree());

  const flatSections = useMemo(() => {
    const out: { id: string; label: string }[] = [];
    for (const cat of treeQuery.data?.result ?? []) {
      for (const sec of cat.sections) {
        out.push({ id: sec.id, label: `${cat.name} › ${sec.name} (${sec.code})` });
      }
    }
    return out;
  }, [treeQuery.data]);

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      sectionId: "",
      code: "",
      name: "",
      description: "",
      isChargeDeduction: false,
    },
  });

  const { enabled: autoCode, nextCode } = useAutoCodePreview("nominal", {
    enabled: showAdd,
    onPreview: (code) => {
      if (code && !form.getValues("code")) form.setValue("code", code);
    },
  });

  const editForm = useForm<EditFormValues>({
    resolver: zodResolver(editSchema),
    defaultValues: {
      name: "",
      description: "",
      isChargeDeduction: false,
      sectionId: "",
    },
  });

  const createMutation = useMutation({
    mutationFn: (input: CreateNominalInput) => ledgerApi.createNominal(input),
    onSuccess: () => {
      setShowAdd(false);
      setSubmitError(null);
      form.reset();
      invalidateTenantQueries(qc, "coa-tree");
    },
    onError: (err) =>
      setSubmitError(err instanceof ApiError ? err.message : "Could not create nominal"),
  });

  const typeMutation = useMutation({
    mutationFn: ({ id, type }: { id: string; type: CategoryType }) =>
      ledgerApi.updateCategoryType(id, type),
    onSuccess: () => {
      invalidateTenantQueries(qc, "coa-tree");
    },
  });

  const updateNominalMutation = useMutation({
    mutationFn: async (values: EditFormValues) => {
      if (!editNominal) throw new Error("No nominal selected");
      await ledgerApi.updateNominal(editNominal.id, {
        name: values.name,
        description: values.description || null,
        isChargeDeduction: values.isChargeDeduction,
      });
      if (values.sectionId !== editNominal.sectionId) {
        await ledgerApi.moveNominal(editNominal.id, { sectionId: values.sectionId });
      }
    },
    onSuccess: () => {
      setEditNominal(null);
      setSubmitError(null);
      invalidateTenantQueries(qc, "coa-tree");
    },
    onError: (err) =>
      setSubmitError(err instanceof ApiError ? err.message : "Could not update nominal"),
  });

  const deleteNominalMutation = useMutation({
    mutationFn: (id: string) => ledgerApi.deleteNominal(id),
    onSuccess: () => {
      setEditNominal(null);
      setSubmitError(null);
      invalidateTenantQueries(qc, "coa-tree");
    },
    onError: (err) =>
      setSubmitError(err instanceof ApiError ? err.message : "Could not delete nominal"),
  });

  const bulkDeleteMutation = useMutation({
    mutationFn: (ids: string[]) => ledgerApi.bulkDeleteNominals(ids),
    onSuccess: (res) => {
      setSelectedNominalIds(new Set());
      setSubmitError(null);
      invalidateTenantQueries(qc, "coa-tree");
      const skipped = res.result?.skipped ?? 0;
      if (skipped > 0) {
        setSubmitError(
          `Deleted ${res.result?.deleted ?? 0}; skipped ${skipped} (journal lines or not found).`,
        );
      }
    },
    onError: (err) =>
      setSubmitError(err instanceof ApiError ? err.message : "Could not bulk delete nominals"),
  });

  function toggleNominalSelect(id: string, checked: boolean) {
    setSelectedNominalIds((prev) => {
      const next = new Set(prev);
      if (checked) next.add(id);
      else next.delete(id);
      return next;
    });
  }

  function toggleEditDelete() {
    if (!editNominal) return;
    if (
      !window.confirm(
        `Delete nominal ${editNominal.code}? Only unused nominals (no journal lines) can be removed.`,
      )
    ) {
      return;
    }
    deleteNominalMutation.mutate(editNominal.id);
  }

  function toggleBulkDelete() {
    const ids = [...selectedNominalIds];
    if (!ids.length) return;
    if (
      !window.confirm(
        `Delete ${ids.length} selected nominal(s)? Nominals with journal lines will be skipped.`,
      )
    ) {
      return;
    }
    bulkDeleteMutation.mutate(ids);
  }

  function toggle(id: string) {
    setExpanded((s) => ({ ...s, [id]: !s[id] }));
  }

  return (
    <div>
      <PageHeader
        title="Chart of Account"
        breadcrumb="Accounting / Chart of accounts"
        description="Hierarchy Category → Section → Nominal (§9.1.1)."
        actions={
          <>
            <div className="flex rounded-md border border-border p-0.5">
              <button
                type="button"
                onClick={() => setView("tree")}
                className={cn(
                  "rounded px-3 py-1.5 text-xs font-medium",
                  view === "tree" ? brandSoftClasses : "text-fg-muted hover:bg-canvas",
                )}
              >
                Tree
              </button>
              <button
                type="button"
                onClick={() => setView("grid")}
                className={cn(
                  "rounded px-3 py-1.5 text-xs font-medium",
                  view === "grid" ? brandSoftClasses : "text-fg-muted hover:bg-canvas",
                )}
              >
                All nominals
              </button>
            </div>
            <Link href="/settings/sections">
              <Button variant="outline">Sections</Button>
            </Link>
            <Button onClick={() => setShowAdd(true)}>
              <Plus className="mr-1 h-4 w-4" /> Nominal account
            </Button>
          </>
        }
      />

      {view === "grid" ? (
        <>
          {selectedNominalIds.size > 0 ? (
            <div className="mb-3 flex items-center gap-2">
              <Button
                type="button"
                variant="outline"
                size="sm"
                disabled={bulkDeleteMutation.isPending}
                onClick={toggleBulkDelete}
              >
                Delete selected ({selectedNominalIds.size})
              </Button>
            </div>
          ) : null}
          {submitError && view === "grid" ? (
            <div className="mb-3 rounded-md border border-status-danger/30 bg-status-danger/10 px-3 py-2 text-sm text-status-danger">
              {submitError}
            </div>
          ) : null}
          <CoaNominalGrid
            categories={treeQuery.data?.result ?? []}
            loading={treeQuery.isLoading}
            error={treeQuery.error}
            selectedIds={selectedNominalIds}
            onToggleSelect={toggleNominalSelect}
            onEdit={(row) => {
            setSubmitError(null);
            setEditNominal({
              id: row.id,
              code: row.code,
              name: row.name,
              description: row.description,
              isChargeDeduction: row.isChargeDeduction,
              sectionId: row.sectionId,
            });
            editForm.reset({
              name: row.name,
              description: row.description ?? "",
              isChargeDeduction: row.isChargeDeduction,
              sectionId: row.sectionId,
            });
          }}
        />
        </>
      ) : treeQuery.isLoading ? (
        <WorkspaceLoading />
      ) : treeQuery.error instanceof Error ? (
        <div className="rounded-md border border-status-danger/30 bg-status-danger/10 p-3 text-sm text-status-danger">
          {treeQuery.error.message}
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-border bg-surface">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-canvas text-left text-xs uppercase tracking-wide text-fg-muted">
                <th className="px-3 py-2">Code</th>
                <th className="px-3 py-2">Nominal account</th>
              </tr>
            </thead>
            <tbody>
              {(treeQuery.data?.result ?? []).map((cat) => (
                <CategoryRows
                  key={cat.id}
                  category={cat}
                  expanded={expanded}
                  onToggle={toggle}
                  onTypeChange={(type) => typeMutation.mutate({ id: cat.id, type })}
                />
              ))}
              {(treeQuery.data?.result ?? []).length === 0 && (
                <tr>
                  <td colSpan={2} className="px-3 py-6 text-center text-fg-muted">
                    Empty chart. Seed categories or add sections in Section Management.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      <Modal
        open={showAdd}
        title="Nominal Account New"
        size="lg"
        onClose={() => {
          setShowAdd(false);
          setSubmitError(null);
        }}
        footer={
          <>
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setShowAdd(false);
                setSubmitError(null);
              }}
            >
              Cancel
            </Button>
            <Button type="submit" form="nominal-new-form" disabled={createMutation.isPending}>
              {createMutation.isPending ? "Saving…" : "Save and close"}
            </Button>
          </>
        }
      >
        <form
          id="nominal-new-form"
          onSubmit={form.handleSubmit((v) =>
            createMutation.mutate({
              sectionId: v.sectionId,
              code: v.code?.trim() || null,
              name: v.name,
              description: v.description || null,
              isChargeDeduction: v.isChargeDeduction,
            }),
          )}
          className="grid grid-cols-1 gap-3 md:grid-cols-2"
        >
          <FormField
            label="Section"
            required
            error={form.formState.errors.sectionId?.message}
          >
            <Select {...form.register("sectionId")}>
              <option value="">Select section…</option>
              {flatSections.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.label}
                </option>
              ))}
            </Select>
          </FormField>
          <FormField
            label={autoCode ? "Code (auto)" : "Code"}
            required={!autoCode}
            error={form.formState.errors.code?.message}
          >
            <Input placeholder={nextCode ?? undefined} {...form.register("code")} />
          </FormField>
          <FormField label="Name" required error={form.formState.errors.name?.message}>
            <Input {...form.register("name")} />
          </FormField>
          <FormField label="Description">
            <Input {...form.register("description")} />
          </FormField>
          <label className="col-span-full flex items-center gap-2 text-sm text-fg">
            <Checkbox {...form.register("isChargeDeduction")} />
            Deduction and charge
          </label>
          {submitError && (
            <div className="col-span-full rounded-md border border-status-danger/30 bg-status-danger/10 px-3 py-2 text-sm text-status-danger">
              {submitError}
            </div>
          )}
        </form>
      </Modal>

      <Modal
        open={editNominal !== null}
        title={`Edit nominal ${editNominal?.code ?? ""}`}
        size="lg"
        onClose={() => {
          setEditNominal(null);
          setSubmitError(null);
        }}
        footer={
          <>
            <Button
              type="button"
              variant="outline"
              className="mr-auto text-status-danger"
              disabled={deleteNominalMutation.isPending}
              onClick={toggleEditDelete}
            >
              Delete
            </Button>
            <Button type="button" variant="outline" onClick={() => setEditNominal(null)}>
              Cancel
            </Button>
            <Button
              type="submit"
              form="nominal-edit-form"
              disabled={updateNominalMutation.isPending}
            >
              {updateNominalMutation.isPending ? "Saving…" : "Save changes"}
            </Button>
          </>
        }
      >
        <form
          id="nominal-edit-form"
          onSubmit={editForm.handleSubmit((v) => updateNominalMutation.mutate(v))}
          className="grid grid-cols-1 gap-3 md:grid-cols-2"
        >
          <FormField label="Section" required error={editForm.formState.errors.sectionId?.message}>
            <Select {...editForm.register("sectionId")}>
              {flatSections.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.label}
                </option>
              ))}
            </Select>
          </FormField>
          <FormField label="Name" required error={editForm.formState.errors.name?.message}>
            <Input {...editForm.register("name")} />
          </FormField>
          <FormField label="Description">
            <Input {...editForm.register("description")} />
          </FormField>
          <label className="col-span-full flex items-center gap-2 text-sm text-fg">
            <Checkbox {...editForm.register("isChargeDeduction")} />
            Deduction and charge
          </label>
          {submitError ? (
            <div className="col-span-full rounded-md border border-status-danger/30 bg-status-danger/10 px-3 py-2 text-sm text-status-danger">
              {submitError}
            </div>
          ) : null}
        </form>
      </Modal>
    </div>
  );
}

const CATEGORY_TYPES: CategoryType[] = [
  "Other",
  "Income",
  "Expense",
  "Asset",
  "Liability",
  "Equity",
];

function CategoryRows({
  category,
  expanded,
  onToggle,
  onTypeChange,
}: {
  category: CoaTreeCategory;
  expanded: Record<string, boolean>;
  onToggle: (id: string) => void;
  onTypeChange: (type: CategoryType) => void;
}) {
  const open = expanded[category.id] ?? true;
  const sectionCount = category.sections.length;
  return (
    <>
      <tr className="border-b border-border bg-brand-50/60 dark:bg-brand-100/10">
        <td colSpan={2} className="px-3 py-2 text-sm font-semibold text-brand-700 dark:text-brand-300">
          <div className="flex items-center justify-between gap-3">
            <button
              type="button"
              onClick={() => onToggle(category.id)}
              className="flex items-center gap-1"
            >
              {open ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
              {category.name} <span className="text-fg-muted">({sectionCount})</span>
            </button>
            <label className="flex items-center gap-2 text-xs font-normal text-fg-muted">
              <span>Type</span>
              <select
                className="h-7 rounded-md border border-border bg-surface px-2 text-xs text-fg"
                value={category.categoryType ?? "Other"}
                onChange={(e) => onTypeChange(e.target.value as CategoryType)}
              >
                {CATEGORY_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </td>
      </tr>
      {open &&
        category.sections.map((sec) => (
          <SectionRows
            key={sec.id}
            section={sec}
            expanded={expanded}
            onToggle={onToggle}
          />
        ))}
    </>
  );
}

function SectionRows({
  section,
  expanded,
  onToggle,
}: {
  section: CoaTreeSection;
  expanded: Record<string, boolean>;
  onToggle: (id: string) => void;
}) {
  const open = expanded[section.id] ?? true;
  return (
    <>
      <tr className="border-b border-border bg-canvas">
        <td colSpan={2} className="px-3 py-1.5 text-sm font-medium text-fg">
          <button
            type="button"
            onClick={() => onToggle(section.id)}
            className="flex items-center gap-1 pl-4"
          >
            {open ? (
              <ChevronDown className="h-3.5 w-3.5" />
            ) : (
              <ChevronRight className="h-3.5 w-3.5" />
            )}
            {section.name}{" "}
            <span className="text-fg-muted">({section.nominals.length})</span>
          </button>
        </td>
      </tr>
      {open &&
        section.nominals.map((n) => (
          <tr key={n.id} className="border-b border-border hover:bg-canvas">
            <td className="px-3 py-1 pl-10 text-fg">{n.code}</td>
            <td className="px-3 py-1 text-fg">{n.name}</td>
          </tr>
        ))}
      {open && section.nominals.length === 0 && (
        <tr>
          <td colSpan={2} className="px-3 py-1 pl-10 text-xs text-fg-muted">
            No nominals yet.
          </td>
        </tr>
      )}
    </>
  );
}
