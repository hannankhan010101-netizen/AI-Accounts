"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import Decimal from "decimal.js";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { ListToolbar } from "@/components/ui/list-toolbar";
import { useClientList } from "@/lib/hooks/use-client-list";
import { matchText } from "@/lib/list/document-list-filters";
import type { BankReconciliationItem, BankReconciliationSession } from "@/lib/api/tenant";
import { cn } from "@/lib/utils";
import { brandSoftClasses } from "@/lib/design-tokens/brand-surfaces";

function dec(v: string): Decimal {
  try {
    return new Decimal(v);
  } catch {
    return new Decimal(0);
  }
}

function reconciliationItemHref(item: BankReconciliationItem): string | null {
  switch (item.itemType) {
    case "bank_payment":
      return `/bank/payments/${item.itemId}`;
    case "bank_receipt":
      return `/bank/receipts/${item.itemId}`;
    case "bank_transfer":
      return `/bank/transfers/${item.itemId}`;
    default:
      return null;
  }
}

function reconciliationItemTypeLabel(itemType: string): string {
  switch (itemType) {
    case "statement_line":
      return "Statement line";
    case "bank_payment":
      return "Bank payment";
    case "bank_receipt":
      return "Bank receipt";
    case "bank_transfer":
      return "Bank transfer";
    default:
      return itemType.replace(/_/g, " ");
  }
}

interface BankReconciliationWorkspaceProps {
  session: BankReconciliationSession;
  isOpen: boolean;
  onToggleCleared: (itemIds: string[], cleared: boolean) => void;
  isUpdating?: boolean;
}

export function BankReconciliationWorkspace({
  session,
  isOpen,
  onToggleCleared,
  isUpdating,
}: BankReconciliationWorkspaceProps) {
  const [filter, setFilter] = useState<"all" | "uncleared" | "cleared">("all");
  const items = session.items ?? [];

  const filtered = useMemo(() => {
    if (filter === "cleared") return items.filter((i) => i.isCleared);
    if (filter === "uncleared") return items.filter((i) => !i.isCleared);
    return items;
  }, [items, filter]);

  const clearedTotal = useMemo(
    () =>
      items
        .filter((i) => i.isCleared)
        .reduce((acc, i) => acc.plus(dec(String(i.amount))), new Decimal(0)),
    [items],
  );
  const statementBalance = dec(String(session.statementBalance));
  const difference = statementBalance.minus(clearedTotal);

  const unclearedCount = items.filter((i) => !i.isCleared).length;

  const { search, setSearch, pageRows, pagination } = useClientList({
    rows: filtered,
    filterFn: (i, q) => matchText([i.itemType, i.reference, i.amount, i.itemId], q),
  });

  const columns = useMemo((): GridColumn<BankReconciliationItem>[] => {
    const cols: GridColumn<BankReconciliationItem>[] = [];
    if (isOpen) {
      cols.push({
        key: "clear",
        header: "",
        render: (item) => (
          <Checkbox
            checked={item.isCleared}
            disabled={isUpdating}
            aria-label={`Clear ${item.reference ?? item.itemType}`}
            onChange={(e) => onToggleCleared([item.id], e.target.checked)}
          />
        ),
      });
    }
    cols.push(
      {
        key: "transactionDate",
        header: "Date",
        sortable: true,
        sortAccessor: (i) => i.transactionDate,
        render: (i) => new Date(i.transactionDate).toLocaleDateString(),
      },
      {
        key: "itemType",
        header: "Type",
        sortable: true,
        sortAccessor: (i) => i.itemType,
        render: (i) => reconciliationItemTypeLabel(i.itemType),
      },
      {
        key: "reference",
        header: "Reference",
        sortable: true,
        sortAccessor: (i) => i.reference ?? "",
        render: (i) => {
          const href = reconciliationItemHref(i);
          const label = i.reference ?? "—";
          if (!href) return label;
          return (
            <Link href={href} className="text-brand hover:underline">
              {label}
            </Link>
          );
        },
      },
      {
        key: "amount",
        header: "Amount",
        align: "right",
        sortable: true,
        sortAccessor: (i) => Number(i.amount),
        render: (i) => String(i.amount),
      },
    );
    return responsiveListColumns(cols, {
      primaryKey: "reference",
      hideBelowMdKeys: ["clear", "itemType", "transactionDate"],
    });
  }, [isOpen, isUpdating, onToggleCleared]);

  return (
    <div className="space-y-4">
      <div className="grid gap-3 sm:grid-cols-4">
        <StatCard label="Statement balance" value={statementBalance.toFixed(2)} />
        <StatCard label="Cleared total" value={clearedTotal.toFixed(2)} />
        <StatCard
          label="Difference"
          value={difference.toFixed(2)}
          tone={difference.abs().lt(0.01) ? "ok" : "warn"}
        />
        <StatCard label="Uncleared items" value={String(unclearedCount)} />
      </div>

      <div className="flex flex-wrap items-center gap-2">
        {(["all", "uncleared", "cleared"] as const).map((f) => (
          <button
            key={f}
            type="button"
            onClick={() => setFilter(f)}
            className={cn(
              "rounded-md px-3 py-1 text-xs font-medium capitalize",
              filter === f ? brandSoftClasses : "bg-canvas text-fg-muted hover:bg-border/40",
            )}
          >
            {f}
          </button>
        ))}
        {isOpen && unclearedCount > 0 && (
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={isUpdating}
            onClick={() =>
              onToggleCleared(
                items.filter((i) => !i.isCleared).map((i) => i.id),
                true,
              )
            }
          >
            Mark all visible uncleared as cleared
          </Button>
        )}
      </div>

      <ListToolbar search={search} onSearchChange={setSearch} searchPlaceholder="Search lines…" />
      <EnterpriseGrid<BankReconciliationItem>
        columns={columns}
        rows={pageRows}
        emptyMessage="No items for this filter."
        pagination={pagination}
        getRowId={(i) => i.id}
        rowClassName={(i) => (i.isCleared ? "bg-status-success/10" : undefined)}
      />
    </div>
  );
}

function StatCard({
  label,
  value,
  tone = "neutral",
}: {
  label: string;
  value: string;
  tone?: "neutral" | "ok" | "warn";
}) {
  return (
    <div className="rounded-lg border border-border bg-surface px-3 py-2">
      <div className="text-xs text-fg-muted">{label}</div>
      <div
        className={cn(
          "mt-0.5 text-lg font-semibold tabular-nums",
          tone === "ok" && "text-status-success",
          tone === "warn" && "text-status-warning",
        )}
      >
        {value}
      </div>
    </div>
  );
}

