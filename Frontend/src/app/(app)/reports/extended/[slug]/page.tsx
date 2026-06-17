"use client";
import { useTenantReportQuery } from "@/lib/api/tenant-query";


import Link from "next/link";
import { useParams } from "next/navigation";
import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { DynamicReportGrid } from "@/components/reports/dynamic-report-grid";
import {
  ReportCriteriaFields,
  type ReportCriteriaValue,
} from "@/components/reports/report-criteria-fields";
import { ReportDatePresets, type DateRangeValue } from "@/components/reports/report-date-presets";
import { ReportExportActions } from "@/components/reports/report-export-actions";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { dynamicRowsToCsv } from "@/lib/export/report-csv";
import { useReportServerPdfExport } from "@/lib/hooks/use-report-server-pdf-export";
import { reportCatalog } from "@/config/reports-catalog";
import { reportsApi } from "@/lib/api/tenant";
import { unwrapExtendedReportRows } from "@/lib/reports/extended-report-rows";

type ExtendedReportPayload =
  | Record<string, unknown>[]
  | { rows?: Record<string, unknown>[]; totals?: Record<string, unknown> };

type ExtendedReportParams = {
  dateFrom?: string;
  dateTo?: string;
  customerId?: string;
  periodCount?: number;
};

const REPORT_FETCHERS: Record<
  string,
  (p?: ExtendedReportParams) => Promise<{ result: ExtendedReportPayload }>
> = {
  "sale-invoices-by-date": (p) => reportsApi.saleInvoicesByDate(p),
  "sale-invoices-by-customer": (p) => reportsApi.saleInvoicesByCustomer(p),
  "sale-summary-by-date": (p) => reportsApi.saleSummaryByDate(p),
  "sale-summary-by-customer": (p) => reportsApi.saleSummaryByCustomer(p),
  "invoice-line-detail": (p) => reportsApi.invoiceLineDetail(p),
  "invoice-line-by-customer": (p) => reportsApi.invoiceLineByCustomer(p),
  "customer-list": () => reportsApi.customerList(),
  "customer-outstanding": (p) => reportsApi.customerOutstanding(p),
  "customer-products": (p) => reportsApi.customerProducts(p),
  "customer-performance": (p) => reportsApi.customerPerformance(p),
  "customer-balances": (p) => reportsApi.customerBalances(p),
  "supplier-balances": (p) => reportsApi.supplierBalances(p),
  "purchase-bills-by-date": (p) => reportsApi.purchaseBillsByDate(p),
  "purchase-bills-by-supplier": (p) => reportsApi.purchaseBillsBySupplier(p),
  "product-sale-detail": (p) => reportsApi.productSaleDetail(p),
  "product-purchase-detail": (p) => reportsApi.productPurchaseDetail(p),
  "product-sale-summary": (p) => reportsApi.productSaleSummary(p),
  "product-purchase-summary": (p) => reportsApi.productPurchaseSummary(p),
  "products-list": () => reportsApi.productsList(),
  "product-performance": (p) => reportsApi.productPerformance(p),
  "product-activity-summary": (p) => reportsApi.productActivitySummary(p),
  "stock-transfer-detail": (p) => reportsApi.stockTransferDetail(p),
  "stock-quantity": () => reportsApi.stockQuantity(),
  "out-of-stock": () => reportsApi.outOfStock(),
  "low-stock": () => reportsApi.lowStock(),
  "stock-valuation": () => reportsApi.stockValuation(),
  "stock-movement": (p) => reportsApi.stockMovement(p),
  "price-list": () => reportsApi.priceList(),
  "bank-payments-list": (p) => reportsApi.bankPaymentsList(p),
  "bank-payment-receipt-data": (p) => reportsApi.bankPaymentReceiptData(p),
  "bank-receipts-list": (p) => reportsApi.bankReceiptsList(p),
  "bank-transfers-list": (p) => reportsApi.bankTransfersList(p),
  "bank-activity-summary": (p) => reportsApi.bankActivitySummary(p),
  "advanced-stock-quantity": () => reportsApi.advancedStockQuantity(),
  "multi-unit-price-list": () => reportsApi.multiUnitPriceList(),
  "sale-summary-by-field": (p) => reportsApi.saleSummaryByField(p),
  "customer-field-activity": (p) => reportsApi.customerFieldActivity(p),
  "bank-account-balances": () => reportsApi.bankAccountBalances(),
  "bank-cash-flow-monthly": (p) => reportsApi.bankCashFlowMonthly(p),
  "assembly-job-cost-summary": () => reportsApi.assemblyJobCostSummary(),
  "assembly-templates": () => reportsApi.assemblyTemplates(),
  "assembly-wip": () => reportsApi.assemblyWip(),
  "assembly-component-cost": () => reportsApi.assemblyComponentCost(),
  "project-payments": (p) => reportsApi.projectPayments(p),
  "financial-monthly-balances": (p) => reportsApi.financialMonthlyBalances(p),
  "financial-trial-balance-by-month": (p) =>
    reportsApi.financialTrialBalanceByMonth({
      dateTo: p?.dateTo,
      periodCount: p?.periodCount,
    }),
};

