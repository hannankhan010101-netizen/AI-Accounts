import type { AuditLogFilters } from "@/lib/api/tenant";

export type AuditLogPreset = {
  id: string;
  label: string;
  draft: AuditLogFilters & { type?: string };
};

function isoDate(d: Date): string {
  return d.toISOString().slice(0, 10);
}

function daysAgo(n: number): string {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return isoDate(d);
}

export const AUDIT_LOG_PRESETS: AuditLogPreset[] = [
  {
    id: "last7",
    label: "Last 7 days",
    draft: { dateFrom: daysAgo(7), dateTo: isoDate(new Date()) },
  },
  {
    id: "rbac30",
    label: "RBAC (30 days)",
    draft: {
      type: "rbac",
      rbacOnly: true,
      dateFrom: daysAgo(30),
      dateTo: isoDate(new Date()),
    },
  },
  {
    id: "bank30",
    label: "Bank (30 days)",
    draft: {
      type: "bank",
      typeContains: "BANK",
      dateFrom: daysAgo(30),
      dateTo: isoDate(new Date()),
    },
  },
  {
    id: "bankRecon30",
    label: "Reconciliations (30 days)",
    draft: {
      transactionType: "BANK_RECONCILIATION",
      dateFrom: daysAgo(30),
      dateTo: isoDate(new Date()),
    },
  },
  {
    id: "signin30",
    label: "Sign-in (30 days)",
    draft: {
      type: "login",
      transactionType: "LOGIN",
      dateFrom: daysAgo(30),
      dateTo: isoDate(new Date()),
    },
  },
];
