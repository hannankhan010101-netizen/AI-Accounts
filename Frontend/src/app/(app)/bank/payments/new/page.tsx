/**
 * New bank payment — catalog §4.2.
 * Header-only for now (matches BankPaymentCreateRequest); multi-line splits land in Phase 3.2.
 */
"use client";

import { useMemo, useState } from "react";
import Decimal from "decimal.js";
import { useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { Button } from "@/components/ui/button";
import { DocumentWorkspace } from "@/components/patterns/document-workspace";
import { TransactionTemplatePicker } from "@/components/patterns/transaction-template-picker";
import { SmartDocumentFilters } from "@/components/patterns/smart-document-filters";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { bankApi, type BankPaymentCreateInput } from "@/lib/api/tenant";
import { ApiError } from "@/lib/api/client";
import { useCompany } from "@/lib/auth/company-context";
import { useDocumentWorkspaceDraft } from "@/lib/hooks/use-document-workspace-draft";
import { invalidateTenantQueries, useTenantListQuery } from "@/lib/api/tenant-query";
import { DemoSandboxBanner } from "@/components/onboarding/demo-sandbox-banner";
import {
  useTourDemoSandbox,
  useTourGhostFill,
} from "@/features/onboarding/hooks/use-tour-ghost-fill";

const smartFilterSchema = z.object({
  filter1: z.string().optional(),
  filter2: z.string().optional(),
  filter3: z.string().optional(),
  filter4: z.string().optional(),
  doc1: z.string().optional(),
  doc2: z.string().optional(),
  doc3: z.string().optional(),
  doc4: z.string().optional(),
});

const schema = z.object({
  bankAccountId: z.string().min(1, "Required"),
  paymentDate: z.string().min(1, "Required"),
  totalAmount: z.string().regex(/^\d+(\.\d+)?$/u, "Positive amount required"),
  nominalCode: z.string().optional(),
  useSplit: z.boolean().optional(),
  smartFilters: smartFilterSchema.optional(),
});
type FormValues = z.infer<typeof schema>;

type SplitLine = { nominalCode: string; amount: string };

export default function NewBankPaymentPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { companyId } = useCompany();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [useSplit, setUseSplit] = useState(false);
  const [splitLines, setSplitLines] = useState<SplitLine[]>([
    { nominalCode: "", amount: "" },
  ]);

  const accountsQuery = useTenantListQuery(["bank-accounts"], () => bankApi.listAccounts());

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      bankAccountId: "",
      paymentDate: new Date().toISOString().slice(0, 10),
      totalAmount: "",
      nominalCode: "",
    },
  });

  const watched = form.watch();

  const { topBanner, clearDraftOnSuccess } = useDocumentWorkspaceDraft({
    scope: "bank-payment-new",
    companyId,
    form,
    values: watched,
  });

  const demoSandbox = useTourDemoSandbox();
  const bankAccountIds = useMemo(
    () => accountsQuery.data?.result.map((a) => a.id) ?? [],
    [accountsQuery.data],
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
    const a = accountsQuery.data?.result.find((x) => x.id === watched.bankAccountId);
    return a?.name ? String(a.name) : "—";
  }, [accountsQuery.data, watched.bankAccountId]);

  const mutation = useMutation({
    mutationFn: (input: BankPaymentCreateInput) => bankApi.createPayment(input),
    onSuccess: async (res) => {
      clearDraftOnSuccess();
      await invalidateTenantQueries(queryClient, "bank-payments");
      if (res.id) router.push(`/bank/payments/${res.id}`);
      else router.push("/bank/payments");
    },
    onError: (err) =>
      setSubmitError(err instanceof ApiError ? err.message : "Could not create payment"),
  });

  const onSubmit = form.handleSubmit((values) => {
    if (demoSandbox) return;
    setSubmitError(null);
    const body: BankPaymentCreateInput = {
      bankAccountId: values.bankAccountId,
      paymentDate: new Date(values.paymentDate).toISOString(),
      totalAmount: values.totalAmount,
      smartFilters: values.smartFilters,
    };
    if (useSplit) {
      const lines = splitLines.filter((l) => l.nominalCode.trim() && l.amount.trim());
      const sum = lines.reduce(
        (acc, l) => acc.plus(new Decimal(l.amount || "0")),
        new Decimal(0),
      );
      if (!sum.eq(values.totalAmount)) {
        setSubmitError("Split line amounts must equal the payment total.");
        return;
      }
      body.nominalLines = lines;
    } else {
      body.nominalCode = values.nominalCode || undefined;
    }
    mutation.mutate(body);
  });

  const loadTemplate = (payload: Record<string, unknown>) => {
    if (typeof payload.bankAccountId === "string") form.setValue("bankAccountId", payload.bankAccountId);
    if (typeof payload.paymentDate === "string") form.setValue("paymentDate", payload.paymentDate);
    if (typeof payload.totalAmount === "string") form.setValue("totalAmount", payload.totalAmount);
    if (typeof payload.nominalCode === "string") form.setValue("nominalCode", payload.nominalCode);
    if (payload.smartFilters && typeof payload.smartFilters === "object") {
      form.setValue("smartFilters", payload.smartFilters as FormValues["smartFilters"]);
    }
    if (Array.isArray(payload.splitLines)) {
      setUseSplit(true);
      setSplitLines(payload.splitLines as SplitLine[]);
    }
  };

  return (
    <DocumentWorkspace
      title="New bank payment"
      breadcrumb="Money / Payments out / New"
      tourRoot="bp-new-header"
      tourSummary="bp-new-summary"
      tourSave="bp-new-save"
      formId="bp-form"
      onSubmit={onSubmit}
      isSaving={mutation.isPending}
      saveLabel="Save payment"
      onCancel={() => router.push("/bank/payments")}
      grandTotal={watched.totalAmount || "0.00"}
      grandTotalLabel="Payment amount"
      error={submitError}
      topBanner={topBanner}
      demoSandbox={demoSandbox}
      demoSandboxBanner={<DemoSandboxBanner filling={ghostFilling} />}
      summaryLines={[
        { label: "Bank account", value: bankName, emphasis: true },
        { label: "Nominal", value: watched.nominalCode || "Default" },
      ]}
      header={
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2" data-tour="bp-new-header">
          <FormField label="Bank account" required error={form.formState.errors.bankAccountId?.message}>
            <Select {...form.register("bankAccountId")}>
              <option value="">Select…</option>
              {accountsQuery.data?.result.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name}
                  {a.code ? ` (${a.code})` : ""}
                </option>
              ))}
            </Select>
          </FormField>
          <FormField label="Payment date" required error={form.formState.errors.paymentDate?.message}>
            <Input type="date" {...form.register("paymentDate")} />
          </FormField>
          <FormField label="Total amount" required error={form.formState.errors.totalAmount?.message}>
            <Input inputMode="decimal" {...form.register("totalAmount")} />
          </FormField>
          <FormField label="Nominal code (optional)" error={form.formState.errors.nominalCode?.message}>
            <Input placeholder="Uses company default if blank" {...form.register("nominalCode")} />
          </FormField>
        </div>
      }
    >
      <TransactionTemplatePicker
        module="bank_payment"
        onLoad={loadTemplate}
        onCapturePayload={() => ({
          bankAccountId: form.getValues("bankAccountId"),
          paymentDate: form.getValues("paymentDate"),
          totalAmount: form.getValues("totalAmount"),
          nominalCode: form.getValues("nominalCode"),
          smartFilters: form.getValues("smartFilters"),
          splitLines: useSplit ? splitLines : undefined,
        })}
      />
      <div className="space-y-3">
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={useSplit}
            onChange={(e) => setUseSplit(e.target.checked)}
          />
          Split across multiple nominal codes
        </label>
        {useSplit ? (
          <div className="space-y-2">
            {splitLines.map((line, i) => (
              <div key={i} className="flex gap-2">
                <Input
                  placeholder="Nominal code"
                  value={line.nominalCode}
                  onChange={(e) => {
                    const next = [...splitLines];
                    next[i] = { ...line, nominalCode: e.target.value };
                    setSplitLines(next);
                  }}
                />
                <Input
                  placeholder="Amount"
                  className="w-32"
                  inputMode="decimal"
                  value={line.amount}
                  onChange={(e) => {
                    const next = [...splitLines];
                    next[i] = { ...line, amount: e.target.value };
                    setSplitLines(next);
                  }}
                />
              </div>
            ))}
            <Button
              type="button"
              size="sm"
              variant="outline"
              onClick={() => setSplitLines([...splitLines, { nominalCode: "", amount: "" }])}
            >
              Add line
            </Button>
          </div>
        ) : null}
      </div>
      <section className="mt-6 border-t border-border pt-4">
        <h3 className="mb-3 text-sm font-medium text-fg-muted">Smart filters</h3>
        <SmartDocumentFilters module="bank" register={form.register} />
      </section>
    </DocumentWorkspace>
  );
}
