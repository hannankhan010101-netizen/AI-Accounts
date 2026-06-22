import { toursForPath } from "@/lib/tour/route-tours";

export type ScreenContext = {
  module: string;
  title: string;
  description: string;
  tourIds: string[];
  quickActions: { label: string; prompt: string }[];
};

const REGISTRY: { prefix: string; ctx: Omit<ScreenContext, "tourIds"> }[] = [
  {
    prefix: "/sales/invoices",
    ctx: {
      module: "sales",
      title: "Sales invoices",
      description: "Create, edit, and post customer invoices.",
      quickActions: [
        { label: "New invoice", prompt: "How do I create a new sales invoice?" },
        { label: "Find invoice", prompt: "Help me find a recent invoice" },
        { label: "All sales activity", prompt: "Show me all sales invoices, receipts, and credits" },
      ],
    },
  },
  {
    prefix: "/sales/all",
    ctx: {
      module: "sales",
      title: "All sales activity",
      description: "Unified list of invoices, receipts, and credits (FastAccounts Sales All).",
      quickActions: [
        { label: "Filter by type", prompt: "How do I find a specific receipt in sales activity?" },
      ],
    },
  },
  {
    prefix: "/purchases/all",
    ctx: {
      module: "purchases",
      title: "All purchase activity",
      description: "Unified list of bills, payments, and credits (FastAccounts Purchases All).",
      quickActions: [
        { label: "Find payment", prompt: "How do I locate a supplier payment?" },
      ],
    },
  },
  {
    prefix: "/bank/import-statement",
    ctx: {
      module: "bank",
      title: "Import bank statement",
      description: "Upload CSV or Excel to open a reconciliation with statement lines.",
      quickActions: [
        { label: "Import format", prompt: "What columns should my bank statement file have?" },
      ],
    },
  },
  {
    prefix: "/bank/reconciliation",
    ctx: {
      module: "bank",
      title: "Bank reconciliation",
      description: "Match bank transactions to ledger entries.",
      quickActions: [
        { label: "Reconcile", prompt: "How do I reconcile my bank account?" },
        { label: "Import statement", prompt: "How do I import a bank statement CSV?" },
      ],
    },
  },
  {
    prefix: "/inventory/add",
    ctx: {
      module: "inventory",
      title: "Add product",
      description: "Create a product with pricing, opening stock, and optional image.",
      quickActions: [
        { label: "Required fields", prompt: "What fields are required when adding a product?" },
        { label: "Opening stock", prompt: "How do I set opening stock on a new product?" },
      ],
    },
  },
  {
    prefix: "/inventory",
    ctx: {
      module: "inventory",
      title: "Inventory",
      description: "Products, stock levels, and adjustments.",
      quickActions: [
        { label: "Stock check", prompt: "How do I check product stock levels?" },
      ],
    },
  },
  {
    prefix: "/reports/analytical",
    ctx: {
      module: "reports",
      title: "Analytical reports",
      description: "Data extracts and analysis hub (FastAccounts Analytical Reports).",
      quickActions: [
        { label: "Bank data extract", prompt: "Which analytical report shows bank payments?" },
      ],
    },
  },
  {
    prefix: "/reports",
    ctx: {
      module: "reports",
      title: "Reports",
      description: "Financial statements and operational reports.",
      quickActions: [
        { label: "P&L", prompt: "Explain the profit and loss report" },
        { label: "Analytical reports", prompt: "What are analytical reports?" },
      ],
    },
  },
  {
    prefix: "/settings",
    ctx: {
      module: "settings",
      title: "Settings",
      description: "Users, roles, company configuration, and audit log.",
      quickActions: [
        { label: "Audit log", prompt: "What does the audit log show?" },
      ],
    },
  },
  {
    prefix: "/dashboard",
    ctx: {
      module: "core",
      title: "Dashboard",
      description: "Overview of your workspace and key actions.",
      quickActions: [
        { label: "Get started", prompt: "What should I do first in Fast Accounts?" },
      ],
    },
  },
];

export function resolveScreenContext(pathname: string): ScreenContext {
  for (const { prefix, ctx } of REGISTRY) {
    if (pathname === prefix || pathname.startsWith(`${prefix}/`)) {
      return { ...ctx, tourIds: toursForPath(pathname) };
    }
  }
  return {
    module: "erp",
    title: "Fast Accounts",
    description: "Accounting ERP for sales, purchases, bank, inventory, and reports.",
    tourIds: toursForPath(pathname),
    quickActions: [
      { label: "Help", prompt: "What can you help me with on this screen?" },
    ],
  };
}

export const ALLOWED_ROUTE_PREFIXES = [
  "/dashboard",
  "/sales",
  "/purchases",
  "/bank",
  "/inventory",
  "/reports",
  "/settings",
  "/admin",
  "/onboarding",
];

export function isAllowedRoute(route: string): boolean {
  if (!route.startsWith("/")) return false;
  return ALLOWED_ROUTE_PREFIXES.some(
    (p) => route === p || route.startsWith(`${p}/`),
  );
}
