/** Command center dashboard types — mirrors GET /dashboard/command-center */

import type { AgingResult, AgingRow, ProductBatch } from "@/lib/api/tenant";

export type CommandCenterPeriod = "mtd" | "qtd" | "ytd" | "fy";
export type SalesGranularity = "day" | "week" | "month";
export type KpiStatus = "good" | "warn" | "critical" | "neutral";
export type InsightSeverity = "good" | "warn" | "critical" | "info";

export interface ExecutiveKpi {
  id: string;
  label: string;
  value: string;
  priorValue: string;
  changePct: number | null;
  trendSeries: number[];
  status: KpiStatus;
  drillDownHref: string;
}

export interface InsightCard {
  id: string;
  severity: InsightSeverity;
  title: string;
  message: string;
  actionHref: string;
  actionLabel: string;
}

export interface ProductStockRow {
  productCode?: string;
  productName?: string;
  quantity: string;
  value: string;
}

export interface ProductMoverRow {
  productCode?: string;
  productName?: string;
  quantitySold: string;
  revenue: string;
}

export interface ActivityRow {
  entityType?: string;
  entityId?: string;
  docType?: string;
  documentNumber?: string;
  documentDate?: string;
  partyName?: string | null;
  totalAmount?: string;
  status?: string;
}

export interface AuditEntry {
  id: string;
  timestamp: string;
  transactionType: string;
  transactionId?: string | null;
  status?: string | null;
  details?: string | null;
  userId?: string | null;
  userName?: string | null;
}

export interface CommandCenterPayload {
  period: {
    from: string;
    to: string;
    priorFrom: string;
    priorTo: string;
    key: string;
  };
  executiveKpis: ExecutiveKpi[];
  bankCashFlow: { month: string; inflow: string; outflow: string; net: string }[];
  bankBalances: { bankAccountId?: string; name: string; balance: string; currency?: string }[];
  salesTrend: { granularity: string; points: { label: string; value: string }[] };
  salesByMonth: { month: string; totalSales: string }[];
  arAging: AgingResult;
  apAging: AgingResult;
  overdue: { arCount: number; arAmount: string; apCount: number; apAmount: string };
  topCustomers: AgingRow[];
  topSuppliers: AgingRow[];
  arTopParties: AgingRow[];
  apTopParties: AgingRow[];
  inventoryCommand: {
    totalValue: string;
    turnoverRatio: number | null;
    lowStock: ProductStockRow[];
    outOfStock: ProductStockRow[];
    overstock: ProductStockRow[];
    fastMovers: ProductMoverRow[];
    slowMovers: ProductMoverRow[];
    bucketCounts: { inStock: number; lowStock: number; outOfStock: number; oversold: number };
    expiringBatches?: {
      windowDays: number;
      expired: number;
      expiringSoon: number;
      totalAlertable: number;
      preview: ProductBatch[];
    };
  };
  inventoryStock: { inStock: number; lowStock: number; outOfStock: number; oversold: number };
  profitability: {
    totals: { income: string; cogs: string; grossProfit: string; expense: string; netProfit: string };
    expenseBreakdown: { label: string; amount: string; pct: number }[];
    revenueBreakdown: { label: string; amount: string; pct: number }[];
    margins: { grossPct: number; netPct: number };
  };
  profitAndLoss: {
    totals: { income: string; expense: string; netProfit: string };
    expenseBreakdown: { label: string; amount: string }[];
  };
  operationalActivity: {
    recentTransactions: ActivityRow[];
    latestInvoices: ActivityRow[];
    latestPayments: ActivityRow[];
    stockAdjustments: ActivityRow[];
    auditEntries: AuditEntry[];
  };
  insights: InsightCard[];
  financialYearFrom: string;
  financialYearTo: string;
}

export interface GridLayoutItem {
  i: string;
  x: number;
  y: number;
  w: number;
  h: number;
  minW?: number;
  minH?: number;
}

export interface DashboardView {
  id: string;
  name: string;
  isDefault?: boolean;
  rolePreset?: "owner" | "cfo" | "accountant" | "manager";
  layout: GridLayoutItem[];
}

export interface DashboardLayoutSettings {
  widgets: string[];
  views: DashboardView[];
  activeViewId: string;
}
