/** New bank receipt — catalog §4.3. */
"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { DocumentWorkspace } from "@/components/patterns/document-workspace";
import { TransactionTemplatePicker } from "@/components/patterns/transaction-template-picker";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { bankApi, type BankReceiptCreateInput } from "@/lib/api/tenant";
import { ApiError } from "@/lib/api/client";
import { useCompany } from "@/lib/auth/company-context";
import { useDocumentWorkspaceDraft } from "@/lib/hooks/use-document-workspace-draft";
import { invalidateTenantQueries, useTenantListQuery } from "@/lib/api/tenant-query";
import { DemoSandboxBanner } from "@/components/onboarding/demo-sandbox-banner";
import {
  useTourDemoSandbox,
  useTourGhostFill,
} from "@/features/onboarding/hooks/use-tour-ghost-fill";

const schema = z.object({
  receiptDate: z.string().min(1, "Required"),
  bankAccountId: z.string().min(1, "Required"),
  totalAmount: z.string().regex(/^\d+(\.\d+)?$/u, "Positive amount required"),
  nominalCode: z.string().optional(),
});
type FormValues = z.infer<typeof schema>;

export default function NewBankReceiptPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { companyId } = useCompany();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [postingWarning, setPostingWarning] = useState<string | null>(null);

  const banksQuery = useTenantListQuery(["bank-accounts"], () => bankApi.listAccounts());

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      receiptDate: new Date().toISOString().slice(0, 10),
      bankAccountId: "",
      totalAmount: "",
      nominalCode: "",
    },
  });

  const watched = form.watch();

  const { topBanner, clearDraftOnSuccess } = useDocumentWorkspaceDraft({
    scope: "bank-receipt-new",
    companyId,
    form,
    values: watched,
  });

  const demoSandbox = useTourDemoSandbox();
  const bankAccountIds = useMemo(
    () => banksQuery.data?.result.map((b) => b.id) ?? [],
    [banksQuery.data],
  );
  const { filling: ghostFilling } = useTourGhostFill({
    form,
    context: {
      customerIds: [],
      supplierIds: [],
      bankAccountIds,
      productCodes: [],
    },
  });

  const bankName = useMemo(() => {
    const b = banksQuery.data?.result.find((x) => x.id === watched.bankAccountId);
    return b?.name ? String(b.name) : "—";
  }, [banksQuery.data, watched.bankAccountId]);

  const mutation = useMutation({
    mutationFn: (input: BankReceiptCreateInput) => bankApi.createReceipt(input),
    onSuccess: async (res) => {
      clearDraftOnSuccess();
      await invalidateTenantQueries(queryClient, "bank-receipts");
      const id = res.result?.id;
      const go = () => (id ? router.push(`/bank/receipts/${id}`) : router.push("/bank/receipts"));
      if (!res.posted && res.postingWarning) {
        setPostingWarning(res.postingWarning);
        setTimeout(go, 1500);
      } else {
        go();
      }
    },
    onError: (err) =>
      setSubmitError(err instanceof ApiError ? err.message : "Could not create receipt"),
  });

  const onSubmit = form.handleSubmit((values) => {
    if (demoSandbox) return;
    setSubmitError(null);
    setPostingWarning(null);
    mutation.mutate({
      receiptDate: new Date(values.receiptDate).toISOString(),
      bankAccountId: values.bankAccountId,
      totalAmount: values.totalAmount,
      nominalCode: values.nominalCode || undefined,
    });
  });

  const loadTemplate = (payload: Record<string, unknown>) => {
    if (typeof payload.receiptDate === "string") form.setValue("receiptDate", payload.receiptDate);
    if (typeof payload.bankAccountId === "string") form.setValue("bankAccountId", payload.bankAccountId);
    if (typeof payload.totalAmount === "string") form.setValue("totalAmount", payload.totalAmount);
    if (typeof payload.nominalCode === "string") form.setValue("nominalCode", payload.nominalCode);
  };

  return (
    <DocumentWorkspace
      title="New bank receipt"
      breadcrumb="Money / Receipts in / New"
      tourRoot="br-new-header"
      tourSummary="br-new-summary"
      tourSave="br-new-save"
      formId="br-form"
      onSubmit={onSubmit}
      isSaving={mutation.isPending}
      saveLabel="Save receipt"
      onCancel={() => router.push("/bank/receipts")}
      grandTotal={watched.totalAmount || "0.00"}
      grandTotalLabel="Receipt amount"
      error={submitError}
      warning={postingWarning}
      topBanner={topBanner}
      demoSandbox={demoSandbox}
      demoSandboxBanner={<DemoSandboxBanner filling={ghostFilling} />}
      summaryLines={[
        { label: "Bank account", value: bankName, emphasis: true },
        { label: "Nominal (CR)", value: watched.nominalCode || "Skip GL" },
      ]}
      header={
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2" data-tour="br-new-header">
          <FormField label="Receipt date" required error={form.formState.errors.receiptDate?.message}>
            <Input type="date" {...form.register("receiptDate")} />
          </FormField>
          <FormField label="Bank account" required error={form.formState.errors.bankAccountId?.message}>
            <Select {...form.register("bankAccountId")}>
              <option value="">Select…</option>
              {banksQuery.data?.result.map((b) => (
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
          <FormField label="Counterpart nominal (optional)">
            <Input
              placeholder="Income nominal — leave blank to skip GL"
              {...form.register("nominalCode")}
            />
          </FormField>
        </div>
      }
    >
      <TransactionTemplatePicker
        module="bank_receipt"
        onLoad={loadTemplate}
        onCapturePayload={() => ({
          receiptDate: form.getValues("receiptDate"),
          bankAccountId: form.getValues("bankAccountId"),
          totalAmount: form.getValues("totalAmount"),
          nominalCode: form.getValues("nominalCode"),
        })}
      />
      <p className="text-sm text-fg-muted">
        Posts DR bank / CR counterpart nominal for refunds, capital, or other income.
      </p>
    </DocumentWorkspace>
  );
}
