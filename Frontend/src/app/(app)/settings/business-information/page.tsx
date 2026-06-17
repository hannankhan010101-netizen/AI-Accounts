"use client";
import { useTenantReferenceQuery, invalidateTenantQueries } from "@/lib/api/tenant-query";

import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";

import { DraftRecoveryBanner } from "@/components/ui/draft-recovery-banner";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { WorkspaceLoading } from "@/components/ui/workspace-loading";
import { useCompany } from "@/lib/auth/company-context";
import { useFormDraft } from "@/lib/hooks/use-form-draft";
import { referenceQueryOptions } from "@/lib/query/options";
import { settingsApi, type BusinessInformation } from "@/lib/api/tenant";

const ADDRESS_LINE_FIELDS = [
  "addressLine1",
  "addressLine2",
  "addressLine3",
  "addressLine4",
  "addressLine5",
] as const;

export default function BusinessInformationPage() {
  const qc = useQueryClient();
  const { companyId } = useCompany();
  const [savedAt, setSavedAt] = useState<Date | null>(null);

  const { data, isLoading } = useTenantReferenceQuery(["business-information"], () => settingsApi.getBusinessInformation());

  const form = useForm<BusinessInformation>({
    defaultValues: { applyOnAllPrints: false },
  });

  const serverValues = data?.result ?? undefined;
  const { hasRecoverableDraft, restoreDraft, discardDraft, clearDraftOnSave } = useFormDraft({
    scope: "business-information",
    companyId,
    form,
    serverValues,
    enabled: Boolean(companyId && serverValues),
  });

  useEffect(() => {
    if (serverValues) form.reset(serverValues);
  }, [serverValues, form]);

  const mutation = useMutation({
    mutationFn: (values: BusinessInformation) => settingsApi.putBusinessInformation(values),
    onSuccess: () => {
      setSavedAt(new Date());
      clearDraftOnSave();
      invalidateTenantQueries(qc, "business-information");
    },
  });

  const onSubmit = form.handleSubmit((values) => mutation.mutate(values));

  return (
    <div>
      <PageHeader
        title="Business Information"
        breadcrumb="Home / Business information"
        description="Company identity, contact, and registration IDs used on prints (§12.13)."
        actions={
          <>
            <Button type="button" variant="outline" onClick={() => form.reset(serverValues ?? {})}>
              Cancel
            </Button>
            <Button type="submit" form="bi-form" disabled={mutation.isPending}>
              {mutation.isPending ? "Saving…" : "Save"}
            </Button>
          </>
        }
      />

      <DraftRecoveryBanner
        visible={hasRecoverableDraft}
        onRestore={restoreDraft}
        onDiscard={discardDraft}
      />

      {isLoading ? (
        <WorkspaceLoading />
      ) : (
        <form
          id="bi-form"
          onSubmit={onSubmit}
          className="grid grid-cols-1 gap-6 rounded-lg border border-border bg-surface p-6 lg:grid-cols-3"
        >
          <div className="space-y-4">
            <FormField label="Business name">
              <Input {...form.register("businessName")} />
            </FormField>
            {ADDRESS_LINE_FIELDS.map((name, i) => (
              <FormField key={name} label={`Business address line ${i + 1}`}>
                <Input {...form.register(name)} />
              </FormField>
            ))}
            <FormField label="Branch name">
              <Input {...form.register("branchName")} />
            </FormField>
          </div>

          <div className="space-y-4">
            <FormField label="Phone number">
              <Input {...form.register("phoneNumber")} />
            </FormField>
            <FormField label="Mobile number">
              <Input {...form.register("mobileNumber")} />
            </FormField>
            <FormField label="Email address">
              <Input type="email" {...form.register("emailAddress")} />
            </FormField>
            <FormField label="Website address">
              <Input {...form.register("websiteAddress")} />
            </FormField>
            <FormField label="Logo URL">
              <Input
                placeholder="https://… (file upload lands with attachments)"
                {...form.register("logoUrl")}
              />
            </FormField>
          </div>

          <div className="space-y-4">
            <FormField label="CNIC">
              <Input {...form.register("cnic")} />
            </FormField>
            <FormField label="STN — Sales Tax Number">
              <Input {...form.register("stn")} />
            </FormField>
            <FormField label="NTN — National Tax Number">
              <Input {...form.register("ntn")} />
            </FormField>
            <label className="flex items-center gap-2 text-sm text-fg">
              <Checkbox {...form.register("applyOnAllPrints")} />
              Apply on all prints
            </label>

            {savedAt && (
              <div className="text-xs text-status-success">Saved at {savedAt.toLocaleTimeString()}</div>
            )}
            {mutation.error instanceof Error && (
              <div className="text-xs text-status-danger" role="alert">
                {mutation.error.message}
              </div>
            )}
          </div>
        </form>
      )}
    </div>
  );
}
