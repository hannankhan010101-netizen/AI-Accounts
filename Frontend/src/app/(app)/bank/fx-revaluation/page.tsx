"use client";
import { useTenantListQuery, invalidateTenantQueries, useTenantReferenceQuery } from "@/lib/api/tenant-query";


import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { Select } from "@/components/ui/select";
import { bankApi, fxRevaluationApi, type FxRevaluationRun } from "@/lib/api/tenant";


export default function FxRevaluationPage() {
  const qc = useQueryClient();
  const [bankAccountId, setBankAccountId] = useState("");
  const [revaluationDate, setRevaluationDate] = useState(
    new Date().toISOString().slice(0, 10),
  );
  const [foreignBalance, setForeignBalance] = useState("");
  const [exchangeRate, setExchangeRate] = useState("");
  const [bookBalanceBase, setBookBalanceBase] = useState("");

  const accounts = useTenantReferenceQuery(["bank-accounts"], () => bankApi.listAccounts());

  const history = useTenantListQuery(["fx-revaluations"], () => fxRevaluationApi.list());

  const run = useMutation({
    mutationFn: () =>
      fxRevaluationApi.create({
        bankAccountId,
        revaluationDate: new Date(revaluationDate).toISOString(),
        foreignBalance,
        exchangeRate,
        bookBalanceBase: bookBalanceBase || undefined,
      }),
    onSuccess: () => {
      void invalidateTenantQueries(qc, "fx-revaluations");
      setForeignBalance("");
      setExchangeRate("");
      setBookBalanceBase("");
    },
  });

  const columns: GridColumn<FxRevaluationRun>[] = [
    {
      key: "revaluationDate",
      header: "Date",
      render: (r) =>
        r.revaluationDate
          ? new Date(String(r.revaluationDate)).toLocaleDateString()
          : "—",
    },
    { key: "bankAccountId", header: "Bank account" },
    { key: "id", header: "Run ID", render: (r) => <span className="font-mono text-xs">{r.id}</span> },
  ];

  return (
    <div className="space-y-8">
      <PageHeader
        title="FX revaluation"
        breadcrumb="Money / FX revaluation"
        description="Revalue foreign-currency bank balances and post adjustment journals."
      />

      <section className="max-w-lg space-y-4 rounded-lg border border-border p-4">
        <h2 className="text-sm font-medium">Run revaluation</h2>
        <FormField label="Bank account">
          <Select value={bankAccountId} onChange={(e) => setBankAccountId(e.target.value)}>
            <option value="">Select account</option>
            {(accounts.data?.result ?? []).map((a) => (
              <option key={a.id} value={a.id}>
                {a.name} ({a.code})
              </option>
            ))}
          </Select>
        </FormField>
        <FormField label="Revaluation date">
          <Input
            type="date"
            value={revaluationDate}
            onChange={(e) => setRevaluationDate(e.target.value)}
          />
        </FormField>
        <FormField label="Foreign balance">
          <Input value={foreignBalance} onChange={(e) => setForeignBalance(e.target.value)} />
        </FormField>
        <FormField label="Exchange rate">
          <Input value={exchangeRate} onChange={(e) => setExchangeRate(e.target.value)} />
        </FormField>
        <FormField label="Book balance (base, optional)">
          <Input
            value={bookBalanceBase}
            onChange={(e) => setBookBalanceBase(e.target.value)}
          />
        </FormField>
        <Button
          onClick={() => run.mutate()}
          disabled={
            run.isPending || !bankAccountId || !foreignBalance || !exchangeRate
          }
        >
          Post revaluation
        </Button>
        {run.isError && (
          <p className="text-sm text-status-danger">{(run.error as Error).message}</p>
        )}
        {run.isSuccess && (
          <p className="text-sm text-status-ok">Revaluation posted.</p>
        )}
      </section>

      <section>
        <h2 className="mb-2 text-lg font-medium">History</h2>
        <EnterpriseGrid<FxRevaluationRun>
          columns={columns}
          rows={history.data?.result ?? []}
          loading={history.isLoading}
          error={history.error}
          emptyMessage="No FX revaluations yet."
          getRowId={(r) => r.id}
        />
      </section>
    </div>
  );
}
