/** New bank / cash account — catalog §4.1. */
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
import { bankApi, type CreateBankAccountInput } from "@/lib/api/tenant";
import { ApiError } from "@/lib/api/client";

const schema = z.object({
  name: z.string().min(1, "Required"),
  nominalCode: z.string().optional(),
  currency: z.string().length(3, "ISO 4217 three letters").default("PKR"),
});
type FormValues = z.infer<typeof schema>;

export default function NewBankAccountPage() {
  const router = useRouter();
  const [submitError, setSubmitError] = useState<string | null>(null);

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { name: "", nominalCode: "", currency: "PKR" },
  });

  const mutation = useMutation({
    mutationFn: (input: CreateBankAccountInput) => bankApi.createAccount(input),
    onSuccess: () => router.push("/bank/balances"),
    onError: (err) =>
      setSubmitError(err instanceof ApiError ? err.message : "Could not create account"),
  });

  return (
    <div>
      <PageHeader
        title="Add bank account"
        breadcrumb="Home / Bank / Account Balances / Add"
        description="Cash, bank, or credit-card-style ledger (§4.1). Opening balance posting wires up in Phase 3.1."
        actions={
          <>
            <Button type="button" variant="outline" onClick={() => router.back()}>
              Cancel
            </Button>
            <Button type="submit" form="ba-form" disabled={mutation.isPending}>
              {mutation.isPending ? "Saving…" : "Save and close"}
            </Button>
          </>
        }
      />
      <form
        id="ba-form"
        onSubmit={form.handleSubmit((v) =>
          mutation.mutate({
            name: v.name,
            nominalCode: v.nominalCode || null,
            currency: v.currency.toUpperCase(),
          }),
        )}
        className="max-w-2xl space-y-4 rounded-lg border border-border bg-surface p-6"
      >
        <FormField label="Name" required error={form.formState.errors.name?.message}>
          <Input {...form.register("name")} />
        </FormField>
        <FormField label="Nominal code (optional)">
          <Input {...form.register("nominalCode")} />
        </FormField>
        <FormField label="Currency" required error={form.formState.errors.currency?.message}>
          <Input maxLength={3} {...form.register("currency")} />
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
