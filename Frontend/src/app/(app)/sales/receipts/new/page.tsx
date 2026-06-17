/** New customer receipt — catalog §5.8. */
"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { AllocationPicker, type AllocationRow } from "@/components/app/allocation-picker";
import { PaymentMethodField } from "@/components/app/payment-method-field";
import { DocumentWorkspace } from "@/components/patterns/document-workspace";
import { SmartDocumentFilters } from "@/components/patterns/smart-document-filters";
import { Checkbox } from "@/components/ui/checkbox";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import {
  bankApi,
  partiesApi,
  salesApi,
  type SalesReceiptCreateInput,
} from "@/lib/api/tenant";
import { ApiError } from "@/lib/api/client";
import { useCompany } from "@/lib/auth/company-context";
import { hasMeaningfulMasterDraft } from "@/lib/hooks/document-draft-helpers";
import { useDocumentWorkspaceDraft } from "@/lib/hooks/use-document-workspace-draft";
import { invalidateTenantQueries, useTenantListQuery } from "@/lib/api/tenant-query";
import { useOpMethods } from "@/lib/hooks/use-op-methods";
import { opMethodLabel } from "@/lib/settings/op-methods-catalog";
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
  receiptDate: z.string().min(1, "Required"),
  customerId: z.string().min(1, "Required"),
  bankAccountId: z.string().min(1, "Required"),
  totalAmount: z.string().regex(/^\d+(\.\d+)?$/u, "Positive amount required"),
  autoFifo: z.boolean().default(true),
  paymentMethod: z.string().optional(),
  whtCode: z.string().optional(),
  whtAmount: z.string().optional(),
  smartFilters: smartFilterSchema.optional(),
});
type FormValues = z.infer<typeof schema>;

type ReceiptDraft = FormValues & { allocations: AllocationRow[] };

