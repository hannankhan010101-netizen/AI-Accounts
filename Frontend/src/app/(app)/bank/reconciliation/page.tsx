/** Bank reconciliation — P1 (catalog §4.5). */
"use client";
import { useTenantListQuery, invalidateTenantQueries } from "@/lib/api/tenant-query";


import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { buildGridExport } from "@/lib/export/grid-export";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { ListToolbar } from "@/components/ui/list-toolbar";
import { PageHeader } from "@/components/ui/page-header";
import { Select } from "@/components/ui/select";
import { useClientList } from "@/lib/hooks/use-client-list";
import { useBankAccountNameMap } from "@/lib/hooks/use-bank-account-name-map";
import { matchText } from "@/lib/list/document-list-filters";
import { bankApi, type BankReconciliationSession } from "@/lib/api/tenant";
import { DemoSandboxBanner } from "@/components/onboarding/demo-sandbox-banner";
import { useTourDemoSandbox } from "@/features/onboarding/hooks/use-tour-ghost-fill";
import { useTourGhostDomFill } from "@/features/onboarding/hooks/use-tour-ghost-dom-fill";

export default function BankReconciliationPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const bankNames = useBankAccountNameMap();
  const [bankAccountId, setBankAccountId] = useState("");
  const [statementBalance, setStatementBalance] = useState("");
  const [statementDate, setStatementDate] = useState(
    () => new Date().toISOString().slice(0, 10),
  );

  const { data: accounts } = useTenantListQuery(["bank-accounts"], () => bankApi.listAccounts());

  const { data: sessions, isLoading, error } = useTenantListQuery(
    ["bank-reconciliations", bankAccountId],
    () => bankApi.listReconciliations(bankAccountId ? { bankAccountId } : undefined),
  );

  const start = useMutation({
    mutationFn: () =>
      bankApi.startReconciliation({
        bankAccountId,
        statementDate: new Date(statementDate).toISOString(),
        statementBalance,
      }),
    onSuccess: (res) => {
      void invalidateTenantQueries(queryClient, "bank-reconciliations");
      const id = res.result?.id;
      if (id) router.push(`/bank/reconciliation/${id}`);
    },
  });

  const accountList = accounts?.result ?? [];
  const demoSandbox = useTourDemoSandbox();
  const bankAccountIds = useMemo(() => accountList.map((a) => a.id), [accountList]);

  const { filling: ghostFilling } = useTourGhostDomFill({
    setters: {
      bankAccountId: setBankAccountId,
      statementDate: setStatementDate,
      statementBalance: setStatementBalance,
    },
    context: {
      customerIds: [],
      supplierIds: [],
      bankAccountIds,
      productCodes: [],
    },
    highlightSelectors: {
      bankAccountId: "[data-tour='bank-recon-account']",
      statementDate: "[data-tour='bank-recon-date']",
      statementBalance: "[data-tour='bank-recon-balance']",
    },
  });
  const allSessions = sessions?.result ?? [];

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows: allSessions,
    syncUrl: true,
    filterFn: (s, q) =>
      matchText(
        [
          s.status,
          bankNames.get(s.bankAccountId),
          s.bankAccountId,
          s.statementBalance,
        ],
        q,
      ),
  });

  const columns = useMemo(
    () => responsiveListColumns<BankReconciliationSession>([
      {
        key: "statementDate",
        header: "Statement date",
        sortable: true,
        sortAccessor: (s) => s.statementDate,
        render: (s) => new Date(s.statementDate).toLocaleDateString(),
      },
      {
        key: "bankAccountId",
        header: "Bank account",
        sortable: true,
        sortAccessor: (s) => bankNames.get(s.bankAccountId) ?? s.bankAccountId,
        render: (s) => bankNames.get(s.bankAccountId) ?? s.bankAccountId,
      },
      { key: "status", header: "Status", sortable: true, sortAccessor: (s) => s.status },
      {
        key: "statementBalance",
        header: "Statement balance",
        align: "right",
        sortable: true,
        sortAccessor: (s) => Number(s.statementBalance),
        render: (s) => String(s.statementBalance),
      },
      {
        key: "items",
        header: "Items",
        align: "right",
        sortAccessor: (s) => s.items?.length ?? 0,
        render: (s) => String(s.items?.length ?? 0),
      },
    ]),
    [bankNames],
  );

  return (
    <div>
      {demoSandbox && <DemoSandboxBanner filling={ghostFilling} />}
      <PageHeader
        title="Bank reconciliation"
        breadcrumb="Money / Reconciliation"
        description="Start a session from a statement date and balance, then match bank lines."
        tourRoot="bank-reconciliation-header"
        actions={
          <div className="flex flex-wrap gap-2">
            <Link href="/bank/import-statement">
              <Button variant="outline">Import statement</Button>
            </Link>
          </div>
        }
      />

      <section
        className="mb-6 grid gap-4 rounded-lg border border-border bg-surface p-4 md:grid-cols-4"
        data-tour="bank-recon-start"
      >
        <FormField label="Bank account">
          <Select
            data-tour="bank-recon-account"
            value={bankAccountId}
            onChange={(e) => setBankAccountId(e.target.value)}
          >
            <option value="">All sessions / pick to start</option>
            {accountList.map((a) => (
              <option key={a.id} value={a.id}>
                {String(a.name)}
                {a.code ? ` (${String(a.code)})` : ""}
              </option>
            ))}
          </Select>
        </FormField>
        <FormField label="Statement date">
          <Input
            data-tour="bank-recon-date"
            type="date"
            value={statementDate}
            onChange={(e) => setStatementDate(e.target.value)}
          />
        </FormField>
        <FormField label="Statement balance">
          <Input
            data-tour="bank-recon-balance"
            value={statementBalance}
            onChange={(e) => setStatementBalance(e.target.value)}
            placeholder="0.00"
          />
        </FormField>
        <div className="flex items-end">
          <Button
            type="button"
            disabled={
              demoSandbox ||
              !bankAccountId ||
              !statementBalance ||
              start.isPending
            }
            onClick={() => {
              if (demoSandbox) return;
              start.mutate();
            }}
            title={demoSandbox ? "Disabled during interactive demo" : undefined}
          >
            {start.isPending ? "Starting…" : "Start reconciliation"}
          </Button>
        </div>
      </section>

      {start.isError ? (
        <p className="mb-4 text-sm text-status-danger">
          {start.error instanceof Error ? start.error.message : "Failed to start"}
        </p>
      ) : null}

      <ListToolbar search={search} onSearchChange={setSearch} searchPlaceholder="Search sessions…" />
      <EnterpriseGrid<BankReconciliationSession>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        error={error}
        emptyMessage="No reconciliation sessions yet."
        pagination={pagination}
        exportCsv={{ ...buildGridExport("bank-reconciliation", columns), rows: filtered }}
        getRowId={(s) => s.id}
        onRowClick={(s) => router.push(`/bank/reconciliation/${s.id}`)}
      />
    </div>
  );
}
