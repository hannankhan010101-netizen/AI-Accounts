/**
 * Journal voucher create — catalog §9.2 / Phase 2.2.
 * Debit/credit grid with balance enforcement before POST /journals.
 */
"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { useFieldArray, useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import Decimal from "decimal.js";
import { Button } from "@/components/ui/button";
import { DocumentWorkspace } from "@/components/patterns/document-workspace";
import { JournalLinesEditor } from "@/components/patterns/journal-lines-editor";
import { TransactionTemplatePicker } from "@/components/patterns/transaction-template-picker";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { journalsApi, type JournalCreateInput } from "@/lib/api/tenant";
import { ApiError } from "@/lib/api/client";
import { useCompany } from "@/lib/auth/company-context";
import { useDocumentWorkspaceDraft } from "@/lib/hooks/use-document-workspace-draft";

const amountSchema = z
  .string()
  .regex(/^-?\d+(\.\d+)?$/u, "Numeric amount required")
  .or(z.literal(""));

const lineSchema = z.object({
  nominalCode: z.string().min(1, "Required"),
  debit: amountSchema,
  credit: amountSchema,
  projectCode: z.string().optional(),
});

const schema = z.object({
  journalDate: z.string().min(1, "Required"),
  refNo: z.string().optional(),
  lines: z.array(lineSchema).min(2, "At least two lines"),
});
type FormValues = z.infer<typeof schema>;

function emptyLine() {
  return { nominalCode: "", debit: "", credit: "", projectCode: "" };
}

function toDecimal(value: string): Decimal {
  if (!value) return new Decimal(0);
  try {
    return new Decimal(value);
  } catch {
    return new Decimal(0);
  }
}

export default function NewJournalPage() {
  const router = useRouter();
  const { companyId } = useCompany();
  const [submitError, setSubmitError] = useState<string | null>(null);

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      journalDate: new Date().toISOString().slice(0, 10),
      refNo: "",
      lines: [emptyLine(), emptyLine()],
    },
  });

  const lines = useFieldArray({ control: form.control, name: "lines" });
  const watched = form.watch();
  const watchedLines = watched.lines ?? [];

  const { topBanner, clearDraftOnSuccess } = useDocumentWorkspaceDraft({
    scope: "journal-new",
    companyId,
    form,
    values: watched,
    shouldPersist: (v) =>
      Boolean(v.refNo?.trim()) ||
      Boolean(v.lines?.some((l) => l.nominalCode || l.debit || l.credit)),
  });

  const totals = useMemo(() => {
    const debit = watchedLines.reduce((acc, l) => acc.plus(toDecimal(l.debit)), new Decimal(0));
    const credit = watchedLines.reduce((acc, l) => acc.plus(toDecimal(l.credit)), new Decimal(0));
    return { debit, credit, diff: debit.minus(credit) };
  }, [watchedLines]);

  const balanced = totals.diff.isZero() && totals.debit.gt(0);

  const mutation = useMutation({
    mutationFn: (input: JournalCreateInput) => journalsApi.create(input),
    onSuccess: (res) => {
      clearDraftOnSuccess();
      const id = res?.result?.id;
      if (id) router.push(`/settings/journals/${id}`);
      else router.push("/settings/journals");
    },
    onError: (err) =>
      setSubmitError(err instanceof ApiError ? err.message : "Could not create journal"),
  });

  const onSubmit = form.handleSubmit((values) => {
    setSubmitError(null);
    if (!balanced) {
      setSubmitError("Debit and credit totals must match and be greater than zero.");
      return;
    }
    mutation.mutate({
      journalDate: new Date(values.journalDate).toISOString(),
      refNo: values.refNo || null,
      lines: values.lines.map((l) => ({
        nominalCode: l.nominalCode,
        debit: l.debit || "0",
        credit: l.credit || "0",
        projectCode: l.projectCode || null,
      })),
    });
  });

  const loadTemplate = (payload: Record<string, unknown>) => {
    if (typeof payload.journalDate === "string") form.setValue("journalDate", payload.journalDate);
    if (typeof payload.refNo === "string") form.setValue("refNo", payload.refNo);
    if (Array.isArray(payload.lines) && payload.lines.length >= 2) {
      form.setValue("lines", payload.lines as FormValues["lines"]);
    }
  };

  return (
    <DocumentWorkspace
      title="New journal"
      breadcrumb="Accounting / Journals / New"
      tourRoot="journal-new-header"
      tourSummary="journal-new-summary"
      tourSave="journal-new-save"
      formId="journal-form"
      onSubmit={onSubmit}
      isSaving={mutation.isPending}
      saveLabel={balanced ? "Post journal" : "Unbalanced"}
      onCancel={() => router.push("/settings/journals")}
      grandTotal={totals.debit.toFixed(2)}
      grandTotalLabel="Total debit"
      error={submitError}
      topBanner={topBanner}
      summaryLines={[
        { label: "Debit", value: totals.debit.toFixed(2), emphasis: true },
        { label: "Credit", value: totals.credit.toFixed(2) },
        {
          label: "Difference",
          value: `${totals.diff.toFixed(2)} ${totals.diff.isZero() ? "✓ balanced" : "✗ out of balance"}`,
          emphasis: !totals.diff.isZero(),
        },
        { label: "Lines", value: String(watchedLines.length) },
      ]}
      header={
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2" data-tour="journal-new-header">
          <FormField label="Journal date" required error={form.formState.errors.journalDate?.message}>
            <Input type="date" {...form.register("journalDate")} />
          </FormField>
          <FormField label="Reference">
            <Input {...form.register("refNo")} placeholder="Optional" />
          </FormField>
        </div>
      }
    >
      <TransactionTemplatePicker
        module="journal"
        onLoad={loadTemplate}
        onCapturePayload={() => ({
          journalDate: form.getValues("journalDate"),
          refNo: form.getValues("refNo"),
          lines: form.getValues("lines"),
        })}
      />
      <JournalLinesEditor
        form={form}
        lines={lines}
        emptyLine={emptyLine}
        tourTarget="journal-new-lines"
      />
      <div className="mt-4 flex justify-end">
        <Button
          type="button"
          variant="outline"
          disabled={!balanced || mutation.isPending}
          onClick={() => {
            if (!balanced) return;
            const values = form.getValues();
            mutation.mutate({
              journalDate: new Date(values.journalDate).toISOString(),
              refNo: values.refNo || null,
              status: "draft",
              lines: values.lines.map((l) => ({
                nominalCode: l.nominalCode,
                debit: l.debit || "0",
                credit: l.credit || "0",
                projectCode: l.projectCode || null,
              })),
            });
          }}
        >
          Save as draft
        </Button>
      </div>
    </DocumentWorkspace>
  );
}
