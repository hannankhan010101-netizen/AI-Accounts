/**

 * Admin hub — simplified entry to catalog §12 settings (KISS IA).

 */

import { BookOpen, Plug, Printer, ScrollText, SlidersHorizontal, Users } from "lucide-react";



import { AdminHubClient, type AdminHubSection } from "@/components/admin/admin-hub-client";

import { PageHeader } from "@/components/ui/page-header";



const sections: AdminHubSection[] = [

  {

    title: "People and access",

    description: "Users, roles, invites, and audit trail.",

    icon: Users,

    links: [

      { label: "Users", href: "/settings/users" },

      { label: "Roles", href: "/settings/roles" },

      { label: "Access control", href: "/settings/access-control" },

      { label: "Data scope", href: "/settings/advance-users" },

      { label: "User log", href: "/settings/user-log" },

      { label: "Invite templates", href: "/settings/invite-templates" },

    ],

  },

  {

    title: "Accounting setup",

    description: "Ledger, tax, and period controls.",

    icon: BookOpen,

    links: [

      { label: "Journals", href: "/settings/journals" },

      { label: "Chart of accounts", href: "/settings/coa" },

      { label: "Tax and year end", href: "/settings/taxes-year-end" },

      { label: "Lock date", href: "/settings/lock-date" },

      { label: "Business information", href: "/settings/business-information" },

    ],

  },

  {

    title: "Lists and preferences",

    description: "Filters, columns, and smart defaults.",

    icon: SlidersHorizontal,

    links: [

      { label: "Smart settings", href: "/settings/smart" },

      { label: "Filters", href: "/settings/filters" },

      { label: "Columns", href: "/settings/columns" },

      { label: "Content settings", href: "/settings/content" },

      { label: "Custom fields", href: "/settings/custom-fields" },

    ],

  },

  {

    title: "Integrations",

    description: "Payments, compliance, and modules.",

    icon: Plug,

    links: [

      { label: "Online payments", href: "/settings/online-payments" },

      { label: "FBR errors", href: "/settings/fbr-errors" },

      { label: "Module access", href: "/settings/module-access" },

      { label: "Module subscriptions", href: "/settings/module-subscriptions" },

      { label: "Report catalog", href: "/settings/reports-catalog" },

      { label: "Import jobs", href: "/settings/import-jobs" },

      { label: "Data migration", href: "/settings/migrations" },

    ],

  },

  {

    title: "Printing templates",

    description: "Document layouts by type.",

    icon: Printer,

    links: [

      { label: "Sales invoice (SI)", href: "/settings/printing/si" },

      { label: "Supplier bill (VI)", href: "/settings/printing/vi" },

      { label: "All printing settings", href: "/settings/printing/si" },

    ],

  },

  {

    title: "Compliance and logs",

    description: "Email, recurrence, and operational logs.",

    icon: ScrollText,

    links: [

      { label: "Email settings", href: "/settings/email" },

      { label: "Sent emails", href: "/settings/sent-emails" },

      { label: "Missed recurrence", href: "/settings/missed-recurrence" },

    ],

  },

];



export default function AdminHubPage() {

  return (

    <div>

      <PageHeader

        title="Admin"

        breadcrumb="Home / Admin"

        description="Company setup and configuration. Day-to-day accounting lives under Accounting in the sidebar."

      />



      <AdminHubClient sections={sections} />



      <p className="mt-6 text-caption text-fg-muted">

        Need a setting not listed here? Use{" "}

        <span className="font-medium">Settings</span> in the top bar for the full catalog menu, or{" "}

        <kbd className="rounded border border-border px-1">Ctrl K</kbd> to jump anywhere.

      </p>

    </div>

  );

}

