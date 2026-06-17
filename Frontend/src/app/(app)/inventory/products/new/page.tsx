/** New product — catalog §7.1 minimal. Full master (multi-unit, pricing, tax) lands in Phase 6.1. */
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { inventoryApi, type CreateProductInput } from "@/lib/api/tenant";
import { ApiError } from "@/lib/api/client";
import { useCompany } from "@/lib/auth/company-context";
import { hasMeaningfulMasterDraft } from "@/lib/hooks/document-draft-helpers";
import { useAutoCodePreview } from "@/lib/hooks/use-auto-code-preview";
import { useDocumentWorkspaceDraft } from "@/lib/hooks/use-document-workspace-draft";

const schema = z.object({
  code: z.string().optional(),
  name: z.string().min(1, "Required"),
  isStock: z.boolean().default(true),
});
type FormValues = z.infer<typeof schema>;

export default function NewProductPage() {
  const router = useRouter();
  const { companyId } = useCompany();
  const [submitError, setSubmitError] = useState<string | null>(null);

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { code: "", name: "", isStock: true },
  });

  const watched = form.watch();
  const { enabled: autoCode, nextCode } = useAutoCodePreview("product", {
    onPreview: (code) => {
      if (code && !form.getValues("code")) form.setValue("code", code);
    },
  });
  const { topBanner, clearDraftOnSuccess } = useDocumentWorkspaceDraft({
    scope: "product-new",
    companyId,
    form,
    values: watched,
    shouldPersist: (v) => hasMeaningfulMasterDraft(v) || v.isStock === false,
  });

  const mutation = useMutation({
    mutationFn: (input: CreateProductInput) => inventoryApi.createProduct(input),
    onSuccess: () => {
      clearDraftOnSuccess();
      router.push("/inventory/products");
    },
    onError: (err) =>
      setSubmitError(err instanceof ApiError ? err.message : "Could not create product"),
  });

  return (
    <div className="space-y-4">
      {topBanner}
      <PageHeader
        title="Add product"
        breadcrumb="Home / Inventory / Products / Add"
        description="Minimal product master. Multi-unit, pricing, tax codes, batch/expiry, bundles land in Phase 6.1."
        actions={
          <>
            <Button type="button" variant="outline" onClick={() => router.back()}>
              Cancel
            </Button>
            <Button type="submit" form="product-form" disabled={mutation.isPending}>
              {mutation.isPending ? "Saving…" : "Save and close"}
            </Button>
          </>
        }
      />
      <form
        id="product-form"
        onSubmit={form.handleSubmit((v) =>
          mutation.mutate({
            code: v.code?.trim() || null,
            name: v.name,
            isStock: v.isStock,
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
        <label className="flex items-center gap-2 text-sm text-fg">
          <Checkbox {...form.register("isStock")} />
          Stock product (counts in inventory; unchecked = service / non-stock)
        </label>
        {submitError && (
          <div className="rounded-md border border-status-danger/30 bg-status-danger/10 px-3 py-2 text-sm text-status-danger">
            {submitError}
          </div>
        )}
      </form>
    </div>
  );
}
