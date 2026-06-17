/** User Log viewer — catalog §12.15. */
"use client";
import { useTenantReferenceQuery, useTenantListQuery } from "@/lib/api/tenant-query";

import { brandLinkClasses } from "@/lib/design-tokens/brand-surfaces";
import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { ListToolbar } from "@/components/ui/list-toolbar";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { useToast } from "@/components/ui/toast";
import { Select } from "@/components/ui/select";
import { useRouter } from "next/navigation";
import { useConfiguredListColumns } from "@/lib/hooks/use-configured-list-columns";
import { auditNavigationHref, auditNavigationLabel, userLogHref } from "@/lib/rbac/audit-log";
import { AUDIT_LOG_PRESETS } from "@/lib/rbac/audit-log-presets";
import {
  deleteSavedAuditPreset,
  exportSavedAuditPresetsJson,
  importSavedAuditPresetsFromJson,
  loadSavedAuditPresets,
  saveAuditPreset,
  type SavedAuditPreset,
} from "@/lib/rbac/audit-log-saved-presets";
import { auditApi, type AuditLogEntry, type AuditLogFilters } from "@/lib/api/tenant";
import { useClientList } from "@/lib/hooks/use-client-list";
import { matchText } from "@/lib/list/document-list-filters";
import { paginatedListQueryOptions, referenceQueryOptions } from "@/lib/query/options";
import { cn } from "@/lib/utils";

function buildColumns(): GridColumn<AuditLogEntry>[] {
  return responsiveListColumns<AuditLogEntry>([
    {
      key: "timestamp",
      header: "Timestamp",
      sortable: true,
      sortAccessor: (r) => r.timestamp,
      render: (r) => new Date(r.timestamp).toLocaleString(),
    },
    { key: "transactionType", header: "Transaction type" },
    { key: "transactionId", header: "Transaction ID" },
    { key: "status", header: "Status" },
    { key: "details", header: "Details" },
    { key: "userName", header: "User" },
    {
      key: "view",
      header: "",
      render: (r) => {
        const href = auditNavigationHref(r);
        if (!href) return "—";
        return (
          <Link href={href} className={cn("text-sm font-medium hover:underline", brandLinkClasses)}>
            {auditNavigationLabel(r)}
          </Link>
        );
      },
    },
  ], { primaryKey: "timestamp" });
}

function filtersFromSearchParams(
  searchParams: URLSearchParams
): AuditLogFilters & { type?: string } {
  const transactionType = searchParams.get("transactionType") ?? undefined;
  const transactionId = searchParams.get("transactionId") ?? undefined;
  const userId = searchParams.get("userId") ?? undefined;
  const dateFrom = searchParams.get("dateFrom") ?? undefined;
  const dateTo = searchParams.get("dateTo") ?? undefined;
  const rbacOnly = searchParams.get("rbacOnly") === "true";
  const typeContains = searchParams.get("typeContains") ?? undefined;

  let type = "";
  if (rbacOnly) type = "rbac";
  else if (transactionType === "LOGIN") type = "login";
  else if (typeContains === "BANK") type = "bank";
  else if (transactionType) type = transactionType;

  return {
    type,
    userId,
    dateFrom,
    dateTo,
    transactionType,
    transactionId,
    rbacOnly: rbacOnly || undefined,
    typeContains,
  };
}

function toAppliedFilters(
  draft: AuditLogFilters & { type?: string }
): AuditLogFilters {
  const type = draft.type ?? "";
  if (type === "rbac") {
    return {
      userId: draft.userId || undefined,
      dateFrom: draft.dateFrom || undefined,
      dateTo: draft.dateTo || undefined,
      transactionId: draft.transactionId || undefined,
      rbacOnly: true,
    };
  }
  if (type === "bank" || draft.typeContains) {
    return {
      userId: draft.userId || undefined,
      dateFrom: draft.dateFrom || undefined,
      dateTo: draft.dateTo || undefined,
      transactionId: draft.transactionId || undefined,
      typeContains: draft.typeContains || "BANK",
    };
  }
  if (type === "login") {
    return {
      userId: draft.userId || undefined,
      dateFrom: draft.dateFrom || undefined,
      dateTo: draft.dateTo || undefined,
      transactionId: draft.transactionId || undefined,
      transactionType: draft.transactionType || "LOGIN",
    };
  }
  return {
    userId: draft.userId || undefined,
    dateFrom: draft.dateFrom || undefined,
    dateTo: draft.dateTo || undefined,
    transactionId: draft.transactionId || undefined,
    transactionType:
      type && type !== "logout" && type !== "transaction" ? type : draft.transactionType,
  };
}

