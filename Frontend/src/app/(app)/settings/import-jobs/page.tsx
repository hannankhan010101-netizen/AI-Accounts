/** Bulk import jobs — JSON rows or Excel upload (P3). */
"use client";
import { invalidateTenantQueries, useTenantListQuery } from "@/lib/api/tenant-query";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { ListToolbar } from "@/components/ui/list-toolbar";
import { useClientList } from "@/lib/hooks/use-client-list";
import { matchText } from "@/lib/list/document-list-filters";
import { PageHeader } from "@/components/ui/page-header";
import { Select } from "@/components/ui/select";
import { getCurrentCompanyId } from "@/lib/auth/storage";
import { importJobsApi } from "@/lib/api/tenant";

const JOB_TYPES = [
  "customers",
  "suppliers",
  "products",
  "opening_stock",
  "product_tax_update",
  "journals",
  "bank_payments",
  "bank_receipts",
  "supplier_bills",
  "sales_invoices",
  "sales_receipts",
  "supplier_payments",
  "roles",
] as const;

type JobRow = Record<string, unknown> & { id?: string; jobType?: string; status?: string };

export default function ImportJobsPage() {
  const qc = useQueryClient();
  const [jobType, setJobType] = useState<(typeof JOB_TYPES)[number]>("customers");
  const [file, setFile] = useState<File | null>(null);
  const [postGl, setPostGl] = useState(false);

  const DOC_JOB_TYPES = new Set([
    "sales_invoices",
    "sales_receipts",
    "supplier_bills",
    "supplier_payments",
  ]);
  const showPostGl = DOC_JOB_TYPES.has(jobType);

  const { data, isLoading, isFetching, error } = useTenantListQuery(["import-jobs"], () => importJobsApi.list());

  const upload = useMutation({
    mutationFn: async () => {
      if (!file) throw new Error("Choose a file");
      const companyId = getCurrentCompanyId();
      if (!companyId) throw new Error("No company selected");
      const form = new FormData();
      form.append("file", file);
      const token = localStorage.getItem("accessToken");
      const qs = new URLSearchParams({ jobType });
      if (showPostGl && postGl) qs.set("postGl", "true");
      const res = await fetch(
        `/api/v1/companies/${companyId}/import-jobs/upload?${qs.toString()}`,
        {
          method: "POST",
          headers: token ? { Authorization: `Bearer ${token}` } : {},
          body: form,
        }
      );
      if (!res.ok) {
        const err = (await res.json().catch(() => ({}))) as { detail?: string };
        throw new Error(err.detail ?? res.statusText);
      }
      return res.json();
    },
    onSuccess: () => {
      setFile(null);
      void invalidateTenantQueries(qc, "import-jobs");
    },
  });

  const jobs = (data?.result ?? []) as JobRow[];
  const { search, setSearch, pageRows, pagination } = useClientList({
    rows: jobs,
    syncUrl: true,
    filterFn: (r, q) => matchText([r.jobType, r.status, r.fileName, r.resultSummary], q),
  });

  const columns = responsiveListColumns<JobRow>([
    { key: "jobType", header: "Type" },
    { key: "status", header: "Status" },
    { key: "fileName", header: "File" },
    { key: "resultSummary", header: "Summary" },
    {
      key: "createdAt",
      header: "Created",
      render: (r) =>
        r.createdAt ? new Date(String(r.createdAt)).toLocaleString() : "—",
    },
  ]);

  return (
    <div>
      <PageHeader
        title="Import jobs"
        breadcrumb="Home / Settings / Import jobs"
        description="Upload CSV or Excel for masters, opening stock, product tax codes, SI/SR/VI/VP (draft or post to GL), journals, bank EP/IR, or roles."
      />
      <section className="mb-6 flex flex-wrap items-end gap-3 rounded-lg border border-border bg-surface p-4">
        <div>
          <label className="mb-1 block text-xs font-medium text-fg-muted">Job type</label>
          <Select
            value={jobType}
            onChange={(e) => setJobType(e.target.value as (typeof JOB_TYPES)[number])}
          >
            {JOB_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </Select>
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-fg-muted">File</label>
          <input
            type="file"
            accept=".csv,.xlsx"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            className="block text-sm"
          />
        </div>
        {showPostGl ? (
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={postGl}
              onChange={(e) => setPostGl(e.target.checked)}
            />
            Post to GL after import (or use column <code className="text-xs">status=posted</code>)
          </label>
        ) : null}
        <Button
          type="button"
          disabled={!file || upload.isPending}
          onClick={() => upload.mutate()}
        >
          {upload.isPending ? "Uploading…" : "Upload & enqueue"}
        </Button>
      </section>
      {upload.isError ? (
        <div className="mb-4 rounded-md border border-status-danger/30 bg-status-danger/10 p-3 text-sm text-status-danger">
          {upload.error instanceof Error ? upload.error.message : "Upload failed"}
        </div>
      ) : null}
      <ListToolbar search={search} onSearchChange={setSearch} />
      <EnterpriseGrid<JobRow>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        fetching={isFetching}
        error={error}
        emptyMessage="No import jobs yet."
        pagination={pagination}
        getRowId={(r) => String(r.id ?? "")}
      />
    </div>
  );
}