const DATE_FILTERED_SLUGS = new Set([
  "sale-invoices-by-date",
  "sale-invoices-by-customer",
  "sale-summary-by-date",
  "sale-summary-by-customer",
  "invoice-line-detail",
  "invoice-line-by-customer",
  "customer-outstanding",
  "customer-products",
  "customer-performance",
  "customer-balances",
  "supplier-balances",
  "purchase-bills-by-date",
  "purchase-bills-by-supplier",
  "product-sale-detail",
  "product-purchase-detail",
  "product-sale-summary",
  "product-purchase-summary",
  "product-performance",
  "product-activity-summary",
  "stock-transfer-detail",
  "stock-movement",
  "bank-payments-list",
  "bank-payment-receipt-data",
  "bank-receipts-list",
  "bank-transfers-list",
  "bank-activity-summary",
  "sale-summary-by-field",
  "customer-field-activity",
  "bank-cash-flow-monthly",
  "project-payments",
  "financial-monthly-balances",
  "financial-trial-balance-by-month",
]);

const CUSTOMER_CRITERIA_SLUGS = new Set([
  "invoice-line-by-customer",
  "customer-outstanding",
  "customer-products",
]);

const FILTER_SCHEMAS: Record<string, Record<string, unknown>> = {
  "invoice-line-by-customer": {
    type: "object",
    properties: { customerId: { type: "string" } },
  },
  "customer-outstanding": {
    type: "object",
    properties: { customerId: { type: "string" } },
  },
  "customer-products": {
    type: "object",
    properties: { customerId: { type: "string" } },
  },
};

function defaultRange(): DateRangeValue {
  const now = new Date();
  const start = new Date(now.getFullYear(), now.getMonth(), 1);
  return {
    dateFrom: start.toISOString().slice(0, 10),
    dateTo: now.toISOString().slice(0, 10),
  };
}

function catalogTitle(slug: string): string {
  const hit = reportCatalog.find((r) => r.href.endsWith(`/extended/${slug}`));
  return hit?.name ?? slug.split("-").map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
}

