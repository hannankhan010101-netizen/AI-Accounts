/** Admin hub — simplified entry to catalog §12 settings (KISS IA). */

import { AdminHubClient } from "@/components/admin/admin-hub-client";
import { PageHeader } from "@/components/ui/page-header";

export default function AdminHubPage() {
  return (
    <div>
      <PageHeader
        title="Admin"
        breadcrumb="Home / Admin"
        description="Company setup and configuration. Day-to-day accounting lives under Accounting in the sidebar."
      />

      <AdminHubClient />

      <p className="mt-6 text-caption text-fg-muted">
        Need a setting not listed here? Use{" "}
        <span className="font-medium">Settings</span> in the top bar for the full catalog menu, or{" "}
        <kbd className="rounded border border-border px-1">Ctrl K</kbd> to jump anywhere.
      </p>
    </div>
  );
}
