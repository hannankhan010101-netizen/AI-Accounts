/** Online payments — PayPro & Kuickpay initiate (P7). */
"use client";

import { useMutation } from "@tanstack/react-query";
import { useTenantListQuery, useTenantReferenceQuery } from "@/lib/api/tenant-query";
import { useState } from "react";

import { IntegrationReadinessBanner } from "@/components/settings/integration-readiness-banner";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { Select } from "@/components/ui/select";
import { bankApi, partiesApi, paymentsApi } from "@/lib/api/tenant";
export default function OnlinePaymentsPage() {
  const [provider, setProvider] = useState<"paypro" | "kuickpay">("paypro");
  const [customerId, setCustomerId] = useState("");
  const [bankAccountId, setBankAccountId] = useState("");
  const [amount, setAmount] = useState("");

  const { data: customers } = useTenantReferenceQuery(["customers"], () => partiesApi.listCustomers());
  const { data: banks } = useTenantReferenceQuery(["bank-accounts"], () => bankApi.listAccounts());
  const { data: payproTx } = useTenantListQuery(["paypro-tx"], () => paymentsApi.listPaypro());
  const { data: kuickpayTx } = useTenantListQuery(["kuickpay-tx"], () => paymentsApi.listKuickpay());

  const initiate = useMutation({
    mutationFn: async () => {
      const body = {
        customerId,
        amount,
        bankAccountId: bankAccountId || undefined,
      };
      return provider === "paypro"
        ? paymentsApi.initiatePaypro(body)
        : paymentsApi.initiateKuickpay(body);
    },
  });

  const checkoutUrl = (initiate.data?.result as { checkoutUrl?: string } | undefined)?.checkoutUrl;
  const transactions =
    provider === "paypro" ? payproTx?.result ?? [] : kuickpayTx?.result ?? [];

  return (
    <div>
      <PageHeader
        title="Online payments"
        breadcrumb="Settings / Online payments"
      />
      <IntegrationReadinessBanner />
      <div className="grid max-w-xl gap-4 rounded-lg border border-border bg-surface p-4">
        <label className="text-sm">
          <span className="font-medium text-fg">Provider</span>
          <Select
            className="mt-1 w-full"
            value={provider}
            onChange={(e) => setProvider(e.target.value as "paypro" | "kuickpay")}
          >
            <option value="paypro">PayPro</option>
            <option value="kuickpay">Kuickpay</option>
          </Select>
        </label>
        <label className="text-sm">
          <span className="font-medium text-fg">Customer</span>
          <Select
            className="mt-1 w-full"
            value={customerId}
            onChange={(e) => setCustomerId(e.target.value)}
          >
            <option value="">Select customer</option>
            {(customers?.result ?? []).map((c) => (
              <option key={c.id} value={c.id}>
                {c.code ? `${c.code} — ` : ""}
                {c.name}
              </option>
            ))}
          </Select>
        </label>
        <label className="text-sm">
          <span className="font-medium text-fg">Bank account (settlement)</span>
          <Select
            className="mt-1 w-full"
            value={bankAccountId}
            onChange={(e) => setBankAccountId(e.target.value)}
          >
            <option value="">Default from Smart Settings</option>
            {(banks?.result ?? []).map((b) => (
              <option key={b.id} value={b.id}>
                {b.name}
              </option>
            ))}
          </Select>
        </label>
        <label className="text-sm">
          <span className="font-medium text-fg">Amount</span>
          <input
            type="text"
            className="mt-1 w-full rounded-md border border-border px-3 py-2"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="0.00"
          />
        </label>
        <Button
          type="button"
          disabled={!customerId || !amount || initiate.isPending}
          onClick={() => initiate.mutate()}
        >
          {initiate.isPending ? "Starting…" : "Initiate checkout"}
        </Button>
        {checkoutUrl ? (
          <p className="text-sm text-brand-700 dark:text-brand-300">
            Checkout:{" "}
            <a href={checkoutUrl} target="_blank" rel="noreferrer" className="underline">
              {checkoutUrl}
            </a>
          </p>
        ) : null}
        {initiate.isError ? (
          <p className="text-sm text-status-danger">
            {initiate.error instanceof Error ? initiate.error.message : "Failed"}
          </p>
        ) : null}
      </div>

      <section className="mt-8">
        <h2 className="mb-2 text-sm font-semibold text-fg">Recent transactions</h2>
        <ul className="divide-y rounded-lg border border-border bg-surface text-sm">
          {transactions.length === 0 ? (
            <li className="px-3 py-2 text-fg-muted">No transactions yet.</li>
          ) : (
            transactions.map((tx) => {
              const row = tx as {
                id?: string;
                merchantRef?: string;
                status?: string;
                amount?: string;
              };
              return (
                <li key={row.id ?? row.merchantRef} className="flex justify-between px-3 py-2">
                  <span>{row.merchantRef ?? row.id}</span>
                  <span className="text-fg-muted">
                    {row.status} · {row.amount}
                  </span>
                </li>
              );
            })
          )}
        </ul>
      </section>
    </div>
  );
}