export default function ExtendedReportPage() {
  const params = useParams<{ slug: string }>();
  const slug = params.slug;
  const fetcher = REPORT_FETCHERS[slug];
  const title = catalogTitle(slug);
  const usesDates = DATE_FILTERED_SLUGS.has(slug);
  const usesCustomer = CUSTOMER_CRITERIA_SLUGS.has(slug);
  const usesPeriodCount = slug === "financial-trial-balance-by-month";
  const [range, setRange] = useState<DateRangeValue>(() => defaultRange());
  const [criteria, setCriteria] = useState<Omit<ReportCriteriaValue, "dateFrom" | "dateTo">>({});
  const [periodCount, setPeriodCount] = useState(12);
  const [presetId, setPresetId] = useState<string | undefined>("this-month");
  const [runKey, setRunKey] = useState(0);

  const reportId = useMemo(
    () => reportCatalog.find((r) => r.href.endsWith(`/extended/${slug}`))?.id ?? slug,
    [slug],
  );

  const exportCriteria = useMemo(() => {
    const base: Record<string, unknown> = usesDates
      ? { dateFrom: range.dateFrom, dateTo: range.dateTo }
      : {};
    if (criteria.customerId) base.customerId = criteria.customerId;
    if (usesPeriodCount) base.periodCount = periodCount;
    return base;
  }, [range.dateFrom, range.dateTo, usesDates, criteria.customerId, usesPeriodCount, periodCount]);

  const { exportPdf, exportingPdf } = useReportServerPdfExport(
    reportId,
    `report-${slug}`,
  );

  const fetchParams = useMemo((): ExtendedReportParams | undefined => {
    if (!usesDates && !usesCustomer && !usesPeriodCount) return undefined;
    const p: ExtendedReportParams = {};
    if (usesDates) {
      p.dateFrom = range.dateFrom;
      p.dateTo = range.dateTo;
    }
    if (criteria.customerId) p.customerId = criteria.customerId;
    if (usesPeriodCount) p.periodCount = periodCount;
    return p;
  }, [
    usesDates,
    usesCustomer,
    usesPeriodCount,
    range.dateFrom,
    range.dateTo,
    criteria.customerId,
    periodCount,
  ]);

  const { data, isLoading, error, isFetching } = useTenantReportQuery(["extended-report",
      slug,
      range.dateFrom,
      range.dateTo,
      criteria.customerId,
      periodCount,
      runKey,], () =>
      fetcher
        ? fetcher(fetchParams)
        : Promise.resolve({ result: [] }),
    { enabled: Boolean(fetcher) });

  const rows = unwrapExtendedReportRows(data?.result);
  const filterSchema = FILTER_SCHEMAS[slug];
  const showFilters = usesDates || Boolean(filterSchema) || usesPeriodCount;

  return (
    <div>
      <PageHeader
        title={title}
        breadcrumb={`Insights / ${title}`}
        description="Extended standard report."
        actions={
          <div className="flex flex-wrap gap-2">
            <ReportExportActions
              filename={`report-${slug}`}
              enabled={rows.length > 0}
              buildCsv={() => dynamicRowsToCsv(rows)}
              onExportPdf={() => exportPdf(exportCriteria)}
              exportingPdf={exportingPdf}
            />
            <Link
              href="/reports"
              className="inline-flex h-9 items-center rounded-md border border-border bg-surface px-3 text-sm font-medium text-fg hover:bg-canvas"
            >
              ← Reports hub
            </Link>
          </div>
        }
      />

      {!fetcher && (
        <div className="alert-warning-surface mb-4 rounded-md p-3 text-sm">
          Unknown report key.
        </div>
      )}

      {showFilters ? (
        <div className="mb-4 space-y-3 rounded-lg border border-border bg-surface p-4">
          {usesDates ? (
            <>
              <ReportDatePresets
                activeId={presetId}
                onSelect={(id, next) => {
                  setPresetId(id);
                  setRange(next);
                }}
              />
              <div className="flex flex-wrap items-end gap-3">
                <label className="text-sm">
                  <span className="mb-1 block text-fg-muted">From</span>
                  <Input
                    type="date"
                    value={range.dateFrom}
                    onChange={(e) => {
                      setPresetId(undefined);
                      setRange((prev) => ({ ...prev, dateFrom: e.target.value }));
                    }}
                  />
                </label>
                <label className="text-sm">
                  <span className="mb-1 block text-fg-muted">To</span>
                  <Input
                    type="date"
                    value={range.dateTo}
                    onChange={(e) => {
                      setPresetId(undefined);
                      setRange((prev) => ({ ...prev, dateTo: e.target.value }));
                    }}
                  />
                </label>
              </div>
            </>
          ) : null}
          {filterSchema ? (
            <ReportCriteriaFields
              schema={filterSchema}
              value={{ ...range, ...criteria }}
              onChange={(next) => {
                setCriteria({
                  customerId: next.customerId,
                  supplierId: next.supplierId,
                  productCode: next.productCode,
                  status: next.status,
                });
              }}
            />
          ) : null}
          {usesPeriodCount ? (
            <label className="text-sm">
              <span className="mb-1 block text-fg-muted">Months</span>
              <Input
                type="number"
                min={1}
                max={36}
                value={periodCount}
                onChange={(e) => setPeriodCount(Number(e.target.value) || 12)}
                className="w-24"
              />
            </label>
          ) : null}
          <Button type="button" onClick={() => setRunKey((k) => k + 1)} disabled={isFetching}>
            {isFetching ? "Running…" : "Run report"}
          </Button>
        </div>
      ) : null}

      <div id="report-print-area">
        <DynamicReportGrid
          rows={rows}
          loading={isLoading}
          error={error}
          drillContext={
            usesDates
              ? { dateFrom: range.dateFrom, dateTo: range.dateTo }
              : undefined
          }
        />
      </div>
    </div>
  );
}