export default function UserLogPage() {
  const router = useRouter();
  const toast = useToast();
  const searchParams = useSearchParams();
  const baseColumns = useMemo(() => buildColumns(), []);
  const columns = useConfiguredListColumns("user-log", baseColumns);
  const initial = filtersFromSearchParams(searchParams);
  const [filters, setFilters] = useState<AuditLogFilters>(() => toAppliedFilters(initial));
  const [draft, setDraft] = useState<AuditLogFilters & { type?: string }>(initial);
  const [bookmarkMessage, setBookmarkMessage] = useState<string | null>(null);
  const [savedPresets, setSavedPresets] = useState<SavedAuditPreset[]>([]);
  const [savePresetName, setSavePresetName] = useState("");
  const importPresetsRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setSavedPresets(loadSavedAuditPresets());
  }, []);

  useEffect(() => {
    const next = filtersFromSearchParams(searchParams);
    setDraft(next);
    setFilters(toAppliedFilters(next));
  }, [searchParams]);

  const { data: transactionTypeGroups } = useTenantReferenceQuery(["audit-log-transaction-types"], () => auditApi.listTransactionTypes());

  const { data, isLoading, error, isFetching } = useTenantListQuery(["audit-log", filters], () => auditApi.list(filters));

  const { search, setSearch, pageRows, pagination } = useClientList({
    rows: data?.result,
    syncUrl: true,
    filterFn: (r, q) =>
      matchText(
        [r.transactionType, r.transactionId, r.status, r.details, r.userName, r.userId],
        q,
      ),
  });

  function apply() {
    setFilters(toAppliedFilters(draft));
    router.push(userLogHref(toAppliedFilters(draft)));
  }

  function applyPreset(preset: { draft: AuditLogFilters & { type?: string } }) {
    setDraft(preset.draft);
    const next = toAppliedFilters(preset.draft);
    setFilters(next);
    router.push(userLogHref(next));
  }

  function handleSavePreset() {
    try {
      const preset = saveAuditPreset(savePresetName, draft);
      setSavedPresets(loadSavedAuditPresets());
      setSavePresetName("");
      setBookmarkMessage(`Saved preset “${preset.label}”.`);
    } catch (e) {
      setBookmarkMessage(e instanceof Error ? e.message : "Save failed");
    }
  }

  function handleDeletePreset(id: string) {
    deleteSavedAuditPreset(id);
    setSavedPresets(loadSavedAuditPresets());
  }

  const bookmarkPath = userLogHref(toAppliedFilters(draft));

  async function copyBookmark() {
    const url =
      typeof window !== "undefined"
        ? `${window.location.origin}${bookmarkPath}`
        : bookmarkPath;
    try {
      await navigator.clipboard.writeText(url);
      setBookmarkMessage("Bookmark link copied.");
      router.push(bookmarkPath);
    } catch {
      setBookmarkMessage("Copy failed — use Apply to update the address bar.");
    }
  }

  return (
    <div>
      <PageHeader
        title="User Log"
        breadcrumb="Home / User Log"
        description="Read-only audit trail of sign-ins and transactional events (§12.15)."
      />

      <div className="mb-4 rounded-lg border border-border bg-surface p-4">
        <div className="mb-3 flex flex-wrap gap-2">
          <span className="self-center text-xs font-medium uppercase tracking-wide text-fg-muted">
            Presets
          </span>
          {AUDIT_LOG_PRESETS.map((preset) => (
            <Button
              key={preset.id}
              type="button"
              variant="outline"
              onClick={() => applyPreset(preset)}
            >
              {preset.label}
            </Button>
          ))}
          {savedPresets.map((preset) => (
            <span key={preset.id} className="inline-flex items-center gap-1">
              <Button
                type="button"
                variant="outline"
                onClick={() => applyPreset(preset)}
              >
                {preset.label}
              </Button>
              <button
                type="button"
                className="rounded px-1 text-xs text-fg-muted hover:bg-canvas hover:text-status-danger"
                aria-label={`Remove preset ${preset.label}`}
                onClick={() => handleDeletePreset(preset.id)}
              >
                ×
              </button>
            </span>
          ))}
        </div>
        <div className="mb-3 flex flex-wrap items-end gap-2">
          <FormField label="Save preset">
            <Input
              className="w-48"
              placeholder="My filter name"
              value={savePresetName}
              onChange={(e) => setSavePresetName(e.target.value)}
            />
          </FormField>
          <Button
            type="button"
            variant="outline"
            disabled={!savePresetName.trim()}
            onClick={handleSavePreset}
          >
            Save current filters
          </Button>
          <Button
            type="button"
            variant="outline"
            disabled={savedPresets.length === 0}
            onClick={() => {
              const blob = new Blob([exportSavedAuditPresetsJson()], {
                type: "application/json",
              });
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = "audit-log-presets.json";
              a.click();
              URL.revokeObjectURL(url);
              setBookmarkMessage("Exported saved presets.");
            }}
          >
            Export presets JSON
          </Button>
          <input
            ref={importPresetsRef}
            type="file"
            accept=".json,application/json"
            className="hidden"
            onChange={async (e) => {
              const file = e.target.files?.[0];
              e.target.value = "";
              if (!file) return;
              try {
                const text = await file.text();
                const count = importSavedAuditPresetsFromJson(text, { merge: true });
                setSavedPresets(loadSavedAuditPresets());
                setBookmarkMessage(`Imported ${count} preset(s).`);
              } catch (err) {
                setBookmarkMessage(
                  err instanceof Error ? err.message : "Import failed"
                );
              }
            }}
          />
          <Button
            type="button"
            variant="outline"
            onClick={() => importPresetsRef.current?.click()}
          >
            Import presets JSON
          </Button>
        </div>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
          <FormField label="Type">
            <Select
              value={draft.type ?? (draft.typeContains === "BANK" ? "bank" : "")}
              onChange={(e) => {
                const v = e.target.value;
                setDraft((s) => ({
                  ...s,
                  type: v,
                  rbacOnly: undefined,
                  typeContains: v === "bank" ? "BANK" : undefined,
                  transactionType: v === "login" ? "LOGIN" : undefined,
                }));
              }}
            >
              <option value="">All</option>
              <option value="rbac">Users &amp; roles (RBAC)</option>
              <option value="bank">Bank (all types)</option>
              {(transactionTypeGroups?.result ?? []).map((group) => (
                <optgroup key={group.group} label={group.group}>
                  {group.types.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.label}
                    </option>
                  ))}
                </optgroup>
              ))}
              <option value="login">Log in</option>
              <option value="logout">Log out</option>
              <option value="transaction">Transactions</option>
            </Select>
          </FormField>
          <FormField label="Transaction ID">
            <Input
              placeholder="Optional (e.g. import job id)"
              value={draft.transactionId ?? ""}
              onChange={(e) => setDraft((s) => ({ ...s, transactionId: e.target.value }))}
            />
          </FormField>
          <FormField label="User ID">
            <Input
              placeholder="Optional"
              value={draft.userId ?? ""}
              onChange={(e) => setDraft((s) => ({ ...s, userId: e.target.value }))}
            />
          </FormField>
          <FormField label="Date from">
            <Input
              type="date"
              value={draft.dateFrom ?? ""}
              onChange={(e) => setDraft((s) => ({ ...s, dateFrom: e.target.value }))}
            />
          </FormField>
          <FormField label="Date to">
            <Input
              type="date"
              value={draft.dateTo ?? ""}
              onChange={(e) => setDraft((s) => ({ ...s, dateTo: e.target.value }))}
            />
          </FormField>
        </div>
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <Button type="button" onClick={apply}>
            Apply
          </Button>
          <Button type="button" variant="outline" onClick={() => void copyBookmark()}>
            Copy bookmark link
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => {
              setDraft({});
              setFilters({});
              setBookmarkMessage(null);
              router.push("/settings/user-log");
            }}
          >
            Clear
          </Button>
          {bookmarkMessage && (
            <span className="text-xs text-fg-muted">{bookmarkMessage}</span>
          )}
          <code className="max-w-full truncate text-xs text-fg-muted" title={bookmarkPath}>
            {bookmarkPath}
          </code>
          <Button
            type="button"
            variant="outline"
            onClick={async () => {
              try {
                const blob = await auditApi.downloadCsv(filters);
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = "audit-log.csv";
                a.click();
                URL.revokeObjectURL(url);
              } catch (e) {
                toast.error(e instanceof Error ? e.message : "Export failed");
              }
            }}
          >
            Export CSV (filtered)
          </Button>
          {isFetching && <span className="self-center text-xs text-fg-muted">Refreshing…</span>}
        </div>
      </div>

      <ListToolbar search={search} onSearchChange={setSearch} />
      <EnterpriseGrid<AuditLogEntry>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        fetching={isFetching}
        error={error}
        emptyMessage="No log entries match the current filter."
        pagination={pagination}
        getRowId={(r) => r.id}
        onRowClick={(r) => {
          const href = auditNavigationHref(r);
          if (href) router.push(href);
        }}
      />
    </div>
  );
}
