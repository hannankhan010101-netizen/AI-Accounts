/** Shared advance return form — FA §5.8 / §6.4 */
"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import { useRouter } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { DocumentWorkspace } from "@/components/patterns/document-workspace";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { bankApi } from "@/lib/api/tenant";
import { ApiError } from "@/lib/api/client";

const schema = z.object({
  returnDate: z.string().min(1, "Required"),
  amount: z.string().regex(/^\d+(\.\d+)?$/u, "Enter a positive amount"),
  bankAccountId: z.string().min(1, "Required"),
});

type FormValues = z.infer<typeof schema>;

interface AdvanceReturnFormProps {
  title: string;
  breadcrumb: string;
  cancelHref: string;
  defaultBankAccountId: string;
  maxAmount: string;
  submitLabel: string;
  onSubmit: (values: {
    returnDate: string;
    amount: string;
    bankAccountId: string;
  }) => Promise<void>;
}

export function AdvanceReturnForm({
  title,
  breadcrumb,
  cancelHref,
  defaultBankAccountId,
  maxAmount,
  submitLabel,
  onSubmit,
}: AdvanceReturnFormProps) {
  const router = useRouter();
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      returnDate: new Date().toISOString().slice(0, 10),
      amount: maxAmount,
      bankAccountId: defaultBankAccountId,
    },
  });

  const banksQuery = useTenantListQuery(["bank-accounts"], () => bankApi.listAccounts());

  const mutation = useMutation({
    mutationFn: (values: FormValues) =>
      onSubmit({
        returnDate: new Date(values.returnDate).toISOString(),
        amount: values.amount,
        bankAccountId: values.bankAccountId,
      }),
    onSuccess: () => router.push(cancelHref),
  });

  const handleSubmit = form.handleSubmit((values) => {
    if (Number(values.amount) > Number(maxAmount)) {
      form.setError("amount", { message: `Maximum return is ${maxAmount}` });
      return;
    }
    mutation.mutate(values);
  });

  return (
    <DocumentWorkspace
      title={title}
      breadcrumb={breadcrumb}
      formId="advance-return-form"
      onSubmit={handleSubmit}
      isSaving={mutation.isPending}
      saveLabel={submitLabel}
      onCancel={() => router.push(cancelHref)}
      grandTotal={form.watch("amount") || "0"}
      grandTotalLabel="Return amount"
      error={
        mutation.error instanceof ApiError
          ? mutation.error.message
          : mutation.isError
            ? "Could not process advance return"
            : null
      }
      summaryLines={[{ label: "Max return", value: maxAmount, emphasis: true }]}
      header={
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <FormField label="Return date" required error={form.formState.errors.returnDate?.message}>
            <Input type="date" {...form.register("returnDate")} />
          </FormField>
          <FormField
            label="Amount"
            required
            error={form.formState.errors.amount?.message}
          >
            <p className="mb-1 text-xs text-fg-muted">Unallocated advance: {maxAmount}</p>
            <Input inputMode="decimal" {...form.register("amount")} />
          </FormField>
          <FormField label="Bank account" required error={form.formState.errors.bankAccountId?.message}>
            <Select {...form.register("bankAccountId")}>
              <option value="">Select bank…</option>
              {(banksQuery.data?.result ?? []).map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </Select>
          </FormField>
        </div>
      }
    >
      <p className="text-sm text-fg-muted">
        This posts a bank movement to return unallocated advance to the party.
      </p>
    </DocumentWorkspace>
  );
}
