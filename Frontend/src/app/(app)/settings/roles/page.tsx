/** Roles management — catalog §12.4 */
"use client";
import { useTenantReferenceQuery, invalidateTenantQueries, useTenantListQuery } from "@/lib/api/tenant-query";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { ListToolbar } from "@/components/ui/list-toolbar";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { importJobsApi, rbacApi, type RbacRole } from "@/lib/api/tenant";
import { roleImportJobAuditHref } from "@/lib/rbac/audit-log";
import { resolveRoleCloneIdsFromExport } from "@/lib/rbac/role-export";
import { hasPermission, PERM_ROLES_MANAGE } from "@/lib/rbac/permissions";
import { useClientList } from "@/lib/hooks/use-client-list";
import { matchText } from "@/lib/list/document-list-filters";
import { detailQueryOptions, listQueryOptions, referenceQueryOptions } from "@/lib/query/options";
import { brandLinkClasses } from "@/lib/design-tokens/brand-surfaces";
import { cn } from "@/lib/utils";

const ROLE_JOB_TYPE = "roles";

type ImportJobRow = {
  id?: string;
  jobType?: string;
  status?: string;
  fileName?: string;
  resultSummary?: string;
  createdAt?: string;
};

export default function RolesPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [importFile, setImportFile] = useState<File | null>(null);
  const [trackedJobId, setTrackedJobId] = useState<string | null>(null);
  const [importMessage, setImportMessage] = useState<string | null>(null);
  const [importPreview, setImportPreview] = useState<Record<string, unknown> | null>(
    null
  );
  const [importPreviewHint, setImportPreviewHint] = useState<string | null>(null);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [cloneSuffix, setCloneSuffix] = useState(" (copy)");
  const [exportStripIds, setExportStripIds] = useState(false);
  const headerImportRef = useRef<HTMLInputElement>(null);
  const cloneExportRef = useRef<HTMLInputElement>(null);

  const { data: permsData } = useTenantReferenceQuery(["my-permissions"], () => rbacApi.getMyPermissions());
  const canManageRoles = hasPermission(
    permsData?.result?.permissions ?? [],
    PERM_ROLES_MANAGE
  );

  const { data, isLoading, error } = useTenantReferenceQuery(["rbac-roles"], () => rbacApi.listRoles());

  const roles = data?.result ?? [];

  const { search, setSearch, pageRows, pagination } = useClientList({
    rows: roles,
    syncUrl: true,
    filterFn: (r, q) => matchText([r.name], q),
  });

  const { data: jobsData } = useTenantListQuery<{ result: ImportJobRow[] }>(
    ["import-jobs", "roles"],
    () => importJobsApi.list(),
    {
      enabled: canManageRoles,
      refetchInterval: (query) => {
        const jobs = (query.state.data?.result ?? []) as ImportJobRow[];
        const roleJobs = jobs.filter((j) => j.jobType === ROLE_JOB_TYPE);
        const pending = roleJobs.some(
          (j) => j.status === "pending" || j.status === "processing",
        );
        const tracked = jobs.find((j) => j.id === trackedJobId);
        if (tracked?.status === "pending" || tracked?.status === "processing") {
          return 2000;
        }
        return pending ? 3000 : false;
      },
    },
  );

  const roleImportJobs = useMemo(() => {
    const rows = (jobsData?.result ?? []) as ImportJobRow[];
    return rows
      .filter((j) => j.jobType === ROLE_JOB_TYPE)
      .slice(0, 5);
  }, [jobsData]);

  const { data: trackedJob } = useTenantListQuery<{ result: ImportJobRow & { status?: string } }>(
    ["role-import-job", trackedJobId],
    () => rbacApi.getRoleImportJob(trackedJobId!),
    {
      enabled: Boolean(trackedJobId && canManageRoles),
      refetchInterval: (query) => {
        const status = query.state.data?.result?.status;
        if (status === "pending" || status === "processing") return 2000;
        return false;
      },
    },
  );

  useEffect(() => {
    const status = trackedJob?.result?.status;
    if (!trackedJobId || !status) return;
    if (status === "completed" || status === "failed") {
      void invalidateTenantQueries(queryClient, "rbac-roles");
      void invalidateTenantQueries(queryClient, "import-jobs", "roles");
    }
  }, [trackedJobId, trackedJob?.result?.status, queryClient]);

  const exportRoles = useMutation({
    mutationFn: () => rbacApi.exportRoles({ stripIds: exportStripIds }),
    onSuccess: (res) => {
      const blob = new Blob([JSON.stringify(res.result, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const suffix = res.result.namesOnly ? "-names-only" : "";
      a.download = `roles-export${suffix}-${new Date().toISOString().slice(0, 10)}.json`;
      a.click();
      URL.revokeObjectURL(url);
      setImportMessage(
        res.result.namesOnly ? "Roles exported (names only, no ids)." : "Roles exported."
      );
    },
    onError: (e: Error) => setImportMessage(e.message),
  });

  const cloneBatch = useMutation({
    mutationFn: () =>
      rbacApi.cloneRolesBatch({
        roleIds: Array.from(selected),
        nameSuffix: cloneSuffix.trim() || undefined,
      }),
    onSuccess: (res) => {
      setSelected(new Set());
      setImportMessage(`Cloned ${res.result?.length ?? 0} role(s).`);
      void invalidateTenantQueries(queryClient, "rbac-roles");
    },
    onError: (e: Error) => setImportMessage(e.message),
  });

  const cloneFromExport = useMutation({
    mutationFn: async (file: File) => {
      const roleIds = resolveRoleCloneIdsFromExport(
        await file.text(),
        roles.map((r) => ({ id: r.id, name: r.name })),
        selected
      );
      return rbacApi.cloneRolesBatch({
        roleIds,
        nameSuffix: cloneSuffix.trim() || undefined,
      });
    },
    onSuccess: (res) => {
      setSelected(new Set());
      setImportMessage(`Cloned ${res.result?.length ?? 0} role(s) from export.`);
      void invalidateTenantQueries(queryClient, "rbac-roles");
    },
    onError: (e: Error) => setImportMessage(e.message),
  });

  const previewImport = useMutation({
    mutationFn: async () => {
      if (!importFile) throw new Error("Choose a file");
      return rbacApi.uploadRoleImport(importFile, { skipExisting: true, dryRun: true });
    },
    onSuccess: (res) => {
      const result = (res.data?.result ?? null) as Record<string, unknown> | null;
      setImportPreview(result);
      if (result?.namesOnly === true) {
        setImportPreviewHint(
          "Names-only file — roles will be matched or created by name (no ids in file)."
        );
      } else {
        setImportPreviewHint(null);
      }
      setImportMessage("Import preview ready (dry run).");
    },
    onError: (e: Error) => setImportMessage(e.message),
  });

  const runRoleImport = async (file: File) => {
    setImportFile(file);
    return rbacApi.uploadRoleImport(file, { skipExisting: true });
  };

  const headerImport = useMutation({
    mutationFn: (file: File) => runRoleImport(file),
    onSuccess: (res) => {
      const result = res.data?.result as Record<string, unknown> | undefined;
      const mode = result?.mode as string | undefined;
      if (mode === "async" && result?.job && typeof result.job === "object") {
        const job = result.job as { id?: string };
        if (job.id) setTrackedJobId(job.id);
        setImportMessage(
          `Queued async import (${String(result.rowCount ?? "")} roles). Job ${job.id ?? ""}.`
        );
      } else if (mode === "sync") {
        const created = Array.isArray(result?.created) ? result.created.length : 0;
        const skipped = Array.isArray(result?.skipped) ? result.skipped.length : 0;
        setImportMessage(`Import complete: ${created} created, ${skipped} skipped.`);
        void invalidateTenantQueries(queryClient, "rbac-roles");
      } else {
        setImportMessage("Import finished.");
        void invalidateTenantQueries(queryClient, "rbac-roles");
      }
      void invalidateTenantQueries(queryClient, "import-jobs", "roles");
    },
    onError: (e: Error) => setImportMessage(e.message),
  });

  const uploadImport = useMutation({
    mutationFn: async () => {
      if (!importFile) throw new Error("Choose a file");
      return runRoleImport(importFile);
    },
    onSuccess: (res) => {
      setImportFile(null);
      const result = res.data?.result as Record<string, unknown> | undefined;
      const mode = result?.mode as string | undefined;
      if (mode === "async" && result?.job && typeof result.job === "object") {
        const job = result.job as { id?: string };
        if (job.id) setTrackedJobId(job.id);
        setImportMessage(
          `Queued async import (${String(result.rowCount ?? "")} roles). Job ${job.id ?? ""}.`
        );
      } else if (mode === "sync") {
        const created = Array.isArray(result?.created) ? result.created.length : 0;
        const skipped = Array.isArray(result?.skipped) ? result.skipped.length : 0;
        setImportMessage(`Import complete: ${created} created, ${skipped} skipped.`);
        void invalidateTenantQueries(queryClient, "rbac-roles");
      } else {
        setImportMessage("Import finished.");
        void invalidateTenantQueries(queryClient, "rbac-roles");
      }
      void invalidateTenantQueries(queryClient, "import-jobs", "roles");
    },
    onError: (e: Error) => setImportMessage(e.message),
  });

  const roleColumns: GridColumn<RbacRole>[] = useMemo(() => {
    const cols: GridColumn<RbacRole>[] = [];
    if (canManageRoles) {
      cols.push({
        key: "select",
        header: "",
        render: (r) => (
          <input
            type="checkbox"
            checked={selected.has(r.id)}
            onChange={(e) => {
              const next = new Set(selected);
              if (e.target.checked) next.add(r.id);
              else next.delete(r.id);
              setSelected(next);
            }}
          />
        ),
      });
    }
    cols.push(
      { key: "name", header: "Role", sortable: true, sortAccessor: (r) => r.name },
      {
        key: "permissions",
        header: "Permissions",
        render: (r) => {
          const p = r.permissions;
          if (Array.isArray(p) && p.includes("*")) return "Full access";
          if (Array.isArray(p)) return `${p.length} codes`;
          return "—";
        },
      }
    );
    if (canManageRoles) {
      cols.push({
        key: "actions",
        header: "",
        render: (r) => (
          <Link
            href={`/settings/roles/${r.id}`}
            className={cn("text-sm font-medium hover:underline", brandLinkClasses)}
          >
            Edit
          </Link>
        ),
      });
    }
    return responsiveListColumns(cols, { primaryKey: "name" });
  }, [canManageRoles, selected]);

  const jobColumns = responsiveListColumns<ImportJobRow>([
    { key: "status", header: "Status" },
    { key: "fileName", header: "File" },
    { key: "resultSummary", header: "Summary" },
    {
      key: "createdAt",
      header: "Created",
      render: (r) =>
        r.createdAt ? new Date(String(r.createdAt)).toLocaleString() : "—",
    },
    {
      key: "audit",
      header: "Audit",
      render: (r) =>
        r.id && (r.status === "completed" || r.status === "failed") ? (
          <Link
            href={roleImportJobAuditHref(String(r.id))}
            className={cn("text-sm font-medium hover:underline", brandLinkClasses)}
          >
            View log
          </Link>
        ) : (
          "—"
        ),
    },
  ]);

  const activeJob = trackedJob?.result;

  return (
    <div>
      <PageHeader
        title="Roles"
        breadcrumb="Home / Roles"
        description="RBAC roles (§12.4). Import JSON/CSV; large files queue in the background."
        actions={
          canManageRoles ? (
            <div className="flex flex-wrap gap-2">
              <input
                ref={headerImportRef}
                type="file"
                accept=".json,.csv"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) headerImport.mutate(file);
                  e.target.value = "";
                }}
              />
              <label className="flex items-center gap-2 text-sm text-fg">
                <input
                  type="checkbox"
                  checked={exportStripIds}
                  onChange={(e) => setExportStripIds(e.target.checked)}
                />
                Names only
              </label>
              <Button
                type="button"
                variant="outline"
                disabled={exportRoles.isPending}
                onClick={() => exportRoles.mutate()}
              >
                {exportRoles.isPending
                  ? "Exporting…"
                  : exportStripIds
                    ? "Export JSON (no ids)"
                    : "Export JSON"}
              </Button>
              <Button
                type="button"
                variant="outline"
                disabled={headerImport.isPending}
                onClick={() => headerImportRef.current?.click()}
              >
                {headerImport.isPending ? "Importing…" : "Import JSON"}
              </Button>
              <Link href="/settings/roles/new">
                <Button>+ Add role</Button>
              </Link>
            </div>
          ) : (
            <Button disabled>+ Add role</Button>
          )
        }
      />

      {canManageRoles && (
        <div className="mb-4 flex flex-wrap items-end gap-3 rounded-lg border border-brand/30 bg-brand/5 p-4">
          {selected.size > 0 && (
            <span className="text-sm font-medium text-fg">{selected.size} selected</span>
          )}
          <FormField label="Name suffix">
            <Input
              className="w-40"
              value={cloneSuffix}
              onChange={(e) => setCloneSuffix(e.target.value)}
              placeholder=" (copy)"
            />
          </FormField>
          <input
            ref={cloneExportRef}
            type="file"
            accept=".json,application/json"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) cloneFromExport.mutate(file);
              e.target.value = "";
            }}
          />
          {selected.size > 0 && (
            <Button
              type="button"
              disabled={cloneBatch.isPending || cloneFromExport.isPending}
              onClick={() => cloneBatch.mutate()}
            >
              {cloneBatch.isPending ? "Cloning…" : "Clone selected"}
            </Button>
          )}
          <Button
            type="button"
            variant="outline"
            disabled={cloneFromExport.isPending}
            onClick={() => cloneExportRef.current?.click()}
          >
            {cloneFromExport.isPending ? "Cloning…" : "Clone from export JSON"}
          </Button>
          {selected.size > 0 && (
            <Button type="button" variant="outline" onClick={() => setSelected(new Set())}>
              Clear selection
            </Button>
          )}
        </div>
      )}

      {canManageRoles && (
        <section className="mb-6 space-y-4 rounded-lg border border-border bg-surface p-4">
          <h2 className="text-sm font-semibold text-fg">Import roles</h2>
          <p className="text-sm text-fg-muted">
            Upload JSON or CSV (including names-only exports without role ids). Files
            with 50+ roles are processed asynchronously.
          </p>
          <div className="flex flex-wrap items-end gap-3">
            <input
              type="file"
              accept=".json,.csv"
              className="block text-sm"
              onChange={(e) => setImportFile(e.target.files?.[0] ?? null)}
            />
            <Button
              type="button"
              variant="outline"
              disabled={!importFile || previewImport.isPending}
              onClick={() => previewImport.mutate()}
            >
              {previewImport.isPending ? "Previewing…" : "Preview import"}
            </Button>
            <Button
              type="button"
              disabled={!importFile || uploadImport.isPending}
              onClick={() => uploadImport.mutate()}
            >
              {uploadImport.isPending ? "Uploading…" : "Upload"}
            </Button>
          </div>
          {importPreviewHint && (
            <p className="rounded-md border border-status-warning/30 bg-status-warning/10 px-3 py-2 text-sm text-status-warning">
              {importPreviewHint}
            </p>
          )}
          {importPreview && (
            <pre className="max-h-48 overflow-auto rounded-md border border-border bg-canvas p-3 text-xs text-fg">
              {JSON.stringify(importPreview, null, 2)}
            </pre>
          )}
          {importMessage && (
            <p
              className={`text-sm ${
                exportRoles.isError || cloneBatch.isError || uploadImport.isError
                  ? "text-status-danger"
                  : "text-fg"
              }`}
            >
              {importMessage}
            </p>
          )}
          {activeJob && (
            <div className="rounded-md border border-border bg-canvas px-3 py-2 text-sm text-fg">
              <span className="font-medium">Tracked job:</span> {activeJob.status}
              {activeJob.fileName ? ` — ${activeJob.fileName}` : ""}
              {activeJob.resultSummary ? ` — ${activeJob.resultSummary}` : ""}
            </div>
          )}
          {roleImportJobs.length > 0 && (
            <div>
              <h3 className="mb-2 text-xs font-medium uppercase tracking-wide text-fg-muted">
                Recent role imports
              </h3>
              <EnterpriseGrid<ImportJobRow>
                columns={jobColumns}
                rows={roleImportJobs}
                emptyMessage="No role import jobs."
              />
            </div>
          )}
        </section>
      )}

      <ListToolbar search={search} onSearchChange={setSearch} />
      <EnterpriseGrid<RbacRole>
        columns={roleColumns}
        rows={pageRows}
        loading={isLoading}
        error={error}
        emptyMessage="No roles defined yet."
        pagination={pagination}
        onRowClick={
          canManageRoles ? (r) => r.id && router.push(`/settings/roles/${r.id}`) : undefined
        }
      />
    </div>
  );
}
