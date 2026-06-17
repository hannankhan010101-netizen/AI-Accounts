"use client";

import { ApplicationSettingsForm } from "@/components/settings/application-settings-form";
import { appSettingsApi } from "@/lib/api/tenant";

export default function MissedRecurrencePage() {
  return (
    <ApplicationSettingsForm
      title="Missed recurrence"
      breadcrumb="Settings / Missed recurrence"
      description="How recurring documents behave when a scheduled run is missed (catalog §3.3)."
      queryKey="missed-recurrence-settings"
      load={() => appSettingsApi.getMissedRecurrenceSettings()}
      save={(body) => appSettingsApi.putMissedRecurrenceSettings(body)}
      fields={[
        { key: "notifyAdmin", label: "Notify administrator", kind: "checkbox" },
        { key: "autoSkip", label: "Auto-skip missed runs", kind: "checkbox" },
        { key: "lookbackDays", label: "Lookback days", kind: "number" },
      ]}
    />
  );
}
