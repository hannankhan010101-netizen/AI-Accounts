"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import { useQuery } from "@tanstack/react-query";
import Decimal from "decimal.js";

import { Input } from "@/components/ui/input";
import { partiesApi, purchasesApi, salesApi } from "@/lib/api/tenant";

export interface AllocationRow {
  documentId: string;
  amount: string;
}

interface AllocationPickerProps {
  mode: "customer" | "supplier";
  partyId: string;
  receiptTotal: string;
  rows: AllocationRow[];
  onChange: (rows: AllocationRow[]) => void;
}

function dec(v: string): Decimal {
  try {
    return new Decimal(v || "0");
  } catch {
    return new Decimal(0);
  }
}

export function AllocationPicker({
  mode,
  partyId,
  receiptTotal,
  rows,
  onChange,
}: AllocationPickerProps) {
  const openQuery = useTenantListQuery([mode === "customer" ? "open-invoices" : "open-bills",
      partyId,], () =>
      mode === "customer"
        ? partiesApi.listOpenInvoices(partyId)
        : partiesApi.listOpenBills(partyId),
    { enabled: Boolean(partyId) });

  const open = openQuery.data?.result ?? [];
  const allocated = rows.reduce((acc, r) => acc.plus(dec(r.amount)), new Decimal(0));
  const total = dec(receiptTotal);

  const setAmount = (documentId: string, amount: string) => {
    const next = [...rows];
    const idx = next.findIndex((r) => r.documentId === documentId);
    if (amount === "" || dec(amount).lte(0)) {
      if (idx >= 0) next.splice(idx, 1);
    } else if (idx >= 0) {
      next[idx] = { documentId, amount };
    } else {
      next.push({ documentId, amount });
    }
    onChange(next);
  };

  const fillRemaining = (documentId: string, remaining: string) => {
    const left = total.minus(allocated);
    const cap = Decimal.min(dec(remaining), left);
    if (cap.gt(0)) setAmount(documentId, cap.toFixed(2));
  };

  if (!partyId) {
    return (
      <p className="text-xs text-fg-muted">Select a {mode === "customer" ? "customer" : "supplier"} first.</p>
    );
  }

  if (openQuery.isLoading) {
    return <p className="text-xs text-fg-muted">Loading open documents…</p>;
  }

  if (open.length === 0) {
    return (
      <p className="text-xs text-fg-muted">No open {mode === "customer" ? "invoices" : "bills"} to allocate.</p>
    );
  }

  return (
    <div className="space-y-2 rounded-md border border-border bg-canvas p-3">
      <div className="flex justify-between text-xs text-fg-muted">
        <span>Allocate to specific documents</span>
        <span className="tabular-nums">
          Allocated {allocated.toFixed(2)} / {total.toFixed(2)}
        </span>
      </div>
      <table className="min-w-full text-xs">
        <thead>
          <tr className="text-left text-fg-muted">
            <th className="py-1 pr-2">Document</th>
            <th className="py-1 pr-2 text-right">Remaining</th>
            <th className="py-1 pr-2 text-right">Allocate</th>
            <th className="py-1"></th>
          </tr>
        </thead>
        <tbody>
          {open.map((doc) => {
            const id = doc.id;
            const label =
              mode === "customer"
                ? (doc as { invoiceNumber?: string }).invoiceNumber ?? id
                : (doc as { billNumber?: string }).billNumber ?? id;
            const remaining = doc.remaining;
            const current = rows.find((r) => r.documentId === id)?.amount ?? "";
            return (
              <tr key={id} className="border-t border-border">
                <td className="py-1.5 pr-2 font-medium text-fg">{label}</td>
                <td className="py-1.5 pr-2 text-right tabular-nums">{remaining}</td>
                <td className="py-1.5 pr-2">
                  <Input
                    inputMode="decimal"
                    className="h-7 w-28 text-right tabular-nums"
                    value={current}
                    onChange={(e) => setAmount(id, e.target.value)}
                  />
                </td>
                <td className="py-1.5">
                  <button
                    type="button"
                    className="text-brand hover:underline"
                    onClick={() => fillRemaining(id, remaining)}
                  >
                    Fill
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