export default function NewSalesReceiptPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { companyId } = useCompany();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [postingWarning, setPostingWarning] = useState<string | null>(null);
  const [allocations, setAllocations] = useState<AllocationRow[]>([]);

  const customersQuery = useTenantListQuery(["customers"], () => partiesApi.listCustomers());
  const banksQuery = useTenantListQuery(["bank-accounts"], () => bankApi.listAccounts());

  const { defaultMethod } = useOpMethods();

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      receiptDate: new Date().toISOString().slice(0, 10),
      customerId: "",
      bankAccountId: "",
      totalAmount: "",
      autoFifo: true,
      paymentMethod: "",
    },
  });

  useEffect(() => {
    if (defaultMethod && !form.getValues("paymentMethod")) {
      form.setValue("paymentMethod", defaultMethod);
    }
  }, [defaultMethod, form]);

  const watched = form.watch();
  const draftValues = useMemo<ReceiptDraft>(
    () => ({ ...watched, allocations }),
    [watched, allocations],
  );

  const { topBanner, clearDraftOnSuccess } = useDocumentWorkspaceDraft<
    ReceiptDraft,
    FormValues
  >({
    scope: "sales-receipt-new",
    companyId,
    form,
    values: draftValues,
    shouldPersist: (v) =>
      hasMeaningfulMasterDraft(v) || (v.allocations?.length ?? 0) > 0,
    onRestore: (v) => setAllocations(v.allocations ?? []),
  });

  const demoSandbox = useTourDemoSandbox();
  const customerIds = useMemo(
    () => customersQuery.data?.result.map((c) => c.id) ?? [],
    [customersQuery.data],
  );
  const bankAccountIds = useMemo(
    () => banksQuery.data?.result.map((b) => b.id) ?? [],
    [banksQuery.data],
  );
  const { filling: ghostFilling } = useTourGhostFill({
    form,
    context: {
      customerIds,
      supplierIds: [],
      bankAccountIds,
      productCodes: [],
    },
  });

  const customerName = useMemo(() => {
    const c = customersQuery.data?.result.find((x) => x.id === watched.customerId);
    return c?.name ? String(c.name) : "—";
  }, [customersQuery.data, watched.customerId]);

  const bankName = useMemo(() => {
    const b = banksQuery.data?.result.find((x) => x.id === watched.bankAccountId);
    return b?.name ? String(b.name) : "—";
  }, [banksQuery.data, watched.bankAccountId]);

  const mutation = useMutation({
    mutationFn: (input: SalesReceiptCreateInput) => salesApi.createReceipt(input),
    onSuccess: async (res) => {
      clearDraftOnSuccess();
      await invalidateTenantQueries(queryClient, "sales-receipts");
      const id = res.result?.id;
      const go = () => (id ? router.push(`/sales/receipts/${id}`) : router.push("/sales/receipts"));
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
      customerId: values.customerId,
      bankAccountId: values.bankAccountId,
      totalAmount: values.totalAmount,
      whtCode: values.whtCode || null,
      whtAmount: values.whtAmount || null,
      paymentMethod: values.paymentMethod || defaultMethod || null,
      smartFilters: values.smartFilters,
      autoFifo: values.autoFifo,
      allocations: values.autoFifo
        ? undefined
        : allocations
            .filter((a) => a.amount && Number(a.amount) > 0)
            .map((a) => ({ invoiceId: a.documentId, amount: a.amount })),
    });
  });

  return (
    <DocumentWorkspace
      title="New customer receipt"
      breadcrumb="Sell / Receipts / New"
      tourRoot="sr-new-header"
      tourSummary="sr-new-summary"
      tourSave="sr-new-save"
      formId="sr-form"
      onSubmit={onSubmit}
      isSaving={mutation.isPending}
      saveLabel="Save receipt"
      onCancel={() => router.push("/sales/receipts")}
      grandTotal={watched.totalAmount || "0.00"}
      grandTotalLabel="Receipt amount"
      error={submitError}
      warning={postingWarning}
      topBanner={topBanner}
      demoSandbox={demoSandbox}
      demoSandboxBanner={<DemoSandboxBanner filling={ghostFilling} />}
      summaryLines={[
        { label: "Customer", value: customerName, emphasis: true },
        { label: "Bank", value: bankName },
        {
          label: "Method",
          value: opMethodLabel(watched.paymentMethod || defaultMethod),
        },
        {
          label: "Allocation",
          value: watched.autoFifo ? "FIFO (automatic)" : "Manual",
        },
      ]}
      header={
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2" data-tour="sr-new-header">
          <FormField label="Receipt date" required error={form.formState.errors.receiptDate?.message}>
            <Input type="date" {...form.register("receiptDate")} />
          </FormField>
          <FormField label="Customer" required error={form.formState.errors.customerId?.message}>
            <Select {...form.register("customerId")}>
              <option value="">Select…</option>
              {customersQuery.data?.result.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                  {c.code ? ` (${c.code})` : ""}
                </option>
              ))}
            </Select>
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
          <FormField label="Total amount (bank)" required error={form.formState.errors.totalAmount?.message}>
            <Input inputMode="decimal" {...form.register("totalAmount")} />
          </FormField>
          <PaymentMethodField
            value={watched.paymentMethod ?? ""}
            onChange={(v) => form.setValue("paymentMethod", v, { shouldDirty: true })}
          />
          <FormField label="WHT code">
            <Input placeholder="Optional" {...form.register("whtCode")} />
          </FormField>
          <FormField label="WHT amount">
            <Input inputMode="decimal" placeholder="Withheld tax" {...form.register("whtAmount")} />
          </FormField>
        </div>
      }
    >
      <label className="flex items-start gap-2 text-sm text-fg" data-tour="sr-new-alloc">
        <Checkbox {...form.register("autoFifo")} className="mt-0.5" />
        <span>
          <span className="font-medium">Auto-allocate against open invoices (FIFO)</span>
          <span className="block text-xs text-fg-muted">
            Oldest invoice first. Uncheck to allocate manually below.
          </span>
        </span>
      </label>

      {!watched.autoFifo && (
        <AllocationPicker
          mode="customer"
          partyId={watched.customerId}
          receiptTotal={watched.totalAmount}
          rows={allocations}
          onChange={setAllocations}
        />
      )}

      <section className="space-y-3 border-t border-border pt-4">
        <h3 className="text-sm font-medium text-fg">Smart filters</h3>
        <SmartDocumentFilters module="sales" register={form.register} />
      </section>
    </DocumentWorkspace>
  );
}
