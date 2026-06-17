"use client";

import Link from "next/link";

import { InsightsPanel } from "@/components/dashboard/command-center/insights-panel";
import { WidgetShell } from "@/components/dashboard/command-center/widget-shell";
import {
  InventoryTurnoverMetric,
  InventoryValueMetric,
} from "@/components/dashboard/command-center/widgets/inventory-metrics";
import type { CommandCenterPayload } from "@/components/dashboard/command-center/types/command-center";
import {
  AgingStackChart,
  DonutChart,
  DualBarChart,
  fmtAmount,
  fmtCompact,
  PnlRatioBar,
  SalesTrendChart,
} from "@/components/dashboard/dashboard-charts";
import { KpiCard } from "@/components/ui/kpi-card";
import { EmptyState } from "@/components/ui/empty-state";
import { COMMAND_CENTER_WIDGET_CATALOG } from "@/lib/dashboard/widget-catalog";
import { brandLinkClasses } from "@/lib/design-tokens/brand-surfaces";
import { cn } from "@/lib/utils";

const CHART_SERIES = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
  "var(--accent-sage)",
] as const;

function ActivityList({ rows, empty }: { rows: CommandCenterPayload["operationalActivity"]["recentTransactions"]; empty: string }) {
  if (!rows.length) return <EmptyState description={empty} className="py-4" />;
  return (
    <ul className="space-y-1.5 text-xs">
      {rows.map((r, i) => (
        <li key={`${r.entityId ?? i}`} className="flex justify-between gap-2 rounded-md px-2 py-1.5 hover:bg-surface-muted/50">
          <span className="min-w-0 truncate text-fg">
            {r.documentNumber ?? r.docType ?? "—"}
            {r.partyName ? ` · ${r.partyName}` : ""}
          </span>
          <span className="shrink-0 tabular-nums text-fg-muted">{r.documentDate?.slice(0, 10)}</span>
        </li>
      ))}
    </ul>
  );
}

function ProductList({
  rows,
  empty,
  valueKey = "quantity",
}: {
  rows: { productName?: string; productCode?: string; quantity?: string; quantitySold?: string; revenue?: string; value?: string }[];
  empty: string;
  valueKey?: "quantity" | "quantitySold" | "revenue" | "value";
}) {
  if (!rows.length) return <EmptyState description={empty} className="py-4" />;
  return (
    <ul className="space-y-1.5 text-xs">
      {rows.map((r, i) => (
        <li key={`${r.productCode ?? i}`} className="flex justify-between gap-2">
          <span className="truncate text-fg">{r.productName ?? r.productCode}</span>
          <span className="shrink-0 tabular-nums font-medium text-fg">
            {fmtCompact(String(r[valueKey] ?? r.quantity ?? r.revenue ?? r.value ?? "0"))}
          </span>
        </li>
      ))}
    </ul>
  );
}

function PartyList({ rows, empty, href }: { rows: { partyName?: string | null; balance: string }[]; empty: string; href: string }) {
  if (!rows.length) {
    return (
      <EmptyState
        description={empty}
        className="py-4"
        action={
          <Link href={href} className={cn("text-xs font-medium", brandLinkClasses)}>
            View report →
          </Link>
        }
      />
    );
  }
  return (
    <ul className="space-y-1 text-xs">
      {rows.map((r, i) => (
        <li key={`${r.partyName ?? i}`} className="flex justify-between gap-2 rounded-md px-2 py-1 hover:bg-surface-muted/50">
          <span className="truncate text-fg">{r.partyName ?? "—"}</span>
          <span className="tabular-nums font-medium">{fmtCompact(r.balance)}</span>
        </li>
      ))}
    </ul>
  );
}

export function getWidgetTitle(id: string): string {
  return COMMAND_CENTER_WIDGET_CATALOG.find((w) => w.id === id)?.label ?? id;
}

