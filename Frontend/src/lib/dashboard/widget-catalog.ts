/** Command center widget catalog v2 + layout defaults + legacy migration */

import type { DashboardView, GridLayoutItem } from "@/components/dashboard/command-center/types/command-center";

export type DashboardWidgetDef = {
  id: string;
  label: string;
  group: string;
  row: number;
  kpiOnly?: boolean;
};

export const COMMAND_CENTER_WIDGET_CATALOG: DashboardWidgetDef[] = [
  { id: "kpi-cash", label: "Cash Available", group: "Executive", row: 1, kpiOnly: true },
  { id: "kpi-bank", label: "Bank Balance", group: "Executive", row: 1, kpiOnly: true },
  { id: "kpi-revenue", label: "Monthly Revenue", group: "Executive", row: 1, kpiOnly: true },
  { id: "kpi-gross-profit", label: "Gross Profit", group: "Executive", row: 1, kpiOnly: true },
  { id: "kpi-net-profit", label: "Net Profit", group: "Executive", row: 1, kpiOnly: true },
  { id: "kpi-ar", label: "Accounts Receivable", group: "Executive", row: 1, kpiOnly: true },
  { id: "kpi-ap", label: "Accounts Payable", group: "Executive", row: 1, kpiOnly: true },
  { id: "kpi-inventory-value", label: "Inventory Value", group: "Executive", row: 1, kpiOnly: true },
  { id: "chart-cashflow", label: "Cashflow Chart", group: "Cashflow", row: 2 },
  { id: "chart-sales-trend", label: "Sales Trend", group: "Cashflow", row: 2 },
  { id: "health-ar-aging", label: "AR Aging", group: "Health", row: 3 },
  { id: "health-ap-aging", label: "AP Aging", group: "Health", row: 3 },
  { id: "health-overdue-invoices", label: "Overdue Invoices", group: "Health", row: 3 },
  { id: "health-overdue-payments", label: "Overdue Payments", group: "Health", row: 3 },
  { id: "health-top-customers", label: "Top Customers", group: "Health", row: 3 },
  { id: "health-top-suppliers", label: "Top Suppliers", group: "Health", row: 3 },
  { id: "inv-value", label: "Inventory Value", group: "Inventory", row: 4 },
  { id: "inv-low-stock", label: "Low Stock Items", group: "Inventory", row: 4 },
  { id: "inv-out-of-stock", label: "Out of Stock", group: "Inventory", row: 4 },
  { id: "inv-overstock", label: "Overstocked Items", group: "Inventory", row: 4 },
  { id: "inv-fast-movers", label: "Fast Moving Products", group: "Inventory", row: 4 },
  { id: "inv-slow-movers", label: "Slow Moving Products", group: "Inventory", row: 4 },
  { id: "inv-turnover", label: "Inventory Turnover", group: "Inventory", row: 4 },
  { id: "pnl-snapshot", label: "P&L Snapshot", group: "Profitability", row: 5 },
  { id: "chart-expense-breakdown", label: "Expense Breakdown", group: "Profitability", row: 5 },
  { id: "chart-revenue-breakdown", label: "Revenue Breakdown", group: "Profitability", row: 5 },
  { id: "chart-margin-analysis", label: "Margin Analysis", group: "Profitability", row: 5 },
  { id: "activity-recent-tx", label: "Recent Transactions", group: "Activity", row: 6 },
  { id: "activity-invoices", label: "Latest Invoices", group: "Activity", row: 6 },
  { id: "activity-payments", label: "Latest Payments", group: "Activity", row: 6 },
  { id: "activity-stock-adj", label: "Stock Adjustments", group: "Activity", row: 6 },
  { id: "activity-audit", label: "Audit Activities", group: "Activity", row: 6 },
  { id: "insights-panel", label: "Alerts & Insights", group: "Insights", row: 7 },
];

export const DEFAULT_COMMAND_CENTER_WIDGETS = COMMAND_CENTER_WIDGET_CATALOG.map((w) => w.id);

