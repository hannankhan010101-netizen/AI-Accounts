/** Edit draft journal — PATCH /journals/{id} then optional POST /post */
"use client";
import { invalidateTenantQueries, useTenantDetailQuery } from "@/lib/api/tenant-query";

import { useEffect, useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useFieldArray, useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import Decimal from "decimal.js";

import { DocumentWorkspace } from "@/components/patterns/document-workspace";
import { JournalLinesEditor } from "@/components/patterns/journal-lines-editor";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { DetailPageLoading } from "@/components/ui/detail-page-loading";
import { journalsApi, type JournalUpdateInput } from "@/lib/api/tenant";
import { ApiError } from "@/lib/api/client";


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

export default function EditJournalPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const id = typeof params.id === "string" ? params.id : "";
  const [submitError, setSubmitError] = useState<string | null>(null);

  const { data, isLoading } = useTenantDetailQuery(["journal", id], () => journalsApi.get(id), { enabled: Boolean(id) });

  const journal = data?.result;

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      journalDate: new Date().toISOString().slice(0, 10),
      refNo: "",
      lines: [emptyLine(), emptyLine()],
    },
  });

  useEffect(() => {
    if (!journal?.lines?.length) return;
    form.reset({
      journalDate: journal.journalDate.slice(0, 10),
      refNo: journal.refNo ?? "",
      lines: journal.lines.map((l) => ({
        nominalCode: l.nominalCode,
        debit: String(l.debit ?? "0"),
        credit: String(l.credit ?? "0"),
        projectCode: l.projectCode ?? "",
      })),
    });
  }, [journal, form]);

  const lines = useFieldArray({ control: form.control, name: "lines" });
  const watched = form.watch();
  const watchedLines = watched.lines ?? [];

  const totals = useMemo(() => {
    const debit = watchedLines.reduce((acc, l) => acc.plus(toDecimal(l.debit)), new Decimal(0));
    const credit = watchedLines.reduce((acc, l) => acc.plus(toDecimal(l.credit)), new Decimal(0));
    return { debit, credit, diff: debit.minus(credit) };
  }, [watchedLines]);

  const balanced = totals.diff.isZero() && totals.debit.gt(0);

  const saveMutation = useMutation({
    mutationFn: (input: JournalUpdateInput) => journalsApi.update(id, input),
    onSuccess: () => {
      void invalidateTenantQueries(queryClient, "journal", id);
      router.push(`/settings/journals/${id}`);
    },
    onError: (err) =>
      setSubmitError(err instanceof ApiError ? err.message : "Could not save journal"),
  });

  const postMutation = useMutation({
    mutationFn: () => journalsApi.post(id),
    onSuccess: () => {
      void invalidateTenantQueries(queryClient, "journal", id);
      void invalidateTenantQueries(queryClient, "journals");
      router.push(`/settings/journals/${id}`);
    },
    onError: (err) =>
      setSubmitError(err instanceof ApiError ? err.message : "Could not post journal"),
  });

  const onSubmit = form.handleSubmit((values) => {
    setSubmitError(null);
    if (!balanced) {
      setSubmitError("Debit and credit totals must match and be greater than zero.");
      return;
    }
    saveMutation.mutate({
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

  if (isLoading) return <DetailPageLoading />;
  if (!journal) return null;
  if (journal.status !== "draft") {
    return (
      <div className="p-6 text-sm text-fg-muted">
        Only draft journals can be edited.{" "}
        <button type="button" className="text-brand underline" onClick={() => router.back()}>
          Go back
        </button>
      </div>
    );
  }

  return (
    <DocumentWorkspace
      title={`Edit journal ${journal.journalNumber ?? id}`}
      breadcrumb="Accounting / Journals / Edit"
      formId="journal-edit-form"
      onSubmit={onSubmit}
      isSaving={saveMutation.isPending}
      saveLabel="Save draft"
      onCancel={() => router.push(`/settings/journals/${id}`)}
      grandTotal={totals.debit.toFixed(2)}
      grandTotalLabel="Total debit"
      error={submitError}
      summaryLines={[
        { label: "Debit", value: totals.debit.toFixed(2), emphasis: true },
        { label: "Credit", value: totals.credit.toFixed(2) },
        {
          label: "Difference",
          value: `${totals.diff.toFixed(2)} ${totals.diff.isZero() ? "✓" : "✗"}`,
          emphasis: !totals.diff.isZero(),
        },
      ]}
      header={
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <FormField label="Journal date" required error={form.formState.errors.journalDate?.message}>
            <Input type="date" {...form.register("journalDate")} />
          </FormField>
          <FormField label="Reference">
            <Input {...form.register("refNo")} placeholder="Optional" />
          </FormField>
        </div>
      }
    >
      <JournalLinesEditor form={form} lines={lines} emptyLine={emptyLine} />
      <div className="mt-4 flex justify-end">
        <Button
          type="button"
          disabled={!balanced || postMutation.isPending || saveMutation.isPending}
          onClick={() => {
            if (!balanced) return;
            void saveMutation
              .mutateAsync({
                journalDate: new Date(watched.journalDate).toISOString(),
                refNo: watched.refNo || null,
                lines: watchedLines.map((l) => ({
                  nominalCode: l.nominalCode,
                  debit: l.debit || "0",
                  credit: l.credit || "0",
                  projectCode: l.projectCode || null,
                })),
              })
              .then(() => postMutation.mutate());
          }}
        >
          {postMutation.isPending ? "Posting…" : "Save & post journal"}
        </Button>
      </div>
    </DocumentWorkspace>
  );
}