export function CommandCenterWidget({
  id,
  data,
  editMode,
}: {
  id: string;
  data: CommandCenterPayload;
  editMode?: boolean;
}) {
  const title = getWidgetTitle(id);

  switch (id) {
    case "chart-cashflow":
      return (
        <WidgetShell title={title} subtitle="Inflow vs outflow" editMode={editMode}>
          <DualBarChart data={data.bankCashFlow} inKey="inflow" outKey="outflow" labelKey="month" />
        </WidgetShell>
      );
    case "chart-sales-trend":
      return (
        <WidgetShell title={title} subtitle={`${data.salesTrend.granularity} view`} editMode={editMode}>
          <SalesTrendChart points={data.salesTrend.points} />
        </WidgetShell>
      );
    case "health-ar-aging":
      return (
        <WidgetShell title={title} editMode={editMode}>
          <AgingStackChart buckets={data.arAging.buckets} />
        </WidgetShell>
      );
    case "health-ap-aging":
      return (
        <WidgetShell title={title} editMode={editMode}>
          <AgingStackChart buckets={data.apAging.buckets} />
        </WidgetShell>
      );
    case "health-overdue-invoices":
      return (
        <WidgetShell title={title} editMode={editMode}>
          <KpiCard
            label="Overdue AR"
            value={data.overdue.arAmount}
            formatValue={(n) => fmtAmount(String(n))}
            delta={`${data.overdue.arCount} aged balance(s)`}
            deltaTone="negative"
            animateValue
          />
        </WidgetShell>
      );
    case "health-overdue-payments":
      return (
        <WidgetShell title={title} editMode={editMode}>
          <KpiCard
            label="Overdue AP"
            value={data.overdue.apAmount}
            formatValue={(n) => fmtAmount(String(n))}
            delta={`${data.overdue.apCount} aged balance(s)`}
            deltaTone="negative"
            animateValue
          />
        </WidgetShell>
      );
    case "health-top-customers":
      return (
        <WidgetShell title={title} editMode={editMode}>
          <PartyList rows={data.topCustomers} empty="No outstanding receivables." href="/reports/ar-aging" />
        </WidgetShell>
      );
    case "health-top-suppliers":
      return (
        <WidgetShell title={title} editMode={editMode}>
          <PartyList rows={data.topSuppliers} empty="No outstanding payables." href="/reports/ap-aging" />
        </WidgetShell>
      );
    case "inv-value":
      return (
        <WidgetShell title={title} subtitle="Stock on hand at cost" editMode={editMode} className="!p-3">
          <InventoryValueMetric data={data.inventoryCommand} />
        </WidgetShell>
      );
    case "inv-turnover":
      return (
        <WidgetShell title={title} subtitle="COGS ÷ average inventory" editMode={editMode} className="!p-3">
          <InventoryTurnoverMetric ratio={data.inventoryCommand.turnoverRatio} />
        </WidgetShell>
      );
    case "inv-low-stock":
      return (
        <WidgetShell title={title} editMode={editMode}>
          <ProductList rows={data.inventoryCommand.lowStock} empty="No low-stock items." />
        </WidgetShell>
      );
    case "inv-out-of-stock":
      return (
        <WidgetShell title={title} editMode={editMode}>
          <ProductList rows={data.inventoryCommand.outOfStock} empty="All SKUs have stock." />
        </WidgetShell>
      );
    case "inv-overstock":
      return (
        <WidgetShell title={title} editMode={editMode}>
          <ProductList rows={data.inventoryCommand.overstock} empty="No overstocked SKUs." valueKey="value" />
        </WidgetShell>
      );
    case "inv-fast-movers":
      return (
        <WidgetShell title={title} editMode={editMode}>
          <ProductList rows={data.inventoryCommand.fastMovers} empty="No sales in period." valueKey="quantitySold" />
        </WidgetShell>
      );
    case "inv-slow-movers":
      return (
        <WidgetShell title={title} editMode={editMode}>
          <ProductList rows={data.inventoryCommand.slowMovers} empty="No sales in period." valueKey="quantitySold" />
        </WidgetShell>
      );
    case "pnl-snapshot":
      return (
        <WidgetShell title={title} editMode={editMode}>
          <KpiCard
            label="Net profit"
            value={data.profitability.totals.netProfit}
            formatValue={(n) => fmtAmount(String(n))}
            delta={`Margin ${data.profitability.margins.netPct.toFixed(1)}%`}
            deltaTone={parseFloat(data.profitability.totals.netProfit) >= 0 ? "positive" : "negative"}
            footer={
              <Link href="/reports/profit-and-loss" className={cn("text-xs font-medium", brandLinkClasses)}>
                View P&L →
              </Link>
            }
          />
        </WidgetShell>
      );
    case "chart-expense-breakdown":
      return (
        <WidgetShell title={title} editMode={editMode}>
          <DonutChart
            segments={data.profitability.expenseBreakdown.map((row, i) => ({
              label: row.label,
              amount: row.amount,
              color: CHART_SERIES[i % CHART_SERIES.length] ?? "var(--chart-1)",
            }))}
          />
        </WidgetShell>
      );
    case "chart-revenue-breakdown":
      return (
        <WidgetShell title={title} editMode={editMode}>
          <DonutChart
            segments={data.profitability.revenueBreakdown.map((row, i) => ({
              label: row.label,
              amount: row.amount,
              color: CHART_SERIES[i % CHART_SERIES.length] ?? "var(--chart-2)",
            }))}
          />
        </WidgetShell>
      );
    case "chart-margin-analysis":
      return (
        <WidgetShell title={title} editMode={editMode}>
          <PnlRatioBar
            income={data.profitability.totals.income}
            expense={data.profitability.totals.expense}
            netProfit={data.profitability.totals.netProfit}
          />
        </WidgetShell>
      );
    case "activity-recent-tx":
      return (
        <WidgetShell title={title} editMode={editMode}>
          <ActivityList rows={data.operationalActivity.recentTransactions} empty="No recent activity." />
        </WidgetShell>
      );
    case "activity-invoices":
      return (
        <WidgetShell title={title} editMode={editMode}>
          <ActivityList rows={data.operationalActivity.latestInvoices} empty="No invoices in period." />
        </WidgetShell>
      );
    case "activity-payments":
      return (
        <WidgetShell title={title} editMode={editMode}>
          <ActivityList rows={data.operationalActivity.latestPayments} empty="No payments in period." />
        </WidgetShell>
      );
    case "activity-stock-adj":
      return (
        <WidgetShell title={title} editMode={editMode}>
          <ActivityList rows={data.operationalActivity.stockAdjustments} empty="No stock adjustments." />
        </WidgetShell>
      );
    case "activity-audit":
      return (
        <WidgetShell title={title} editMode={editMode}>
          {!data.operationalActivity.auditEntries.length ? (
            <EmptyState description="No audit entries." className="py-4" />
          ) : (
            <ul className="space-y-1.5 text-xs">
              {data.operationalActivity.auditEntries.map((e) => (
                <li key={e.id} className="flex justify-between gap-2">
                  <span className="truncate text-fg">{e.transactionType}</span>
                  <span className="text-fg-muted">{e.timestamp.slice(0, 10)}</span>
                </li>
              ))}
            </ul>
          )}
        </WidgetShell>
      );
    case "insights-panel":
      return (
        <WidgetShell title={title} subtitle="AI-assisted business signals" editMode={editMode}>
          <InsightsPanel insights={data.insights} />
        </WidgetShell>
      );
    default:
      return (
        <WidgetShell title={title} editMode={editMode}>
          <p className="text-sm text-fg-muted">Widget not configured.</p>
        </WidgetShell>
      );
  }
}
