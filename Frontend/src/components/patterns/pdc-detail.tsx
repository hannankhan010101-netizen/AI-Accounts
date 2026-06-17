"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { invalidateTenantQueries, useTenantDetailQuery, useTenantListQuery } from "@/lib/api/tenant-query";
import { useState } from "react";
import Decimal from "decimal.js";

import { StatusBadge } from "@/components/app/status-badge";
import { PrintLink } from "@/components/print/print-link";
import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { PageHeader } from "@/components/ui/page-header";
import { Select } from "@/components/ui/select";
import { bankApi, pdcApi, type PdcIssued, type PdcReceived, type PdcStatus } from "@/lib/api/tenant";

const STATUSES: PdcStatus[] = ["pending", "presented", "cleared", "bounced", "cancelled"];

function fmtMoney(v: string | number): string {
  try {
    return new Decimal(typeof v === "string" ? v : v.toString()).toFixed(2);
  } catch {
    return String(v);
  }
}

interface PdcDetailProps {
  mode: "received" | "issued";
  chequeId: string;
  listHref: string;
  breadcrumb: string;
  partyLabel: string;
  resolvePartyName: (partyId: string) => string;
  printHref?: string;
}

export function PdcDetail({
  mode,
  chequeId,
  listHref,
  breadcrumb,
  partyLabel,
  resolvePartyName,
  printHref,
}: PdcDetailProps) {
  const router = useRouter();
  const qc = useQueryClient();
  const [bankAccountId, setBankAccountId] = useState("");
  const [actionError, setActionError] = useState<string | null>(null);

  const queryKey = mode === "received" ? ["pdc-received", chequeId] : ["pdc-issued", chequeId];

  const { data, isLoading, error } = useTenantDetailQuery(
    queryKey,
    async () => {
      if (mode === "received") {
        return pdcApi.getReceived(chequeId) as Promise<{ result: PdcReceived | PdcIssued }>;
      }
      return pdcApi.getIssued(chequeId) as Promise<{ result: PdcReceived | PdcIssued }>;
    },
    { enabled: Boolean(chequeId) },
  );

  const { data: banks } = useTenantListQuery(["bank-accounts"], () => bankApi.listAccounts());

  const invalidate = () => {
    void invalidateTenantQueries(qc, ...queryKey);
    void invalidateTenantQueries(qc, mode === "received" ? "pdc-received" : "pdc-issued");
  };

  const statusMutation = useMutation({
    mutationFn: async (status: PdcStatus) => {
      if (mode === "received") {
        return pdcApi.setReceivedStatus(chequeId, status);
      }
      return pdcApi.setIssuedStatus(chequeId, status);
    },
    onSuccess: () => {
      setActionError(null);
      invalidate();
    },
    onError: (e: Error) => setActionError(e.message),
  });

  const presentMutation = useMutation({
    mutationFn: async () => {
      if (mode === "received") {
        return pdcApi.presentReceived(chequeId);
      }
      return pdcApi.presentIssued(chequeId);
    },
    onSuccess: () => {
      setActionError(null);
      invalidate();
    },
    onError: (e: Error) => setActionError(e.message),
  });

  const clearMutation = useMutation({
    mutationFn: () => {
      if (mode === "received") {
        const bankId = bankAccountId || banks?.result?.[0]?.id;
        if (!bankId) throw new Error("Select a bank account to clear into.");
        return pdcApi.clearReceived(chequeId, {
          bankAccountId: bankId,
          clearDate: new Date().toISOString(),
          autoFifo: true,
        });
      }
      return pdcApi.clearIssued(chequeId, {
        clearDate: new Date().toISOString(),
        autoFifo: true,
      });
    },
    onSuccess: () => {
      setActionError(null);
      invalidate();
    },
    onError: (e: Error) => setActionError(e.message),
  });

  const bounceMutation = useMutation({
    mutationFn: async () => {
      if (mode === "received") return pdcApi.bounceReceived(chequeId);
      return pdcApi.bounceIssued(chequeId);
    },
    onSuccess: () => {
      setActionError(null);
      invalidate();
    },
    onError: (e: Error) => setActionError(e.message),
  });

  if (isLoading) return <div className="text-sm text-fg-muted">Loading…</div>;
  if (error instanceof Error)
    return (
      <div className="rounded-md border border-status-danger/30 bg-status-danger/10 p-3 text-sm text-status-danger">
        {error.message}
      </div>
    );

  const row = data?.result;
  if (!row) return null;

  const received = mode === "received" ? (row as PdcReceived) : null;
  const issued = mode === "issued" ? (row as PdcIssued) : null;
  const partyId = received?.customerId ?? issued?.supplierId ?? "";
  const canPresent = row.status === "pending";
  const canClear = row.status === "pending" || row.status === "presented";
  const canBounce = canClear;
  const linkedId =
    received?.linkedReceiptId ?? issued?.linkedPaymentId ?? null;

  return (
    <div>
      <PageHeader
        title={`${mode === "received" ? "PDC Received" : "PDC Issued"} ${row.voucherNumber}`}
        breadcrumb={breadcrumb}
        actions={
          <div className="flex gap-2">
            {printHref ? <PrintLink href={printHref} /> : null}
            <Button type="button" variant="outline" onClick={() => router.push(listHref)}>
              Back
            </Button>
          </div>
        }
      />

      {actionError ? (
        <div className="mb-4 rounded-md border border-status-danger/30 bg-status-danger/10 p-3 text-sm text-status-danger">
          {actionError}
        </div>
      ) : null}

      <section className="mb-4 grid grid-cols-1 gap-4 rounded-lg border border-border bg-surface p-4 md:grid-cols-3">
        <Field label="Voucher" value={row.voucherNumber} />
        <Field label="Cheque no." value={row.chequeNumber} />
        <Field label="Amount" value={fmtMoney(row.amount)} />
        <Field label={partyLabel} value={resolvePartyName(partyId)} />
        <Field
          label={mode === "received" ? "Received date" : "Issued date"}
          value={new Date(
            (received?.receivedDate ?? issued?.issuedDate) as string,
          ).toLocaleDateString()}
        />
        <Field
          label="Cheque date"
          value={new Date(row.chequeDate).toLocaleDateString()}
        />
        {mode === "received" ? (
          <Field label="Drawer bank" value={received?.bankName ?? "—"} />
        ) : (
          <Field
            label="Bank account"
            value={
              banks?.result.find((b) => b.id === issued?.bankAccountId)?.name ??
              issued?.bankAccountId ??
              "—"
            }
          />
        )}
        <div>
          <div className="text-xs font-medium uppercase tracking-wide text-fg-muted">Status</div>
          <div className="mt-1 flex flex-wrap items-center gap-2">
            <StatusBadge status={row.status} />
            <Select
              className="h-8 max-w-[10rem]"
              value={row.status}
              onChange={(e) => statusMutation.mutate(e.target.value as PdcStatus)}
            >
              {STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </Select>
          </div>
        </div>
        {linkedId ? (
          <div>
            <div className="text-xs font-medium uppercase tracking-wide text-fg-muted">
              Linked settlement
            </div>
            <div className="mt-1">
              <Link
                href={
                  mode === "received"
                    ? `/sales/receipts/${linkedId}`
                    : `/purchases/payments/${linkedId}`
                }
                className="text-sm text-brand hover:underline"
              >
                View {mode === "received" ? "receipt" : "payment"}
              </Link>
            </div>
          </div>
        ) : null}
        {row.notes ? <Field label="Notes" value={String(row.notes)} /> : null}
      </section>

      <section className="rounded-lg border border-border bg-surface p-4">
        <h2 className="text-sm font-semibold text-fg">Lifecycle actions</h2>
        <p className="mt-1 text-sm text-fg-muted">
          Present when deposited; clear to post a {mode === "received" ? "receipt" : "payment"} and
          allocate FIFO to open documents.
        </p>
        <div className="mt-4 flex flex-wrap items-end gap-3">
          {canPresent ? (
            <Button
              type="button"
              variant="outline"
              disabled={presentMutation.isPending}
              onClick={() => presentMutation.mutate()}
            >
              {presentMutation.isPending ? "Presenting…" : "Mark presented"}
            </Button>
          ) : null}
          {canClear && mode === "received" ? (
            <FormField label="Clear to bank account">
              <Select
                value={bankAccountId || (banks?.result?.[0]?.id ?? "")}
                onChange={(e) => setBankAccountId(e.target.value)}
              >
                {(banks?.result ?? []).map((b) => (
                  <option key={b.id} value={b.id}>
                    {b.name}
                  </option>
                ))}
              </Select>
            </FormField>
          ) : null}
          {canClear ? (
            <Button
              type="button"
              disabled={clearMutation.isPending}
              onClick={() => clearMutation.mutate()}
            >
              {clearMutation.isPending ? "Clearing…" : "Clear & post settlement"}
            </Button>
          ) : null}
          {canBounce && row.status !== "bounced" && row.status !== "cancelled" ? (
            <Button
              type="button"
              variant="outline"
              disabled={bounceMutation.isPending}
              onClick={() => bounceMutation.mutate()}
            >
              Mark bounced
            </Button>
          ) : null}
        </div>
      </section>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-xs font-medium uppercase tracking-wide text-fg-muted">{label}</div>
      <div className="mt-1 text-sm font-medium text-fg">{value}</div>
    </div>
  );
}
