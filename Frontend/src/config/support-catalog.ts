/** Support hub articles — catalog §2.2 / §2.3. */

export interface SupportArticle {
  id: string;
  title: string;
  category: string;
  summary: string;
  href: string;
  external?: boolean;
}

export const SUPPORT_CATEGORIES = [
  "All",
  "Bank",
  "Sales",
  "Purchases",
  "Inventory",
  "Reports",
  "Settings",
  "Others",
] as const;

export const SUPPORT_ARTICLES: SupportArticle[] = [
  {
    id: "keyboard-shortcuts",
    title: "Keyboard shortcuts",
    category: "Others",
    summary: "Press ? in the app or Ctrl+K to open search.",
    href: "#shortcuts",
  },
  {
    id: "command-palette",
    title: "Jump to any screen",
    category: "Others",
    summary: "Use Ctrl+K to search invoices, reports, and settings.",
    href: "/dashboard",
  },
  {
    id: "sales-all",
    title: "All sales activity",
    category: "Sales",
    summary: "Unified list of invoices, receipts, and credits.",
    href: "/sales/all",
  },
  {
    id: "purchases-all",
    title: "All purchase activity",
    category: "Purchases",
    summary: "Unified list of bills, payments, and credits.",
    href: "/purchases/all",
  },
  {
    id: "bank-import",
    title: "Import bank statement",
    category: "Bank",
    summary: "Upload CSV or Excel to reconcile accounts.",
    href: "/bank/import-statement",
  },
  {
    id: "reports-catalog",
    title: "Report catalog",
    category: "Reports",
    summary: "Browse every FastAccounts report definition.",
    href: "/reports/catalog",
  },
  {
    id: "analytical",
    title: "Analytical reports",
    category: "Reports",
    summary: "Data extracts and analysis hub.",
    href: "/reports/analytical",
  },
  {
    id: "user-log",
    title: "User activity log",
    category: "Settings",
    summary: "Audit trail of changes in this company.",
    href: "/settings/user-log",
  },
  {
    id: "business-info",
    title: "Business information",
    category: "Settings",
    summary: "Company name, address, and print logo.",
    href: "/settings/business-information",
  },
  {
    id: "fa-support",
    title: "FastAccounts support site",
    category: "Others",
    summary: "Official help articles and tutorials.",
    href: "https://fastaccounts.io/support/",
    external: true,
  },
];
