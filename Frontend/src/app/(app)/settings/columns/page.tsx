"use client";

import Link from "next/link";

import { ApplicationSettingsForm } from "@/components/settings/application-settings-form";
import { appSettingsApi } from "@/lib/api/tenant";

export default function ColumnManagementPage() {
  return (
    <div>
      <ApplicationSettingsForm
        title="Column management"
        breadcrumb="Settings / Column management"
        description="Organization-wide list column policy. Per-grid layouts are edited in Content Settings."
        queryKey="columns-settings"
        load={() => appSettingsApi.getColumnsSettings()}
        save={(body) => appSettingsApi.putColumnsSettings(body)}
        fields={[
          {
            key: "syncWithContentSettings",
            label: "Apply Content Settings layouts on list screens",
            kind: "checkbox",
          },
          { key: "allowUserOverrides", label: "Allow per-user column overrides", kind: "checkbox" },
        ]}
      />
      <p className="mt-4 text-sm text-fg-muted">
        Edit column order and visibility per listing in{" "}
        <Link href="/settings/content" className="text-brand hover:underline">
          Content settings
        </Link>
        .
      </p>
    </div>
  );
}
