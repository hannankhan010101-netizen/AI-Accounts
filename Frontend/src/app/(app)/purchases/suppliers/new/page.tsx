/** New supplier — catalog §6.1. */
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { partiesApi, type CreateSupplierInput } from "@/lib/api/tenant";
import { ApiError } from "@/lib/api/client";
import { useCompany } from "@/lib/auth/company-context";
import { hasMeaningfulMasterDraft } from "@/lib/hooks/document-draft-helpers";
import { useAutoCodePreview } from "@/lib/hooks/use-auto-code-preview";
import { useDocumentWorkspaceDraft } from "@/lib/hooks/use-document-workspace-draft";

const schema = z.object({
  code: z.string().optional(),
  name: z.string().min(1, "Required"),
  email: z.string().email("Invalid email").or(z.literal("")).optional(),
  phone: z.string().optional(),
});
type FormValues = z.infer<typeof schema>;

export default function NewSupplierPage() {
  const router = useRouter();
  const { companyId } = useCompany();
  const [submitError, setSubmitError] = useState<string | null>(null);

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { code: "", name: "", email: "", phone: "" },
  });

  const watched = form.watch();
  const { enabled: autoCode, nextCode } = useAutoCodePreview("supplier", {
    onPreview: (code) => {
      if (code && !form.getValues("code")) form.setValue("code", code);
    },
  });
  const { topBanner, clearDraftOnSuccess } = useDocumentWorkspaceDraft({
    scope: "supplier-new",
    companyId,
    form,
    values: watched,
    shouldPersist: hasMeaningfulMasterDraft,
  });

  const mutation = useMutation({
    mutationFn: (input: CreateSupplierInput) => partiesApi.createSupplier(input),
    onSuccess: () => {
      clearDraftOnSuccess();
      router.push("/purchases/suppliers");
    },
    onError: (err) =>
      setSubmitError(err instanceof ApiError ? err.message : "Could not create supplier"),
  });

  return (
    <div className="space-y-4">
      {topBanner}
      <PageHeader
        title="Add supplier"
        breadcrumb="Home / Purchases / Suppliers / Add"
        description="Minimal master record (§6.1). Full party fields ship with Phase 5.1."
        actions={
          <>
            <Button type="button" variant="outline" onClick={() => router.back()}>
              Cancel
            </Button>
            <Button type="submit" form="supplier-form" disabled={mutation.isPending}>
              {mutation.isPending ? "Saving…" : "Save and close"}
            </Button>
          </>
        }
      />
      <form
        id="supplier-form"
        onSubmit={form.handleSubmit((v) =>
          mutation.mutate({
            code: v.code?.trim() || null,
            name: v.name,
            email: v.email || null,
            phone: v.phone || null,
          }),
        )}
        className="max-w-2xl space-y-4 rounded-lg border border-border bg-surface p-6"
      >
        <FormField
          label={autoCode ? "Code (auto)" : "Code"}
          required={!autoCode}
          error={form.formState.errors.code?.message}
        >
          <Input placeholder={nextCode ?? undefined} {...form.register("code")} />
        </FormField>
        <FormField label="Name" required error={form.formState.errors.name?.message}>
          <Input {...form.register("name")} />
        </FormField>
        <FormField label="Email" error={form.formState.errors.email?.message}>
          <Input type="email" {...form.register("email")} />
        </FormField>
        <FormField label="Phone">
          <Input {...form.register("phone")} />
        </FormField>
        {submitError && (
          <div className="rounded-md border border-status-danger/30 bg-status-danger/10 px-3 py-2 text-sm text-status-danger">
            {submitError}
          </div>
        )}
      </form>
    </div>
  );
}
