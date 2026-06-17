/** Bank statement import — FastAccounts Import Statement (catalog §4.5a). */
"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { Select } from "@/components/ui/select";
import { bankApi } from "@/lib/api/tenant";

export default function ImportStatementPage() {
  const router = useRouter();
  const [bankAccountId, setBankAccountId] = useState("");
  const [statementDate, setStatementDate] = useState(
    () => new Date().toISOString().slice(0, 10),
  );
  const [statementBalance, setStatementBalance] = useState("");
  const [file, setFile] = useState<File | null>(null);

  const { data: accounts } = useTenantListQuery(["bank-accounts"], () => bankApi.listAccounts());

  const upload = useMutation({
    mutationFn: async () => {
      if (!file || !bankAccountId) throw new Error("Choose a bank account and statement file");
      const form = new FormData();
      form.append("bankAccountId", bankAccountId);
      form.append("statementDate", new Date(statementDate).toISOString());
      if (statementBalance.trim()) {
        form.append("statementBalance", statementBalance.trim());
      }
      form.append("file", file);
      return bankApi.importStatement(form);
    },
    onSuccess: (res) => {
      const id = res.result?.id;
      if (id) router.push(`/bank/reconciliation/${id}`);
    },
  });

  const accountList = accounts?.result ?? [];

  return (
    <div>
      <PageHeader
        title="Import statement"
        breadcrumb="Money / Import statement"
        description="Upload a CSV or Excel bank statement. A reconciliation session opens with ledger movements plus imported lines."
        actions={
          <Link href="/bank/reconciliation">
            <Button variant="outline">Reconciliation list</Button>
          </Link>
        }
      />

      <section className="max-w-xl space-y-4 rounded-lg border border-border bg-surface p-6">
        <FormField label="Bank account" required>
          <Select
            value={bankAccountId}
            onChange={(e) => setBankAccountId(e.target.value)}
            aria-label="Bank account"
          >
            <option value="">Select account…</option>
            {accountList.map((a) => (
              <option key={a.id} value={a.id}>
                {a.name}
              </option>
            ))}
          </Select>
        </FormField>

        <FormField label="Statement date" required>
          <Input
            type="date"
            value={statementDate}
            onChange={(e) => setStatementDate(e.target.value)}
          />
        </FormField>

        <FormField label="Closing balance">
          <p className="text-xs text-fg-muted">Optional — if blank, sum of imported amounts is used.</p>
          <Input
            type="text"
            inputMode="decimal"
            placeholder="e.g. 125000.00"
            value={statementBalance}
            onChange={(e) => setStatementBalance(e.target.value)}
          />
        </FormField>

        <FormField label="Statement file" required>
          <p className="text-xs text-fg-muted">
            CSV or Excel with columns such as Date, Amount, Description.
          </p>
          <Input
            type="file"
            accept=".csv,.xlsx,.xlsm"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
        </FormField>

        {upload.error instanceof Error && (
          <p className="text-sm text-status-danger">{upload.error.message}</p>
        )}

        <Button
          type="button"
          disabled={upload.isPending || !file || !bankAccountId}
          onClick={() => upload.mutate()}
        >
          {upload.isPending ? "Importing…" : "Import and reconcile"}
        </Button>
      </section>
    </div>
  );
}