export const DEFAULT_COMMAND_CENTER_LAYOUT: GridLayoutItem[] = [
  { i: "chart-cashflow", x: 0, y: 0, w: 6, h: 4, minW: 4, minH: 3 },
  { i: "chart-sales-trend", x: 6, y: 0, w: 6, h: 4, minW: 4, minH: 3 },
  { i: "health-ar-aging", x: 0, y: 4, w: 4, h: 3, minW: 3, minH: 2 },
  { i: "health-ap-aging", x: 4, y: 4, w: 4, h: 3, minW: 3, minH: 2 },
  { i: "health-overdue-invoices", x: 8, y: 4, w: 2, h: 3, minW: 2, minH: 2 },
  { i: "health-overdue-payments", x: 10, y: 4, w: 2, h: 3, minW: 2, minH: 2 },
  { i: "health-top-customers", x: 0, y: 7, w: 6, h: 3, minW: 3, minH: 2 },
  { i: "health-top-suppliers", x: 6, y: 7, w: 6, h: 3, minW: 3, minH: 2 },
  { i: "inv-value", x: 0, y: 10, w: 3, h: 3, minW: 2, minH: 3 },
  { i: "inv-turnover", x: 3, y: 10, w: 3, h: 3, minW: 2, minH: 3 },
  { i: "inv-low-stock", x: 6, y: 10, w: 3, h: 3, minW: 2, minH: 2 },
  { i: "inv-out-of-stock", x: 9, y: 10, w: 3, h: 3, minW: 2, minH: 2 },
  { i: "inv-overstock", x: 0, y: 13, w: 4, h: 3, minW: 2, minH: 2 },
  { i: "inv-fast-movers", x: 4, y: 13, w: 4, h: 3, minW: 2, minH: 2 },
  { i: "inv-slow-movers", x: 8, y: 13, w: 4, h: 3, minW: 2, minH: 2 },
  { i: "pnl-snapshot", x: 0, y: 16, w: 3, h: 3, minW: 2, minH: 2 },
  { i: "chart-margin-analysis", x: 3, y: 16, w: 3, h: 3, minW: 2, minH: 2 },
  { i: "chart-expense-breakdown", x: 6, y: 16, w: 3, h: 3, minW: 2, minH: 2 },
  { i: "chart-revenue-breakdown", x: 9, y: 16, w: 3, h: 3, minW: 2, minH: 2 },
  { i: "activity-recent-tx", x: 0, y: 19, w: 6, h: 3, minW: 3, minH: 2 },
  { i: "activity-invoices", x: 6, y: 19, w: 3, h: 3, minW: 2, minH: 2 },
  { i: "activity-payments", x: 9, y: 19, w: 3, h: 3, minW: 2, minH: 2 },
  { i: "activity-stock-adj", x: 0, y: 22, w: 6, h: 3, minW: 2, minH: 2 },
  { i: "activity-audit", x: 6, y: 22, w: 6, h: 3, minW: 2, minH: 2 },
  { i: "insights-panel", x: 0, y: 25, w: 12, h: 3, minW: 6, minH: 2 },
];

export const DEFAULT_DASHBOARD_VIEW: DashboardView = {
  id: "default",
  name: "Executive",
  isDefault: true,
  rolePreset: "owner",
  layout: DEFAULT_COMMAND_CENTER_LAYOUT,
};

const LEGACY_WIDGET_MAP: Record<string, string[]> = {
  "ar-summary": ["kpi-ar", "health-ar-aging"],
  "ap-summary": ["kpi-ap", "health-ap-aging"],
  "bank-balances": ["kpi-bank", "kpi-cash"],
  "bank-cash-flow": ["chart-cashflow"],
  "sales-fy": ["chart-sales-trend", "kpi-revenue"],
  "expenses-fy": ["chart-expense-breakdown"],
  "pnl-fy": ["pnl-snapshot", "kpi-net-profit", "kpi-gross-profit"],
  "products-inventory": ["inv-value", "inv-low-stock", "inv-out-of-stock"],
  "ar-top-10": ["health-top-customers"],
  "ap-top-10": ["health-top-suppliers"],
};

const LEGACY_RECENT_ACTIVITY_WIDGETS = [
  "bank-cash-flow",
  "products-inventory",
  "sales-fy",
  "expenses-fy",
  "pnl-fy",
  "ar-top-10",
  "ar-watchlist",
  "ap-top-10",
  "ap-watchlist",
  "bank-balances-watchlist",
  "monthly-bank-balance",
  "monthly-bank-balance-watchlist",
  "bank-cash-flow-watchlist",
  "quick-links",
] as const;

