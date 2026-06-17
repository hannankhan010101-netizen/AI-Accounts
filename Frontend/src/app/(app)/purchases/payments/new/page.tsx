/** New supplier payment — catalog §6.4. */
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
  purchasesApi,
  type SupplierPaymentCreateInput,
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
  paymentDate: z.string().min(1, "Required"),
  supplierId: z.string().min(1, "Required"),
  bankAccountId: z.string().min(1, "Required"),
  totalAmount: z.string().regex(/^\d+(\.\d+)?$/u, "Positive amount required"),
  autoFifo: z.boolean().default(true),
  paymentMethod: z.string().optional(),
  whtCode: z.string().optional(),
  whtAmount: z.string().optional(),
  smartFilters: smartFilterSchema.optional(),
});
type FormValues = z.infer<typeof schema>;

type PaymentDraft = FormValues & { allocations: AllocationRow[] };

export default function NewSupplierPaymentPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { companyId } = useCompany();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [postingWarning, setPostingWarning] = useState<string | null>(null);
  const [allocations, setAllocations] = useState<AllocationRow[]>([]);

  const suppliersQuery = useTenantListQuery(["suppliers"], () => partiesApi.listSuppliers());
  const banksQuery = useTenantListQuery(["bank-accounts"], () => bankApi.listAccounts());

  const { defaultMethod } = useOpMethods();

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      paymentDate: new Date().toISOString().slice(0, 10),
      supplierId: "",
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
  const draftValues = useMemo<PaymentDraft>(
    () => ({ ...watched, allocations }),
    [watched, allocations],
  );

  const { topBanner, clearDraftOnSuccess } = useDocumentWorkspaceDraft<
    PaymentDraft,
    FormValues
  >({
    scope: "supplier-payment-new",
    companyId,
    form,
    values: draftValues,
    shouldPersist: (v) =>
      hasMeaningfulMasterDraft(v) || (v.allocations?.length ?? 0) > 0,
    onRestore: (v) => setAllocations(v.allocations ?? []),
  });

  const demoSandbox = useTourDemoSandbox();
  const supplierIds = useMemo(
    () => suppliersQuery.data?.result.map((s) => s.id) ?? [],
    [suppliersQuery.data],
  );
  const bankAccountIds = useMemo(
    () => banksQuery.data?.result.map((b) => b.id) ?? [],
    [banksQuery.data],
  );
  const { filling: ghostFilling } = useTourGhostFill({
    form,
    context: {
      customerIds: [],
      supplierIds,
      bankAccountIds,
      productCodes: [],
    },
  });

  const supplierName = useMemo(() => {
    const s = suppliersQuery.data?.result.find((x) => x.id === watched.supplierId);
    return s?.name ? String(s.name) : "—";
  }, [suppliersQuery.data, watched.supplierId]);

  const bankName = useMemo(() => {
    const b = banksQuery.data?.result.find((x) => x.id === watched.bankAccountId);
    return b?.name ? String(b.name) : "—";
  }, [banksQuery.data, watched.bankAccountId]);

  const mutation = useMutation({
    mutationFn: (input: SupplierPaymentCreateInput) =>
      purchasesApi.createSupplierPayment(input),
    onSuccess: async (res) => {
      clearDraftOnSuccess();
      await invalidateTenantQueries(queryClient, "supplier-payments");
      const go = () => router.push("/purchases/payments");
      if (!res.posted && res.postingWarning) {
        setPostingWarning(res.postingWarning);
        setTimeout(go, 1500);
      } else {
        go();
      }
    },
    onError: (err) =>
      setSubmitError(err instanceof ApiError ? err.message : "Could not create payment"),
  });

  const onSubmit = form.handleSubmit((values) => {
    if (demoSandbox) return;
    setSubmitError(null);
    setPostingWarning(null);
    mutation.mutate({
      paymentDate: new Date(values.paymentDate).toISOString(),
      supplierId: values.supplierId,
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
            .map((a) => ({ billId: a.documentId, amount: a.amount })),
    });
  });

  return (
    <DocumentWorkspace
      title="New supplier payment"
      breadcrumb="Buy / Payments / New"
      tourRoot="vp-new-header"
      tourSummary="vp-new-summary"
      tourSave="vp-new-save"
      formId="vp-form"
      onSubmit={onSubmit}
      isSaving={mutation.isPending}
      saveLabel="Save payment"
      onCancel={() => router.push("/purchases/payments")}
      grandTotal={watched.totalAmount || "0.00"}
      grandTotalLabel="Payment amount"
      error={submitError}
      warning={postingWarning}
      topBanner={topBanner}
      demoSandbox={demoSandbox}
      demoSandboxBanner={<DemoSandboxBanner filling={ghostFilling} />}
      summaryLines={[
        { label: "Supplier", value: supplierName, emphasis: true },
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
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2" data-tour="vp-new-header">
          <FormField label="Payment date" required error={form.formState.errors.paymentDate?.message}>
            <Input type="date" {...form.register("paymentDate")} />
          </FormField>
          <FormField label="Supplier" required error={form.formState.errors.supplierId?.message}>
            <Select {...form.register("supplierId")}>
              <option value="">Select…</option>
              {suppliersQuery.data?.result.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                  {s.code ? ` (${s.code})` : ""}
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
      <label className="flex items-start gap-2 text-sm text-fg" data-tour="vp-new-alloc">
        <Checkbox {...form.register("autoFifo")} className="mt-0.5" />
        <span>
          <span className="font-medium">Auto-allocate against open bills (FIFO)</span>
          <span className="block text-xs text-fg-muted">
            Oldest bill first. Uncheck to allocate manually below.
          </span>
        </span>
      </label>

      {!watched.autoFifo && (
        <AllocationPicker
          mode="supplier"
          partyId={watched.supplierId}
          receiptTotal={watched.totalAmount}
          rows={allocations}
          onChange={setAllocations}
        />
      )}

      <section className="space-y-3 border-t border-border pt-4">
        <h3 className="text-sm font-medium text-fg">Smart filters</h3>
        <SmartDocumentFilters module="purchases" register={form.register} />
      </section>
    </DocumentWorkspace>
  );
}
