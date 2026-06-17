/**
 * Universal command palette registry — navigation, create actions, settings.
 * Routes stay catalog-aligned; labels use plain language (KISS IA).
 */

export type CommandKind = "navigate" | "create" | "settings" | "tour" | "ai";

/** Prefix for tour actions handled in CommandPalette (not router paths). */
export const TOUR_COMMAND_PREFIX = "tour://";

/** Prefix for AI copilot actions. */
export const AI_COMMAND_PREFIX = "ai://";

export interface CommandItem {
  id: string;
  label: string;
  description?: string;
  href: string;
  kind: CommandKind;
  keywords?: string[];
}

export const commandItems: CommandItem[] = [
  { id: "home", label: "Home", href: "/dashboard", kind: "navigate", keywords: ["dashboard"] },

  { id: "si-list", label: "Sales invoices", href: "/sales/invoices", kind: "navigate" },
  { id: "si-new", label: "New sales invoice", href: "/sales/invoices/new", kind: "create", keywords: ["invoice", "sell"] },
  { id: "customers", label: "Customers", href: "/sales/customers", kind: "navigate" },
  { id: "quotations", label: "Quotations", href: "/sales/quotations", kind: "navigate" },
  { id: "sales-orders", label: "Sales orders", href: "/sales/orders", kind: "navigate" },
  { id: "receipts", label: "Sales receipts", href: "/sales/receipts", kind: "navigate" },
  { id: "sales-all", label: "All sales activity", href: "/sales/all", kind: "navigate", keywords: ["sales all", "invoices", "receipts", "credits"] },
  { id: "sr-new", label: "New sales receipt", href: "/sales/receipts/new", kind: "create" },

  { id: "bills", label: "Supplier bills", href: "/purchases/bills", kind: "navigate", keywords: ["purchase", "ap"] },
  { id: "bill-new", label: "New supplier bill", href: "/purchases/bills/new", kind: "create" },
  { id: "suppliers", label: "Suppliers", href: "/purchases/suppliers", kind: "navigate" },
  { id: "po", label: "Purchase orders", href: "/purchases/orders", kind: "navigate" },
  { id: "payments", label: "Bill payments", href: "/purchases/payments", kind: "navigate" },
  { id: "purchases-all", label: "All purchase activity", href: "/purchases/all", kind: "navigate", keywords: ["purchases all", "bills", "payments", "credits"] },

  { id: "bank-balances", label: "Bank balances", href: "/bank/balances", kind: "navigate", keywords: ["money", "cash"] },
  { id: "bank-payments", label: "Bank payments", href: "/bank/payments", kind: "navigate" },
  { id: "bank-receipts", label: "Bank receipts", href: "/bank/receipts", kind: "navigate" },
  { id: "bank-transfers", label: "Bank transfers", href: "/bank/transfers", kind: "navigate" },
  { id: "reconciliation", label: "Bank reconciliation", href: "/bank/reconciliation", kind: "navigate" },
  { id: "import-statement", label: "Import bank statement", href: "/bank/import-statement", kind: "navigate", keywords: ["csv", "excel", "statement"] },
  { id: "fx-revaluation", label: "FX revaluation", href: "/bank/fx-revaluation", kind: "navigate", keywords: ["forex", "currency", "revaluation"] },
  { id: "assembly-templates", label: "Assembly templates", href: "/inventory/assembly/templates", kind: "navigate" },
  { id: "assembly-jobs", label: "Assembly jobs", href: "/inventory/assembly/jobs", kind: "navigate" },
  { id: "projects-settings", label: "Projects", href: "/settings/projects", kind: "settings" },
  { id: "locations-settings", label: "Locations", href: "/settings/locations", kind: "settings" },
  { id: "bp-new", label: "New bank payment", href: "/bank/payments/new", kind: "create" },

  { id: "products", label: "Products", href: "/inventory/products", kind: "navigate", keywords: ["stock", "inventory"] },
  { id: "stock-adj", label: "Stock adjustment", href: "/inventory/stock-adjustment", kind: "navigate" },

  { id: "my-tasks", label: "My tasks", href: "/my-tasks", kind: "navigate", keywords: ["draft", "todo"] },
  { id: "support", label: "Support", href: "/support", kind: "navigate", keywords: ["help"] },
  { id: "profile", label: "Profile", href: "/profile", kind: "navigate" },
  { id: "analytical-reports", label: "Analytical reports", href: "/reports/analytical", kind: "navigate", keywords: ["data extract", "analysis"] },
  { id: "reports-catalog", label: "Report catalog", href: "/reports/catalog", kind: "navigate", keywords: ["full catalog", "all reports"] },
  { id: "trial-balance", label: "Trial balance", href: "/reports/trial-balance", kind: "navigate" },
  { id: "general-ledger", label: "General ledger", href: "/reports/general-ledger", kind: "navigate" },
  { id: "pl", label: "Profit and loss", href: "/reports/profit-and-loss", kind: "navigate" },
  { id: "ar-aging", label: "AR aging", href: "/reports/ar-aging", kind: "navigate" },

  { id: "journals", label: "Journals", href: "/settings/journals", kind: "navigate", keywords: ["accounting", "gl"] },
  { id: "coa", label: "Chart of accounts", href: "/settings/coa", kind: "navigate" },
  { id: "journal-new", label: "New journal", href: "/settings/journals/new", kind: "create" },

  { id: "admin", label: "Admin and settings", href: "/admin", kind: "settings", keywords: ["users", "roles", "setup"] },
  { id: "users", label: "Users", href: "/settings/users", kind: "settings" },
  { id: "roles", label: "Roles", href: "/settings/roles", kind: "settings" },
  { id: "business", label: "Business information", href: "/settings/business-information", kind: "settings" },

  {
    id: "tour-welcome",
    label: "Start welcome tour",
    description: "3-minute workspace orientation",
    href: `${TOUR_COMMAND_PREFIX}onboard.core`,
    kind: "tour",
    keywords: ["help", "onboarding", "guide", "learn"],
  },
  {
    id: "tour-assistant",
    label: "Learning assistant",
    description: "Ask what to do next on this page",
    href: `${TOUR_COMMAND_PREFIX}assistant`,
    kind: "tour",
    keywords: ["help", "ai", "suggestions"],
  },
  {
    id: "ai-open",
    label: "Open AI-Assistant",
    description: "Context-aware ERP assistant",
    href: `${AI_COMMAND_PREFIX}open`,
    kind: "ai",
    keywords: ["help", "assistant", "chat", "groq"],
  },
  {
    id: "ai-invoice",
    label: "AI: invoice help",
    description: "Ask about sales invoices",
    href: `${AI_COMMAND_PREFIX}invoice`,
    kind: "ai",
    keywords: ["sales", "invoice", "si"],
  },
  {
    id: "ai-reconcile",
    label: "AI: reconciliation help",
    description: "Bank reconciliation guidance",
    href: `${AI_COMMAND_PREFIX}reconcile`,
    kind: "ai",
    keywords: ["bank", "recon", "match"],
  },
  {
    id: "ai-search",
    label: "AI search",
    description: "Search with natural language",
    href: `${AI_COMMAND_PREFIX}search`,
    kind: "ai",
    keywords: ["find", "lookup", "query"],
  },
  {
    id: "tour-insights",
    label: "Learning insights",
    href: "/settings/learning-insights",
    kind: "settings",
    keywords: ["onboarding", "analytics", "tours"],
  },
  {
    id: "tour-learning",
    label: "Learning preferences",
    description: "Tour progress, digest email, replay tours",
    href: "/settings/learning",
    kind: "settings",
    keywords: ["onboarding", "tours", "help", "digest"],
  },
  {
    id: "tour-workflow-invoice",
    label: "Workflow: create sales invoice",
    description: "Start from invoice list through save",
    href: `${TOUR_COMMAND_PREFIX}workflow.sales-invoice`,
    kind: "tour",
    keywords: ["invoice", "workflow", "sell", "create"],
  },
  {
    id: "tour-workflow-bill",
    label: "Workflow: create supplier bill",
    href: `${TOUR_COMMAND_PREFIX}workflow.supplier-bill`,
    kind: "tour",
    keywords: ["bill", "purchase", "workflow", "supplier"],
  },
  {
    id: "tour-workflow-supplier-payment",
    label: "Workflow: supplier bill payment",
    description: "Pay AP and allocate to open bills",
    href: `${TOUR_COMMAND_PREFIX}workflow.supplier-payment`,
    kind: "tour",
    keywords: ["payment", "purchase", "ap", "supplier", "workflow", "bill"],
  },
  {
    id: "tour-workflow-journal",
    label: "Workflow: post manual journal",
    href: `${TOUR_COMMAND_PREFIX}workflow.journal`,
    kind: "tour",
    keywords: ["journal", "gl", "workflow", "accounting"],
  },
  {
    id: "tour-workflow-sales-receipt",
    label: "Workflow: customer receipt",
    description: "Record AR receipt and allocate to invoices",
    href: `${TOUR_COMMAND_PREFIX}workflow.sales-receipt`,
    kind: "tour",
    keywords: ["receipt", "sales", "ar", "customer", "workflow"],
  },
  {
    id: "tour-workflow-receipt",
    label: "Workflow: bank receipt",
    href: `${TOUR_COMMAND_PREFIX}workflow.bank-receipt`,
    kind: "tour",
    keywords: ["receipt", "bank", "workflow", "money"],
  },
  {
    id: "tour-workflow-payment",
    label: "Workflow: bank payment",
    href: `${TOUR_COMMAND_PREFIX}workflow.bank-payment`,
    kind: "tour",
    keywords: ["payment", "bank", "workflow", "money"],
  },
];

export function filterCommands(query: string, items: CommandItem[] = commandItems): CommandItem[] {
  const q = query.trim().toLowerCase();
  if (!q) return items;
  return items.filter((item) => {
    const hay = [item.label, item.description, item.href, ...(item.keywords ?? [])]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();
    return hay.includes(q) || q.split(/\s+/).every((word) => hay.includes(word));
  });
}
