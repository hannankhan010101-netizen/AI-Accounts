/**
 * Settings mega-menu structure — catalog §12.1.
 * Routes are placeholders; each Phase 1 milestone replaces them with real pages.
 */

export interface SettingsLink {
  label: string;
  href: string;
}

export interface SettingsColumn {
  title: string;
  groups: { label: string; links: SettingsLink[] }[];
}

export const settingsColumns: SettingsColumn[] = [
  {
    title: "Ledger & access",
    groups: [
      { label: "Journals", links: [{ label: "Journals", href: "/settings/journals" }] },
      {
        label: "Chart of account",
        links: [{ label: "Chart of Account", href: "/settings/coa" }],
      },
      { label: "Nominals", links: [{ label: "Nominals", href: "/settings/nominals" }] },
      {
        label: "Section Management",
        links: [{ label: "Section Management", href: "/settings/sections" }],
      },
      {
        label: "User & Roles",
        links: [
          { label: "Users Management", href: "/settings/users" },
          { label: "Access control", href: "/settings/access-control" },
          { label: "Roles Management", href: "/settings/roles" },
          { label: "Authorisation", href: "/settings/authorisation" },
          { label: "Data scope", href: "/settings/advance-users" },
          { label: "Invite email templates", href: "/settings/invite-templates" },
          { label: "Dashboard Management", href: "/settings/dashboards" },
          { label: "Learning", href: "/settings/learning" },
          { label: "Learning insights", href: "/settings/learning-insights" },
          { label: "What's New (tenant)", href: "/settings/onboarding-releases" },
          { label: "What's New (platform)", href: "/settings/platform-releases" },
        ],
      },
      { label: "Lock Date", links: [{ label: "Lock Date", href: "/settings/lock-date" }] },
      { label: "OP Methods", links: [{ label: "OP Methods", href: "/settings/op-methods" }] },
      {
        label: "Log Management",
        links: [{ label: "User Log", href: "/settings/user-log" }],
      },
    ],
  },
  {
    title: "General application",
    groups: [
      {
        label: "Settings",
        links: [
          { label: "Smart Settings", href: "/settings/smart" },
          { label: "Taxes and Year End", href: "/settings/taxes-year-end" },
          { label: "Business Information", href: "/settings/business-information" },
          { label: "Locations", href: "/settings/locations" },
          { label: "Projects", href: "/settings/projects" },
          { label: "Budgets", href: "/settings/budget" },
          { label: "Filters Management", href: "/settings/filters" },
          { label: "Column Management", href: "/settings/columns" },
          { label: "Content Settings", href: "/settings/content" },
        ],
      },
      {
        label: "Integrations",
        links: [
          { label: "Integration status", href: "/settings/integrations" },
          { label: "Online payments", href: "/settings/online-payments" },
          { label: "FBR errors", href: "/settings/fbr-errors" },
          { label: "Report catalog", href: "/settings/reports-catalog" },
          { label: "Module subscriptions", href: "/settings/module-subscriptions" },
          { label: "Module access", href: "/settings/module-access" },
          { label: "Custom fields", href: "/settings/custom-fields" },
        ],
      },
      {
        label: "Recurrence",
        links: [
          { label: "Recurring schedules", href: "/settings/recurring-schedules" },
          { label: "Missed Recurrence", href: "/settings/missed-recurrence" },
        ],
      },
      {
        label: "Email & SMS",
        links: [
          { label: "Email Settings", href: "/settings/email" },
          { label: "Sent Emails", href: "/settings/sent-emails" },
        ],
      },
    ],
  },
  {
    title: "Printing",
    groups: [
      {
        label: "Sales Printing",
        links: [
          { label: "SI — Sales Invoice", href: "/settings/printing/si" },
          { label: "SC — Sales Credit", href: "/settings/printing/sc" },
          { label: "SO — Sales Order", href: "/settings/printing/so" },
          { label: "SR — Sales Receipt", href: "/settings/printing/sr" },
          { label: "PDCR", href: "/settings/printing/pdcr" },
          { label: "GDNSI", href: "/settings/printing/gdnsi" },
          { label: "GDNSO", href: "/settings/printing/gdnso" },
          { label: "CUS — Customer", href: "/settings/printing/cus" },
        ],
      },
      {
        label: "Purchases Printing",
        links: [
          { label: "VI — Supplier Bill", href: "/settings/printing/vi" },
          { label: "VC — Supplier Credit", href: "/settings/printing/vc" },
          { label: "PO — Purchase Order", href: "/settings/printing/po" },
          { label: "VP — Bill Payment", href: "/settings/printing/vp" },
          { label: "PDCI", href: "/settings/printing/pdci" },
          { label: "GRNPO", href: "/settings/printing/grnpo" },
          { label: "GRNVI", href: "/settings/printing/grnvi" },
        ],
      },
      {
        label: "Journal / Bank / Other / Project Printing",
        links: [
          { label: "Journal", href: "/settings/printing/journal" },
          { label: "Bank", href: "/settings/printing/bank" },
          { label: "Assembly", href: "/settings/printing/assembly" },
          { label: "Stock Adjustment", href: "/settings/printing/stock-adjustment" },
          { label: "Stock Transfer", href: "/settings/printing/stock-transfer" },
          { label: "User Log", href: "/settings/printing/user-log" },
          { label: "Project", href: "/settings/printing/project" },
        ],
      },
    ],
  },
];
