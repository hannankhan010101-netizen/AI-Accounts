"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import Link from "next/link";
import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import Decimal from "decimal.js";

import { Button } from "@/components/ui/button";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { ReportExportActions } from "@/components/reports/report-export-actions";
import { ReportDatePresets } from "@/components/reports/report-date-presets";
import { buildGridExport } from "@/lib/export/grid-export";
import { recordsToCsv } from "@/lib/export/csv";
import { useClientList } from "@/lib/hooks/use-client-list";
import { matchText } from "@/lib/list/document-list-filters";
import { buildStatementLineHref } from "@/lib/reports/report-drilldown";
import { useReportServerPdfExport } from "@/lib/hooks/use-report-server-pdf-export";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import {
  partiesApi,
  reportsApi,
  type StatementLine,
  type StatementResult,
} from "@/lib/api/tenant";

function fmt(v: string): string {
  try {
    return new Decimal(v).toFixed(2);
  } catch {
    return v;
  }
}

interface Params {
  partyId: string;
  dateFrom?: string;
  dateTo?: string;
}

interface StatementReportProps {
  kind: "customer" | "supplier";
}

function StatementInner({ kind }: StatementReportProps) {
  const urlSearch = useSearchParams();
  const queryParam = kind === "customer" ? "customerId" : "supplierId";
  const initialId = urlSearch.get(queryParam) ?? "";

  const [presetId, setPresetId] = useState<string | undefined>();
  const [draft, setDraft] = useState<Params>({
    partyId: initialId,
    dateFrom: "",
    dateTo: "",
  });
  const [params, setParams] = useState<Params | null>(
    initialId ? { partyId: initialId } : null,
  );

  useEffect(() => {
    const id = urlSearch.get(queryParam);
    if (id) {
      setDraft((s) => ({ ...s, partyId: id }));
      setParams({ partyId: id });
    }
  }, [urlSearch, queryParam]);

  const partiesQuery = useTenantListQuery([kind === "customer" ? "customers" : "suppliers"], () =>
      kind === "customer" ? partiesApi.listCustomers() : partiesApi.listSuppliers());

  const { data, isLoading, error, isFetching } = useTenantListQuery(["statement", kind, params], () => {
      if (!params?.partyId) throw new Error("partyId required");
      const args = {
        dateFrom: params.dateFrom ? new Date(params.dateFrom).toISOString() : undefined,
        dateTo: params.dateTo ? new Date(params.dateTo).toISOString() : undefined,
      };
      return kind === "customer"
        ? reportsApi.customerStatement({ customerId: params.partyId, ...args })
        : reportsApi.supplierStatement({ supplierId: params.partyId, ...args });
    },
    { enabled: !!params?.partyId });

  const result: StatementResult | undefined = data?.result;
  const reportId = kind === "customer" ? "034" : "054";
  const { exportPdf, exportingPdf } = useReportServerPdfExport(
    reportId,
    kind === "customer" ? "customer-statement" : "supplier-statement",
  );

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows: result?.lines,
    syncUrl: true,
    filterFn: (r, q) => matchText([r.kind, r.reference, r.id], q),
  });

  const columns = responsiveListColumns<StatementLine>([
    {
      key: "date",
      header: "Date",
      render: (r) => new Date(r.date).toLocaleDateString(),
    },
    { key: "kind", header: "Type" },
    {
      key: "reference",
      header: "Reference",
      render: (r) => {
        const href = buildStatementLineHref(r.kind, r.id);
        if (!href || !r.reference) return r.reference ?? "—";
        return (
          <Link href={href} className="text-brand hover:underline">
            {r.reference}
          </Link>
        );
      },
    },
    { key: "debit", header: "Debit", align: "right", render: (r) => fmt(r.debit) },
    { key: "credit", header: "Credit", align: "right", render: (r) => fmt(r.credit) },
    {
      key: "balance",
      header: "Balance",
      align: "right",
      render: (r) => fmt(r.balance),
    },
  ]);

  return (
    <>
      <div className="mb-4 rounded-lg border border-border bg-surface p-4">
        <ReportDatePresets
          activeId={presetId}
          onSelect={(id, range) => {
            setPresetId(id);
            setDraft((s) => ({ ...s, dateFrom: range.dateFrom, dateTo: range.dateTo }));
          }}
        />
        <div className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-3">
          <FormField label={kind === "customer" ? "Customer" : "Supplier"} required>
            <Select
              value={draft.partyId}
              onChange={(e) => setDraft((s) => ({ ...s, partyId: e.target.value }))}
            >
              <option value="">Select…</option>
              {partiesQuery.data?.result.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                  {"code" in p && p.code ? ` (${p.code})` : ""}
                </option>
              ))}
            </Select>
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
        <div className="mt-3 flex gap-2">
          <Button
            type="button"
            disabled={!draft.partyId}
            onClick={() => setParams({ ...draft })}
          >
            Run report
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => {
              setDraft({ partyId: "", dateFrom: "", dateTo: "" });
              setParams(null);
              setPresetId(undefined);
              setSearch("");
            }}
          >
            Clear
          </Button>
          {isFetching && <span className="self-center text-xs text-fg-muted">Refreshing…</span>}
          <ReportExportActions
            filename={kind === "customer" ? "customer-statement" : "supplier-statement"}
            enabled={!!result}
            buildCsv={() => recordsToCsv(filtered as Record<string, unknown>[])}
            exportingPdf={exportingPdf}
            onExportPdf={() => {
              if (!params?.partyId) return;
              const criteria: Record<string, unknown> = {
                [queryParam]: params.partyId,
              };
              if (params.dateFrom) criteria.dateFrom = params.dateFrom;
              if (params.dateTo) criteria.dateTo = params.dateTo;
              return exportPdf(criteria);
            }}
          />
        </div>
      </div>

      {!params?.partyId ? (
        <div className="rounded-lg border border-dashed border-border bg-surface p-8 text-center text-sm text-fg-muted">
          Select a {kind} and click <span className="font-medium">Run report</span>.
        </div>
      ) : (
        <div id="report-print-area">
          {result && (
            <div className="mb-3 rounded-lg border border-brand-200 p-4 surface-brand-soft dark:border-brand-400/30">
              <div className="text-xs font-medium uppercase tracking-wide">
                {result.party.name ?? result.party.id} {result.party.code ? `(${result.party.code})` : ""}
              </div>
              <div className="mt-1 flex items-baseline justify-between">
                <span className="text-sm">Outstanding balance</span>
                <span className="text-xl font-semibold tabular-nums text-brand-900 dark:text-brand-200">
                  {fmt(result.totals.balance)}
                </span>
              </div>
            </div>
          )}
          <div className="mb-3">
            <Input
              type="search"
              placeholder="Filter lines…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <EnterpriseGrid<StatementLine>
            columns={columns}
            rows={pageRows}
            loading={isLoading}
            error={error}
            emptyMessage="No activity for this party in the chosen window."
            getRowId={(r) => `${r.kind}-${r.id}`}
            pagination={pagination}
            exportCsv={{
              ...buildGridExport(
                kind === "customer" ? "customer-statement" : "supplier-statement",
                columns,
              ),
              rows: filtered,
            }}
          />
        </div>
      )}
    </>
  );
}

export function StatementReport({ kind }: StatementReportProps) {
  return (
    <Suspense fallback={null}>
      <StatementInner kind={kind} />
    </Suspense>
  );
}