/** Map legacy widget ids to command-center ids; pass through known v2 ids. */
export function migrateDashboardWidgets(raw: unknown): Set<string> {
  if (!Array.isArray(raw) || raw.length === 0) {
    return new Set(DEFAULT_COMMAND_CENTER_WIDGETS);
  }
  const out = new Set<string>();
  for (const id of raw) {
    if (typeof id !== "string") continue;
    if (id === "recent-activity") {
      for (const w of LEGACY_RECENT_ACTIVITY_WIDGETS) {
        for (const mapped of LEGACY_WIDGET_MAP[w] ?? []) out.add(mapped);
      }
      continue;
    }
    if (DEFAULT_COMMAND_CENTER_WIDGETS.includes(id)) {
      out.add(id);
      continue;
    }
    for (const mapped of LEGACY_WIDGET_MAP[id] ?? []) out.add(mapped);
  }
  if (out.size === 0) return new Set(DEFAULT_COMMAND_CENTER_WIDGETS);
  return out;
}

export function resolveDashboardWidgets(raw: unknown): Set<string> {
  return migrateDashboardWidgets(raw);
}

export const ROLE_WIDGET_GROUPS: Record<string, Set<string>> = {
  owner: new Set(DEFAULT_COMMAND_CENTER_WIDGETS),
  cfo: new Set(DEFAULT_COMMAND_CENTER_WIDGETS),
  accountant: new Set(
    COMMAND_CENTER_WIDGET_CATALOG.filter(
      (w) =>
        w.row === 1 ||
        w.row === 3 ||
        w.row === 5 ||
        w.row === 6 ||
        w.row === 7 ||
        (w.row === 4 && (w.id === "inv-value" || w.id === "inv-turnover")),
    ).map((w) => w.id),
  ),
  manager: new Set(
    COMMAND_CENTER_WIDGET_CATALOG.filter((w) => [1, 2, 4, 7].includes(w.row)).map((w) => w.id),
  ),
};

/** @deprecated use COMMAND_CENTER_WIDGET_CATALOG */
export const DASHBOARD_WIDGET_CATALOG = COMMAND_CENTER_WIDGET_CATALOG.map(({ id, label, group }) => ({
  id,
  label,
  group,
}));

export const DEFAULT_DASHBOARD_WIDGETS = DEFAULT_COMMAND_CENTER_WIDGETS;

/** Optional permission gate per widget id (hide when user lacks code). */
export const WIDGET_PERMISSION_GATES: Partial<Record<string, string>> = {
  "activity-audit": "audit.read",
  "inv-low-stock": "inventory.read",
  "inv-out-of-stock": "inventory.read",
  "inv-overstock": "inventory.read",
  "inv-fast-movers": "inventory.read",
  "inv-slow-movers": "inventory.read",
  "inv-turnover": "inventory.read",
  "inv-value": "inventory.read",
};

/** Module code used to honor widgetsEnabled kill-switch per widget. */
export const WIDGET_MODULE_GATES: Partial<Record<string, string>> = {
  "kpi-revenue": "sales",
  "chart-sales-trend": "sales",
  "health-top-customers": "sales",
  "health-overdue-invoices": "sales",
  "activity-invoices": "sales",
  "kpi-ap": "purchases",
  "health-ap-aging": "purchases",
  "health-overdue-payments": "purchases",
  "health-top-suppliers": "purchases",
  "activity-payments": "purchases",
  "kpi-cash": "bank",
  "kpi-bank": "bank",
  "chart-cashflow": "bank",
  "inv-value": "inventory",
  "inv-low-stock": "inventory",
  "inv-out-of-stock": "inventory",
  "inv-overstock": "inventory",
  "inv-fast-movers": "inventory",
  "inv-slow-movers": "inventory",
  "inv-turnover": "inventory",
  "activity-stock-adj": "inventory",
  "pnl-snapshot": "financial",
  "chart-expense-breakdown": "financial",
  "chart-revenue-breakdown": "financial",
  "chart-margin-analysis": "financial",
  "kpi-gross-profit": "financial",
  "kpi-net-profit": "financial",
  "kpi-ar": "financial",
  "health-ar-aging": "financial",
};

export function filterWidgetsByPermission(
  widgetIds: string[],
  can: (code: string) => boolean,
): string[] {
  return widgetIds.filter((id) => {
    const gate = WIDGET_PERMISSION_GATES[id];
    return !gate || can(gate);
  });
}

export function filterWidgetsByModuleAccess(
  widgetIds: string[],
  modules: { moduleCode: string; canAccess?: boolean; widgetsEnabled?: boolean }[],
): string[] {
  const access = new Map(
    modules.map((m) => [
      m.moduleCode,
      Boolean(m.canAccess && (m.widgetsEnabled ?? true)),
    ]),
  );
  return widgetIds.filter((id) => {
    const code = WIDGET_MODULE_GATES[id];
    if (!code) return true;
    return access.get(code) ?? true;
  });
}
