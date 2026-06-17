/** New PDC received — catalog §5.7. */
"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { Select } from "@/components/ui/select";
import { partiesApi, pdcApi, type PdcReceivedCreateInput } from "@/lib/api/tenant";
import { ApiError } from "@/lib/api/client";
import { useCompany } from "@/lib/auth/company-context";
import { hasMeaningfulMasterDraft } from "@/lib/hooks/document-draft-helpers";
import { useDocumentWorkspaceDraft } from "@/lib/hooks/use-document-workspace-draft";

const schema = z.object({
  chequeNumber: z.string().min(1),
  bankName: z.string().min(1),
  customerId: z.string().min(1),
  receivedDate: z.string().min(1),
  chequeDate: z.string().min(1),
  amount: z.string().regex(/^\d+(\.\d+)?$/u),
  notes: z.string().optional(),
});
type FormValues = z.infer<typeof schema>;

export default function NewPdcReceivedPage() {
  const router = useRouter();
  const { companyId } = useCompany();
  const [error, setError] = useState<string | null>(null);
  const customersQuery = useTenantListQuery(["customers"], () => partiesApi.listCustomers());
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      chequeNumber: "",
      bankName: "",
      customerId: "",
      receivedDate: new Date().toISOString().slice(0, 10),
      chequeDate: new Date().toISOString().slice(0, 10),
      amount: "",
      notes: "",
    },
  });

  const watched = form.watch();
  const { topBanner, clearDraftOnSuccess } = useDocumentWorkspaceDraft({
    scope: "pdc-received-new",
    companyId,
    form,
    values: watched,
    shouldPersist: hasMeaningfulMasterDraft,
  });

  const mutation = useMutation({
    mutationFn: (input: PdcReceivedCreateInput) => pdcApi.createReceived(input),
    onSuccess: (res) => {
      clearDraftOnSuccess();
      const id = res.result?.id;
      router.push(id ? `/sales/pdc-received/${id}` : "/sales/pdc-received");
    },
    onError: (err) => setError(err instanceof ApiError ? err.message : "Could not save"),
  });

  return (
    <div className="space-y-4">
      {topBanner}
      <PageHeader
        title="New PDC received"
        breadcrumb="Home / Sales / PDC Received / New"
        actions={
          <>
            <Button type="button" variant="outline" onClick={() => router.back()}>
              Cancel
            </Button>
            <Button type="submit" form="pdcr-form" disabled={mutation.isPending}>
              {mutation.isPending ? "Saving…" : "Save"}
            </Button>
          </>
        }
      />
      <form
        id="pdcr-form"
        onSubmit={form.handleSubmit((v) =>
          mutation.mutate({
            chequeNumber: v.chequeNumber,
            bankName: v.bankName,
            customerId: v.customerId,
            receivedDate: new Date(v.receivedDate).toISOString(),
            chequeDate: new Date(v.chequeDate).toISOString(),
            amount: v.amount,
            notes: v.notes || null,
          }),
        )}
        className="max-w-2xl space-y-4 rounded-lg border border-border bg-surface p-6"
      >
        <FormField label="Cheque number" required>
          <Input {...form.register("chequeNumber")} />
        </FormField>
        <FormField label="Drawer bank" required>
          <Input {...form.register("bankName")} />
        </FormField>
        <FormField label="Customer" required>
          <Select {...form.register("customerId")}>
            <option value="">Select…</option>
            {customersQuery.data?.result.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </Select>
        </FormField>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
          <FormField label="Received date" required>
            <Input type="date" {...form.register("receivedDate")} />
          </FormField>
          <FormField label="Cheque date" required>
            <Input type="date" {...form.register("chequeDate")} />
          </FormField>
        </div>
        <FormField label="Amount" required>
          <Input inputMode="decimal" {...form.register("amount")} />
        </FormField>
        <FormField label="Notes">
          <Input {...form.register("notes")} />
        </FormField>
        {error && (
          <div className="rounded-md border border-status-danger/30 bg-status-danger/10 px-3 py-2 text-sm text-status-danger">
            {error}
          </div>
        )}
      </form>
    </div>
  );
}
