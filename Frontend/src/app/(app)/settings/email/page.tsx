"use client";

import { ApplicationSettingsForm } from "@/components/settings/application-settings-form";
import { appSettingsApi } from "@/lib/api/tenant";

export default function EmailSettingsPage() {
  return (
    <ApplicationSettingsForm
      title="Email settings"
      breadcrumb="Settings / Email settings"
      description="SMTP and outbound document email toggles (catalog §3.6)."
      queryKey="email-settings"
      load={() => appSettingsApi.getEmailSettings()}
      save={(body) => appSettingsApi.putEmailSettings(body)}
      fields={[
        { key: "smtpHost", label: "SMTP host", kind: "text" },
        { key: "smtpPort", label: "SMTP port", kind: "number" },
        { key: "fromAddress", label: "From address", kind: "text" },
        { key: "useTls", label: "Use TLS", kind: "checkbox" },
        { key: "sendInvoiceEmail", label: "Enable invoice email from sales screens", kind: "checkbox" },
        {
          key: "sendBalanceReminder",
          label: "Enable customer balance reminder emails",
          kind: "checkbox",
        },
      ]}
    />
  );
}
