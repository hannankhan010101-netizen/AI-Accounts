import { describe, expect, it } from "vitest";

import {
  DEFAULT_COMMAND_CENTER_WIDGETS,
  migrateDashboardWidgets,
  ROLE_WIDGET_GROUPS,
} from "@/lib/dashboard/widget-catalog";

describe("migrateDashboardWidgets", () => {
  it("returns defaults for empty input", () => {
    const result = migrateDashboardWidgets([]);
    expect(result.size).toBe(DEFAULT_COMMAND_CENTER_WIDGETS.length);
  });

  it("passes through v2 widget ids", () => {
    const result = migrateDashboardWidgets(["kpi-cash", "chart-cashflow"]);
    expect(result.has("kpi-cash")).toBe(true);
    expect(result.has("chart-cashflow")).toBe(true);
  });

  it("maps legacy ar-summary to kpi and aging widgets", () => {
    const result = migrateDashboardWidgets(["ar-summary"]);
    expect(result.has("kpi-ar")).toBe(true);
    expect(result.has("health-ar-aging")).toBe(true);
  });

  it("maps recent-activity to multiple legacy widgets", () => {
    const result = migrateDashboardWidgets(["recent-activity"]);
    expect(result.has("chart-cashflow")).toBe(true);
    expect(result.size).toBeGreaterThan(3);
  });
});

describe("ROLE_WIDGET_GROUPS", () => {
  it("manager hides health, profitability, and activity rows", () => {
    const manager = ROLE_WIDGET_GROUPS.manager;
    expect(manager.has("health-ar-aging")).toBe(false);
    expect(manager.has("pnl-snapshot")).toBe(false);
    expect(manager.has("activity-invoices")).toBe(false);
    expect(manager.has("kpi-cash")).toBe(true);
    expect(manager.has("chart-cashflow")).toBe(true);
  });

  it("accountant limits inventory widgets", () => {
    const accountant = ROLE_WIDGET_GROUPS.accountant;
    expect(accountant.has("inv-value")).toBe(true);
    expect(accountant.has("inv-low-stock")).toBe(false);
    expect(accountant.has("health-ar-aging")).toBe(true);
  });
});

describe("insight severity mapping", () => {
  const map: Record<string, string> = {
    good: "text-status-success",
    warn: "text-status-warning",
    critical: "text-status-danger",
    info: "text-fg-muted",
  };

  it("maps all severities", () => {
    for (const key of ["good", "warn", "critical", "info"]) {
      expect(map[key]).toBeTruthy();
    }
  });
});

describe("KPI status logic", () => {
  function toneForKpi(id: string, changePct: number | null): "positive" | "negative" | "neutral" {
    if (changePct === null) return "neutral";
    const invert = id === "kpi-ar" || id === "kpi-ap";
    const up = invert ? changePct <= 0 : changePct >= 0;
    return up ? "positive" : "negative";
  }

  it("treats revenue increase as positive", () => {
    expect(toneForKpi("kpi-revenue", 10)).toBe("positive");
  });

  it("treats AR increase as negative", () => {
    expect(toneForKpi("kpi-ar", 5)).toBe("negative");
  });
});
