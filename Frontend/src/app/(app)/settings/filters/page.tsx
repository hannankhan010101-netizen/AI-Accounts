"use client";

import { ApplicationSettingsForm } from "@/components/settings/application-settings-form";
import { appSettingsApi } from "@/lib/api/tenant";

export default function FiltersManagementPage() {
  return (
    <ApplicationSettingsForm
      title="Filters management"
      breadcrumb="Settings / Filters management"
      description="Default date ranges and whether user filter choices persist across sessions."
      queryKey="filters-settings"
      load={() => appSettingsApi.getFiltersSettings()}
      save={(body) => appSettingsApi.putFiltersSettings(body)}
      fields={[
        {
          key: "defaultDateRange",
          label: "Default date range",
          kind: "select",
          options: [
            { value: "thisMonth", label: "This month" },
            { value: "lastMonth", label: "Last month" },
            { value: "thisYear", label: "This year" },
          ],
        },
        { key: "persistUserFilters", label: "Persist user filter choices", kind: "checkbox" },
      ]}
    />
  );
}
