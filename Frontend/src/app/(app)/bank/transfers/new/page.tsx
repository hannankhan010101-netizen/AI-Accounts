/** New bank transfer — catalog §4.4. */
"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { DocumentWorkspace } from "@/components/patterns/document-workspace";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { bankApi, type BankTransferCreateInput } from "@/lib/api/tenant";
import { ApiError } from "@/lib/api/client";
import { useCompany } from "@/lib/auth/company-context";
import { useDocumentWorkspaceDraft } from "@/lib/hooks/use-document-workspace-draft";
import { invalidateTenantQueries, useTenantListQuery } from "@/lib/api/tenant-query";

const schema = z
  .object({
    transferDate: z.string().min(1, "Required"),
    fromBankAccountId: z.string().min(1, "Required"),
    toBankAccountId: z.string().min(1, "Required"),
    totalAmount: z.string().regex(/^\d+(\.\d+)?$/u, "Positive amount required"),
  })
  .refine((v) => v.fromBankAccountId !== v.toBankAccountId, {
    message: "From and To must differ",
    path: ["toBankAccountId"],
  });
type FormValues = z.infer<typeof schema>;

export default function NewBankTransferPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { companyId } = useCompany();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [postingWarning, setPostingWarning] = useState<string | null>(null);

  const banksQuery = useTenantListQuery(["bank-accounts"], () => bankApi.listAccounts());

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      transferDate: new Date().toISOString().slice(0, 10),
      fromBankAccountId: "",
      toBankAccountId: "",
      totalAmount: "",
    },
  });

  const watched = form.watch();
  const accounts = banksQuery.data?.result ?? [];

  const { topBanner, clearDraftOnSuccess } = useDocumentWorkspaceDraft({
    scope: "bank-transfer-new",
    companyId,
    form,
    values: watched,
  });

  const accountLabel = (id: string) => {
    const b = accounts.find((x) => x.id === id);
    return b?.name ? String(b.name) : "—";
  };

  const fromName = useMemo(() => accountLabel(watched.fromBankAccountId), [accounts, watched.fromBankAccountId]);
  const toName = useMemo(() => accountLabel(watched.toBankAccountId), [accounts, watched.toBankAccountId]);

  const mutation = useMutation({
    mutationFn: (input: BankTransferCreateInput) => bankApi.createTransfer(input),
    onSuccess: async (res) => {
      clearDraftOnSuccess();
      await invalidateTenantQueries(queryClient, "bank-transfers");
      const id = res.result?.id;
      const go = () => (id ? router.push(`/bank/transfers/${id}`) : router.push("/bank/transfers"));
      if (!res.posted && res.postingWarning) {
        setPostingWarning(res.postingWarning);
        setTimeout(go, 1500);
      } else {
        go();
      }
    },
    onError: (err) =>
      setSubmitError(err instanceof ApiError ? err.message : "Could not create transfer"),
  });

  const onSubmit = form.handleSubmit((values) => {
    setSubmitError(null);
    setPostingWarning(null);
    mutation.mutate({
      transferDate: new Date(values.transferDate).toISOString(),
      fromBankAccountId: values.fromBankAccountId,
      toBankAccountId: values.toBankAccountId,
      totalAmount: values.totalAmount,
    });
  });

  return (
    <DocumentWorkspace
      title="New bank transfer"
      breadcrumb="Money / Transfers / New"
      formId="bt-form"
      onSubmit={onSubmit}
      isSaving={mutation.isPending}
      saveLabel="Save transfer"
      onCancel={() => router.push("/bank/transfers")}
      grandTotal={watched.totalAmount || "0.00"}
      grandTotalLabel="Transfer amount"
      error={submitError}
      warning={postingWarning}
      topBanner={topBanner}
      summaryLines={[
        { label: "From", value: fromName, emphasis: true },
        { label: "To", value: toName, emphasis: true },
      ]}
      header={
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <FormField label="Transfer date" required error={form.formState.errors.transferDate?.message}>
            <Input type="date" {...form.register("transferDate")} />
          </FormField>
          <div className="hidden md:block" />
          <FormField label="From bank account" required error={form.formState.errors.fromBankAccountId?.message}>
            <Select {...form.register("fromBankAccountId")}>
              <option value="">Select…</option>
              {accounts.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                  {b.code ? ` (${b.code})` : ""}
                </option>
              ))}
            </Select>
          </FormField>
          <FormField label="To bank account" required error={form.formState.errors.toBankAccountId?.message}>
            <Select {...form.register("toBankAccountId")}>
              <option value="">Select…</option>
              {accounts.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                  {b.code ? ` (${b.code})` : ""}
                </option>
              ))}
            </Select>
          </FormField>
          <FormField label="Total amount" required error={form.formState.errors.totalAmount?.message}>
            <Input inputMode="decimal" {...form.register("totalAmount")} />
          </FormField>
        </div>
      }
    >
      <p className="text-sm text-fg-muted">
        Posts DR to-bank / CR from-bank when both accounts have nominal codes configured.
      </p>
    </DocumentWorkspace>
  );
}
